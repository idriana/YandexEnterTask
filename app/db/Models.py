from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from app.db import metadata

base = declarative_base(metadata=metadata)


class Courier(base):
    """таблица курьеров"""
    __tablename__ = "courier"

    id = Column(Integer, primary_key=True)
    transport = Column(String(4))  # foot или bike или car
    earnings = Column(Integer)  # суммарный заработок
    assign_time = Column(String(32))  # последнее время выдачи заказов этому курьеру
    regions = relationship("Region", backref="courier", lazy="dynamic")  # регионы, в которых работает курьер
    hours = relationship("CourierHours", backref="courier", lazy="dynamic")  # часы работы курьера
    orders = relationship("Order", backref="courier", lazy="dynamic")

    def __repr__(self):
        return f"<Courier {self.id}>"


class Order(base):
    """таблица заказов"""
    __tablename__ = "order"

    id = Column(Integer, primary_key=True)
    weight = Column(Float)  # вес заказа
    region = Column(Integer)  # регион заказа
    courier_id = Column(Integer, ForeignKey("courier.id"))  # курьер, взявший заказ
    hours = relationship("DeliveryHours", backref="order", lazy="dynamic")  # часы доставки заказа

    def __repr__(self):
        return f"<Order {self.id}>"


class Region(base):
    """таблица регионов со статистикой для каждого курьера"""
    __tablename__ = "region"

    id = Column(Integer, primary_key=True)
    import_id = Column(Integer)  # изначальный айди района, не уникальный в таблице
    average_time = Column(Integer)  # статистика по времени для курьера
    orders_number = Column(Integer)  # количество выполненных заказов в этом районе для курьера
    courier_id = Column(Integer, ForeignKey("courier.id"))  # курьер, к которому привязана запись о регионе

    def __repr__(self):
        return f"<Region {self.import_id}>"


class CourierHours(base):
    """таблица часов работы курьеров"""
    __tablename__ = "courier_hours"

    id = Column(Integer, primary_key=True)
    start = Column(Integer)  # время в минутах с начала суток
    end = Column(Integer)
    courier_id = Column(Integer, ForeignKey("courier.id"))  # курьер, к которому привязана запись о часах работы

    def __repr__(self):
        m_start = str(self.start//60)
        m_start = ("0" * (len(m_start) % 2)) + m_start
        s_start = str(self.start%60)
        s_start = s_start + ("0" * (len(s_start) % 2))
        m_end = str(self.end//60)
        m_end = ("0" * (len(m_end) % 2)) + m_end
        s_end = str(self.end%60)
        s_end = s_end + ("0" * (len(s_end) % 2))
        return f"{m_start}:{s_start}-{m_end}:{s_end}"

    def __str__(self):
        return self.__repr__()


class DeliveryHours(base):
    """таблица часов приема заказов"""
    __tablename__ = "delivery_hours"

    id = Column(Integer, primary_key=True)
    start = Column(Integer)  # время в минутах с начала суток
    end = Column(Integer)
    order_id = Column(Integer, ForeignKey("order.id"))  # заказ, к которому привязана запись о часах доставки

    def __repr__(self):
        m_start = str(self.start // 60)
        m_start = ("0" * (len(m_start) % 2)) + m_start
        s_start = str(self.start % 60)
        s_start = s_start + ("0" * (len(s_start) % 2))
        m_end = str(self.end // 60)
        m_end = ("0" * (len(m_end) % 2)) + m_end
        s_end = str(self.end % 60)
        s_end = s_end + ("0" * (len(s_end) % 2))
        return f"{m_start}:{s_start}-{m_end}:{s_end}"

    def __str__(self):
        return self.__repr__()
