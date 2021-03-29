from app.db.Models import Order, DeliveryHours
from app.db.Handlers.BaseHandler import BaseHandler


class OrderHandler(BaseHandler):

    def make_time_records(self, order_id, args: list):
        res = []
        for i in args:
            time1, time2 = self.unpack_time(i)
            if time1 and time2:
                res.append(DeliveryHours(start=time1, end=time2, order_id=order_id))
                self.logger.debug(f"DeliveryHours(start={time1}, end={time2}, order_id={order_id})")
            else:
                return None
        if res:
            return res
        return None

    def make_order_record(self, order_id, weight, region):
        if ((type(weight) is not float) and (type(weight) is not int)) or (weight < 0.01) or (weight > 50):
            return None
        if (type(region) is not int) or (region <= 0):
            return None
        if (type(order_id) is not int) or (order_id <= 0):
            return None
        order = Order(id=order_id, weight=weight, region=region)
        self.logger.debug(f"Order(id={order_id}, weight={weight}, region={region})")
        return order

    async def push(self, raw_data):
        orders = []
        hours = []
        errors = []
        ok = []
        if "data" in raw_data.keys():
            for i in raw_data["data"]:
                if "order_id" in i.keys():
                    if "weight" in i.keys() and "region" in i.keys() and "delivery_hours" in i.keys() \
                            and (len(i) == 4):
                        order = self.make_order_record(i["order_id"], i["weight"], i["region"])
                        order_hours = self.make_time_records(i['order_id'], i["delivery_hours"])
                        if order and order_hours:
                            orders.append(order)
                            hours.extend(order_hours)
                            ok.append({"id": i["order_id"]})
                        else:
                            self.logger.warning(f"wrong params")
                            errors.append({"id": i["order_id"]})
                    else:
                        self.logger.warning(f"wrong keys")
                        errors.append({"id": i["order_id"]})
                else:
                    self.logger.warning("no order id")
                    return {"error": []}
        else:
            self.logger.warning("no data field")
            return {"error": []}
        session = self.make_session()
        if not errors:
            if orders:
                for i in orders + hours:
                    session.add(i)
                session.commit()
                return {"orders": ok}
            else:
                session.rollback()
                self.logger.warning("no data")
                return {"error": []}
        else:
            session.rollback()
            return {"error": errors}


order_handler = OrderHandler()
