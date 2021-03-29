from app.db import engine
from sqlalchemy.orm import sessionmaker
from app.db.Models import Courier

session = sessionmaker(bind=engine)()
res = session.query(Courier).all()
print(res)
for i in res:
    session.delete(i)
session.commit()