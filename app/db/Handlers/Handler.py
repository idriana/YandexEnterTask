from app.db.Handlers.CourierHandler import CourierHandler
from app.db.Handlers.CourierEditHandler import CourierEditHandler
from app.db.Handlers.OrderHandler import OrderHandler
from app.db.Handlers.OrderAssignHandler import OrderAssignHandler
from app.db.Handlers.OrderCompleteHandler import OrderCompleteHandler
from app.db.Handlers.CourierStatsHandler import CourierStatsHandler


class Handler:
    pass


Handler.courier_push = CourierHandler.push
Handler.edit = CourierEditHandler.edit
Handler.order_push = OrderHandler.push
Handler.assign = OrderAssignHandler.assign
Handler.complete = OrderCompleteHandler.complete
Handler.stats = CourierStatsHandler.stats


handler = Handler()
