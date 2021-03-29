from aiohttp.web import run_app
from app.api import host, port
from routes import app


run_app(app, host=host, port=port)
