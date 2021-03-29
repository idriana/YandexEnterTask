from app.api import logger
from aiohttp.web_response import json_response
from aiohttp.web import View, HTTPBadRequest
from app.db.Handlers.CourierHandler import courier_handler
from app.db.Handlers.CourierEditHandler import courier_edit_handler
from app.db.Handlers.OrderHandler import order_handler
from app.db.Handlers.OrderAssignHandler import order_assign_handler
from app.db.Handlers.OrderCompleteHandler import order_complete_handler
from app.db.Handlers.CourierStatsHandler import courier_stats_handler

class CouriersView(View):
    async def post(self):
        try:
            req = await self.request.json()
            logger.debug(f"{req}")
        except Exception as e:
            logger.warning(e)
            raise HTTPBadRequest()
        res = await courier_handler.push(req)
        if "error" in res.keys():
            if res["error"]:
                return json_response({"validation_error": {"couriers": res["error"]}}, status=400)
            else:
                raise HTTPBadRequest()
        return json_response(res, status=201)


class CourierView(View):
    async def patch(self):
        try:
            req = await self.request.json()
            logger.debug(f"{req}")
        except Exception as e:
            logger.warning(e)
            raise HTTPBadRequest
        res = courier_edit_handler.edit(self.request.match_info.get("courier_id"), req)
        return json_response(res)

    async def get(self):
        return json_response(courier_stats_handler.stats(self.request.match_info.get("courier_id")))


class OrdersView(View):
    async def post(self):
        try:
            req = await self.request.json()
            logger.debug(f"{req}")
        except Exception as e:
            logger.warning(e)
            raise HTTPBadRequest()
        res = await order_handler.push(req)
        if "error" in res.keys():
            if res["error"]:
                return json_response({"validation_error": {"orders": res["error"]}}, status=400)
            else:
                raise HTTPBadRequest()
        return json_response(res, status=201)


class OrdersAssignView(View):
    async def post(self):
        try:
            req = await self.request.json()
            logger.debug(f"{req}")
        except Exception as e:
            logger.warning(e)
            raise HTTPBadRequest()
        orders, assign_time = order_assign_handler.assign(req)
        if orders:
            return json_response({"orders": orders, "assign_time": assign_time})
        return json_response({"orders": orders})


class OrderCompleteView(View):
    async def post(self):
        try:
            req = await self.request.json()
            logger.debug(f"{req}")
        except Exception as e:
            logger.warning(e)
            raise HTTPBadRequest()
        order = order_complete_handler.complete(req)
        return json_response({"order_id": order})

