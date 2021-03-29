from config import AppConfig
import logging
from aiomisc.log import basic_config
from aiohttp.web import Application

basic_config(AppConfig.LOGGING, buffered=True)
logger = logging.getLogger("api_logger")

host = AppConfig.HOST
port = AppConfig.PORT

