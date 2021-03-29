from app.db import engine
from sqlalchemy.orm import sessionmaker
from app.db.Models import *


class DB:
    def __init__(self, engine):
        self.engine = engine

    def push(self, *args):
        session = sessionmaker(bind=self.engine)()
        for i in args:
            for j in i:
                session.add(j)
        session.commit()

    def pop(self, type, index):
        session = sessionmaker(bind=self.engine)()
        session.delete(session.query(type).filter_by(id=index).all())
        session.commit()

    def get_courier(self, index):
        session = sessionmaker(bind=self.engine)()
        courier = session.query(Courier).filter_by(id=index).first()
        orders = list(session.query(Order).filter_by(courier_id=index).all())
        regions = list(session.query(Region).filter_by(courier_id=index).all())
        hours = list(session.query(CourierHours).filter_by(courier_id=index).all())
        session.commit()
        return courier, orders, regions, hours


db = DB(engine)
