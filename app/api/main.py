from app.api import host, port, app
from aiohttp.web import run_app
from routes import *
import sys
from pathlib import Path


def make_app():
    app.router.add_view('/couriers', CouriersView)
    app.router.add_view('/couriers/{courier_id:\d+}', CourierView)
    app.router.add_view('/orders', OrdersView)
    app.router.add_view('/orders/assign', OrdersAssignView)
    app.router.add_view('/orders/complete', OrderCompleteView)
    return app


app = make_app()

if __name__ == '__main__':
    logger.debug(f"{Path(__file__).parents[1]}")
    run_app(app, host=host, port=port)
