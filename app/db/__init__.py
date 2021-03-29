from app.db.config import DBConfig
from sqlalchemy import create_engine, MetaData
import logging
from aiomisc.log import basic_config


def alembic_configure():
    with open(DBConfig.ALEMBIC_INI_PATH, "r") as file:
        s = file.read()
    res = s[:s.find("sqlalchemy.url = ") + 17] + DBConfig.SQLALCHEMY_DATABASE_URI
    s = s[s.find("sqlalchemy.url = ") + 18:]
    res = res + s[s.find("\n"):]
    with open(DBConfig.ALEMBIC_INI_PATH, "w") as file:
        file.write(res)


conversation = {
    "all_column_names": lambda constraint, table: ' '.join([
        column.name for column in constraint.columns.values()
    ]),
    "ix": 'ix_%(table_name)s_%(all_column_names)s',
    "uq": "uq_%(table_name)s_%(all_column_names)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(all_column_names)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

basic_config(DBConfig.LOGGING, buffered=True)
logger = logging.getLogger("db_logger")
alembic_configure()
engine = create_engine(DBConfig.SQLALCHEMY_DATABASE_URI, echo=DBConfig.SQLALCHEMY_ECHO)
metadata = MetaData(bind=engine, naming_convention=conversation)
