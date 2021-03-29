from app.db.Handlers.CourierHandler import CourierHandler
from aiohttp.web import HTTPBadRequest
from app.db.Models import *

weight_dict = {
    "foot": 10,
    "bike": 15,
    "car": 50
}


class CourierEditHandler(CourierHandler):
    def edit(self, courier_id, raw_data):
        session = self.make_session()
        courier_query = session.query(Courier).filter_by(id=courier_id)
        courier = courier_query.first()
        if courier is None:
            raise HTTPBadRequest
        orders_query = session.query(Order).filter_by(courier_id=courier_id)
        orders = list(orders_query.all())
        regions_query = session.query(Region).filter_by(courier_id=courier_id)
        regions = list(regions_query.all())
        hours_query = session.query(CourierHours).filter_by(courier_id=courier_id)
        hours = list(hours_query.all())
        self.logger.debug(f"{courier} {orders} {regions} {hours}")
        for i in raw_data.keys():
            if i == "courier_type":
                if raw_data["courier_type"] in ["foot", "bike", "car"]:
                    pass
                    session.delete(courier)
                    courier.transport = raw_data[i]
                    session.add(courier)
                    orders_query.delete()
                    for j in orders:
                        if j.weight > weight_dict[raw_data[i]]:
                            j.courier_id = None
                        session.add(j)
                else:
                    session.rollback()
                    raise HTTPBadRequest
            elif i == "regions":
                regions = self.make_region_records(courier_id, raw_data[i])
                if regions:
                    regions_query.delete()
                    for j in regions:
                        session.add(j)
                else:
                    session.rollback()
                    raise HTTPBadRequest
            elif i == "working_hours":
                hours = self.make_time_records(courier_id, raw_data[i])
                if hours:
                    hours_query.delete()
                    for j in hours:
                        session.add(j)
                else:
                    session.rollback()
                    raise HTTPBadRequest
            else:
                self.logger.warning("wrong keys for courier editing")
                session.rollback()
                raise HTTPBadRequest()
        session.commit()
        res = {
            "courier_id": courier_id,
            "courier_type": courier.transport,
            "regions": [i.import_id for i in regions],
            "working_hours": [str(i) for i in hours]
        }
        self.logger.debug(f"edit res: {res}")
        return res


courier_edit_handler = CourierEditHandler()
