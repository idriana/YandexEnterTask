from app.db.Handlers.BaseHandler import BaseHandler
from app.db.Models import *
from aiohttp.web import HTTPBadRequest
import datetime


value_dict = {
    "foot": 2,
    "bike": 5,
    "car": 9
}

class OrderCompleteHandler(BaseHandler):

    def complete(self, raw_data):
        if ("courier_id" not in raw_data.keys()) or (type(raw_data["courier_id"]) is not int) \
                or (raw_data["courier_id"] <= 0):
            self.logger.warning(f"wrong courier id")
            raise HTTPBadRequest
        if ("order_id" not in raw_data.keys()) or (type(raw_data["order_id"]) is not int) \
                or (raw_data["order_id"] <= 0):
            self.logger.warning("wrong order id")
            raise HTTPBadRequest
        courier_id = raw_data["courier_id"]
        order_id = raw_data["order_id"]
        complete_time = raw_data["complete_time"]
        session = self.make_session()
        order = session.query(Order).filter(Order.courier_id == courier_id, Order.id == order_id).first()
        self.logger.debug(f"order = {order}")
        if not order:
            raise HTTPBadRequest
        region = session.query(Region).filter(Region.import_id == order.region, Region.courier_id == courier_id).first()
        courier = session.query(Courier).filter_by(id=courier_id).first()
        self.logger.debug(f"courier = {courier}, region = {region}")
        session.delete(region)
        session.delete(order)
        session.delete(courier)
        complete_time = (datetime.datetime.strptime(complete_time, '%Y-%m-%dT%H:%M:%S.%f') -
                         datetime.datetime.strptime(courier.assign_time, '%Y-%m-%dT%H:%M:%S.%f'))/60
        self.logger.debug(complete_time)
        complete_time = complete_time.seconds/60
        region.average_time = (region.average_time * region.orders_number + complete_time) / (region.orders_number + 1)
        region.orders_number = region.orders_number + 1
        courier.earnings = courier.earnings + 500 * value_dict[courier.transport]
        session.add(courier)
        session.add(region)
        session.commit()
        return order_id

order_complete_handler = OrderCompleteHandler()