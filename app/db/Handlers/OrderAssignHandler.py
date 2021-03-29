from app.db.Handlers.BaseHandler import BaseHandler
from app.db.Models import *
from aiohttp.web import HTTPBadRequest
import datetime

weight_dict = {
    "foot": 10,
    "bike": 15,
    "car": 50
}


class OrderAssignHandler(BaseHandler):

    def check_timetable(self, hours, start, end):
        for i in hours:
            self.logger.debug(f"{i.start} {i.end} {start} {end}")
            if (start <= i.end) and (end >= i.start):
                return True
        return False

    def assign(self, raw_data):
        if ("courier_id" not in raw_data.keys()):
            self.logger.warning(f"no courier id")
            raise HTTPBadRequest
        courier_id = raw_data["courier_id"]
        session = self.make_session()
        courier = session.query(Courier).filter_by(id=courier_id).first()
        if courier is None:
            raise HTTPBadRequest
        orders = list(session.query(Order).filter_by(courier_id=courier_id).all())
        regions = list(session.query(Region).filter_by(courier_id=courier_id).all())
        regions = [i.import_id for i in regions]
        hours = list(session.query(CourierHours).filter_by(courier_id=courier_id).all())
        self.logger.debug(f"{courier} {orders} {regions} {hours}")
        orders = session.query(Order, DeliveryHours).filter(Order.courier_id == None, DeliveryHours.order_id == Order.id)
        orders = list(orders.filter(Order.weight <= weight_dict[courier.transport]).all())
        self.logger.debug(f"{orders}")
        copy = []
        for i in orders:
            self.logger.debug(f"{i[0].region} {regions}")
            if self.check_timetable(hours, i[1].start, i[1].end) and (i[0].region in regions) and (i[0] not in copy):
                copy.append(i[0])
        orders = copy
        self.logger.debug(f"{orders}")
        if orders:
            for i in orders:
                session.delete(i)
                i.courier_id = courier_id
                session.add(i)
            session.delete(courier)
            courier.assign_time = str(datetime.datetime.now().isoformat("T"))
            session.add(courier)
            session.commit()
            session = self.make_session()
        orders = list(session.query(Order).filter_by(courier_id=courier_id).all())
        orders = [{"id": i.id} for i in orders]
        courier = session.query(Courier).filter_by(id=courier_id).first()
        session.rollback()
        return orders, courier.assign_time


order_assign_handler = OrderAssignHandler()
