from app.db.Models import Courier, Region, CourierHours
from app.db.Handlers.BaseHandler import BaseHandler


class CourierHandler(BaseHandler):

    def make_time_records(self, courier_id, args: list):
        res = []
        for i in args:
            time1, time2 = self.unpack_time(i)
            if time1 and time2:
                res.append(CourierHours(start=time1, end=time2, courier_id=courier_id))
                self.logger.debug(f"CourierHours(start={time1}, end={time2}, courier_id={courier_id})")
            else:
                return None
        if res:
            return res
        return None

    def make_region_records(self, courier_id, args: list):
        res = []
        for i in args:
            if (type(i) is not int) or (i <= 0):
                return None
            res.append(Region(import_id=i, average_time=0, orders_number=0, courier_id=courier_id))
            self.logger.debug(f"Region(import_id={i}, average_time=0, orders_number=0, courier_id={courier_id})")
        if res:
            return res
        return None

    def make_courier_record(self, courier_id, transport):
        if transport not in ["foot", "bike", "car"]:
            return None
        if (type(courier_id) is not int) or (courier_id <= 0):
            return None
        courier = Courier(id=courier_id, transport=transport, earnings=0)
        self.logger.debug(f"Courier(id={courier_id}, transport={transport}, earnings=0)")
        return courier

    async def push(self, raw_data):
        couriers = []
        regions = []
        hours = []
        errors = []
        ok = []
        if "data" in raw_data.keys():
            for i in raw_data["data"]:
                if "courier_id" in i.keys():
                    if ("courier_type" in i.keys()) and ("regions" in i.keys()) \
                            and ("working_hours" in i.keys()) and (len(i.keys()) == 4):
                        courier = self.make_courier_record(i["courier_id"], i["courier_type"])
                        courier_regions = self.make_region_records(i['courier_id'], i["regions"])
                        courier_hours = self.make_time_records(i['courier_id'], i["working_hours"])
                        if courier and courier_hours and courier_regions:
                            couriers.append(courier)
                            regions.extend(courier_regions)
                            hours.extend(courier_hours)
                            ok.append({"id": i["courier_id"]})
                        else:
                            self.logger.warning(f"wrong params")
                            errors.append({"id": i["courier_id"]})
                    else:
                        self.logger.warning(f"wrong keys")
                        errors.append({"id": i["courier_id"]})
                else:
                    self.logger.warning("no courier_id")
                    return {"error": []}
        else:
            self.logger.warning("no data field")
            return {"error": []}
        session = self.make_session()
        if not errors:
            if couriers:
                for i in couriers + regions + hours:
                    session.add(i)
                session.commit()
                return {"couriers": ok}
            else:
                session.rollback()
                self.logger.warning("no data")
                return {"error": []}
        else:
            session.rollback()
            return {"error": errors}


courier_handler = CourierHandler()

