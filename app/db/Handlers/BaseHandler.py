from app.db import logger, engine
from sqlalchemy.orm import sessionmaker


class BaseHandler:
    def __init__(self):
        self.logger = logger
        self.engine = engine

    def make_session(self):
        return sessionmaker(bind=self.engine)()

    def unpack_time(self, s):
        if (type(s) is str) and (s[2] == ":") and (s[5] == "-") and (s[8] == ":"):
            time1 = int(s[:2]) * 60 + int(s[3:5])
            time2 = int(s[6:8]) * 60 + int(s[9:])
            if 0 <= time1 < time2 <= 1440:
                return time1, time2
        return None, None
