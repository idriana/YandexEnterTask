from aiohttp.web import run_app
from app.api import host, port, app
from app.api.routes import *


def make_app():
    app.router.add_view('/couriers', CouriersView)
    app.router.add_view('/couriers/{courier_id:\d+}', CourierView)
    app.router.add_view('/orders', OrdersView)
    app.router.add_view('/orders/assign', OrdersAssignView)
    app.router.add_view('/orders/complete', OrderCompleteView)
    return app


if __name__ == '__main__':
    run_app(make_app(), host=host, port=port)
