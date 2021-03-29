from aiohttp.web import run_app, Application
from app.api import host, port, AppConfig
from app.api.routes import *
import sys
from pathlib import Path

def make_app():
    sys.path.append(Path(__file__).parents[2])
    app = Application(client_max_size=AppConfig.MAX_REQUEST_SIZE)
    app.router.add_view('/couriers', CouriersView)
    app.router.add_view('/couriers/{courier_id:\d+}', CourierView)
    app.router.add_view('/orders', OrdersView)
    app.router.add_view('/orders/assign', OrdersAssignView)
    app.router.add_view('/orders/complete', OrderCompleteView)
    return app


app = make_app()

if __name__ == '__main__':
    run_app(app, host=host, port=port)
