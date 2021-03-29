import os
import logging

basedir = os.path.abspath(os.path.dirname(__file__))


class DBConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or 'sqlite:///' + os.path.join(basedir, "app", "db", "app.db")
    SQLALCHEMY_ECHO = True
    ALEMBIC_INI_PATH = os.path.join(basedir, "app", "alembic.ini")
    LOGGING = logging.DEBUG


class AppConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'some-secret-key'
    HOST = "127.0.0.1"
    PORT = "8080"
    URL = "http://localhost:8080/"
    MEGABYTE = 1024 ** 2
    MAX_REQUEST_SIZE = 70 * MEGABYTE
    LOGGING = logging.DEBUG
