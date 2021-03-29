from app.db.config import AppConfig
import logging
from aiomisc.log import basic_config
from aiohttp.web import Application

basic_config(AppConfig.LOGGING, buffered=True)
logger = logging.getLogger("api_logger")
host = AppConfig.HOST
port = AppConfig.PORT

from aiohttp.web import run_app
from .routes import *
import sys
from pathlib import Path

def make_app():
    sys.path.append(Path(__file__).parents[2])
    sys.path.append(Path(__file__).parents[1])
    app = Application(client_max_size=AppConfig.MAX_REQUEST_SIZE)
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
