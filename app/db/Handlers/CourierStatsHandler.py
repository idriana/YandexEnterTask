from app.db.Handlers.BaseHandler import BaseHandler
from app.db.Models import *
from math import trunc
from aiohttp.web import HTTPBadRequest


class CourierStatsHandler(BaseHandler):
    def stats(self, courier_id):
        session = self.make_session()
        courier = session.query(Courier).filter_by(id=courier_id).first()
        if courier is None:
            raise HTTPBadRequest
        regions = list(session.query(Region).filter_by(courier_id=courier_id).all())
        hours = list(session.query(CourierHours).filter_by(courier_id=courier_id).all())
        time = min([i.average_time for i in regions])
        rating = (60*60 - min(time, 60*60))/(60*60) * 5
        res = {
            "courier_id": int(courier_id),
            "courier_type": courier.transport,
            "regions": [i.import_id for i in regions],
            "working_hours": [str(i) for i in hours],
            "rating": trunc(rating*100)/100,
            "earnings": courier.earnings
        }
        self.logger.debug(str(res))
        return res


courier_stats_handler = CourierStatsHandler()