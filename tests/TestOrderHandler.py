import aiounittest
import aiohttp, asyncio
from sqlalchemy.orm import sessionmaker
from app.db import engine
from app.db.Models import *
from config import AppConfig


async def myrange(start, stop=None, step=1):
    if stop:
        range_ = range(start, stop, step)
    else:
        range_ = range(start)
    for i in range_:
        yield i
        await asyncio.sleep(0)


class TestOrderHandler(aiounittest.AsyncTestCase):

    def setUp(self):
        self.url = AppConfig.URL

    async def test_good_request(self):
        async with aiohttp.ClientSession() as client:
            payload = {
                "data": [
                    {
                        "order_id": 1,
                        "weight": 0.23,
                        "region": 12,
                        "delivery_hours": ["09:00-18:00"]
                    },
                    {
                        "order_id": 2,
                        "weight": 15,
                        "region": 1,
                        "delivery_hours": ["09:00-18:00"]
                    },
                    {
                        "order_id": 3,
                        "weight": 0.01,
                        "region": 22,
                        "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                    }
                ]
            }
            async with client.post(url=self.url + "orders", json=payload) as resp:
                self.assertTrue(resp.status == 201)
                self.assertTrue(await resp.json() == {"orders": [{"id": 1}, {"id": 2}, {"id": 3}]})

    async def test_many_in_one(self):
        async with aiohttp.ClientSession() as client:
            payload = {
                "data": [
                    {
                        "order_id": i,
                        "weight": 0.23,
                        "region": 12,
                        "delivery_hours": ["09:00-18:00"]
                    } for i in range(1, 1000)
                ]
            }
            async with client.post(url=self.url + "orders", json=payload) as resp:
                self.assertTrue(resp.status == 201)
                self.assertTrue(await resp.json() == {'orders': [{"id": i} for i in range(1, 1000)]})

    async def test_many_in_different_requests(self):
        async with aiohttp.ClientSession() as client:
            async for i in myrange(1, 1000):
                payload = {
                    "data": [
                        {
                            "order_id": i,
                            "weight": 0.23,
                            "region": 12,
                            "delivery_hours": ["09:00-18:00"]
                        }
                    ]
                }
                async with client.post(url=self.url + "orders", json=payload) as resp:
                    self.assertTrue(resp.status == 201)
                    self.assertTrue(await resp.json() == {'orders': [{"id": i}]})

    async def test_nothing(self):
        async with aiohttp.ClientSession() as client:
            async with client.post(url=self.url + "orders") as resp:
                self.assertTrue(resp.status == 400)

    async def test_no_data(self):
        async with aiohttp.ClientSession() as client:
            payload = {
                "data": []
            }
            async with client.post(url=self.url + "orders", json=payload) as resp:
                self.assertTrue(resp.status == 400)

    async def test_region_catchable_errors(self):
        async with aiohttp.ClientSession() as client:
            payload = {
                "data": [
                    {
                        "order_id": 1,
                        "weight": 0.23,
                        "region": -12,
                        "delivery_hours": ["09:00-18:00"]
                    },
                    {
                        "order_id": 2,
                        "weight": 15,
                        "region": 1.5,
                        "delivery_hours": ["09:00-18:00"]
                    },
                    {
                        "order_id": 3,
                        "weight": 0.01,
                        "region": "string",
                        "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                    },
                    {
                        "order_id": 4,
                        "weight": 0.23,
                        "delivery_hours": ["09:00-18:00"]
                    },
                    {
                        "order_id": 5,
                        "weight": 15,
                        "region": [],
                        "delivery_hours": ["09:00-18:00"]
                    },
                    {
                        "order_id": 6,
                        "weight": 0.01,
                        "region": 22,
                        "delivery_hours": ["09:00-12:00", "16:00-21:30"],
                        "additional field": "useless info"
                    }
                ]
            }
            async with client.post(url=self.url + "orders", json=payload) as resp:
                print(await resp.text())
                self.assertTrue(resp.status == 400)
                self.assertTrue(await resp.json() == {'validation_error': {
                    'orders': [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}, {"id": 6}]}})

    async def test_weight_catchable_errors(self):
        async with aiohttp.ClientSession() as client:
            payload = {
                "data": [
                    {
                        "order_id": 1,
                        "weight": 0.001,
                        "region": 12,
                        "delivery_hours": ["09:00-18:00"]
                    },
                    {
                        "order_id": 2,
                        "weight": -15,
                        "region": 1,
                        "delivery_hours": ["09:00-18:00"]
                    },
                    {
                        "order_id": 3,
                        "weight": 555,
                        "region": 22,
                        "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                    },
                    {
                        "order_id": 4,
                        "weight": "string?",
                        "region": 12,
                        "delivery_hours": ["09:00-18:00"]
                    },
                    {
                        "order_id": 5,
                        "weight": [15],
                        "region": 1,
                        "delivery_hours": ["09:00-18:00"]
                    },
                    {
                        "order_id": 6,
                        "region": 22,
                        "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                    }
                ]
            }
            async with client.post(url=self.url + "orders", json=payload) as resp:
                print(await resp.text())
                self.assertTrue(resp.status == 400)
                self.assertTrue(await resp.json() == {'validation_error': {
                    'orders': [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}, {"id": 6}]}})

    async def test_delivery_hours_catchable_errors(self):
        async with aiohttp.ClientSession() as client:
            payload = {
                "data": [
                    {
                        "order_id": 1,
                        "weight": 0.23,
                        "region": 12,
                    },
                    {
                        "order_id": 2,
                        "weight": 15,
                        "region": 1,
                        "delivery_hours": ["09:0018:00"]
                    },
                    {
                        "order_id": 3,
                        "weight": 0.01,
                        "region": 22,
                        "delivery_hours": ["0900-12:00", "16:00-2130"]
                    },
                    {
                        "order_id": 4,
                        "weight": 0.23,
                        "region": 12,
                        "delivery_hours": ["29:00-18:00"]
                    },
                    {
                        "order_id": 5,
                        "weight": 15,
                        "region": 1,
                        "delivery_hours": ["string"]
                    },
                    {
                        "order_id": 6,
                        "region": 22,
                        "weight": 0.01,
                        "delivery_hours": ["09:00-12:00", "useless info"]
                    }
                ]
            }
            async with client.post(url=self.url + "orders", json=payload) as resp:
                print(await resp.text())
                self.assertTrue(resp.status == 400)
                self.assertTrue(await resp.json() == {'validation_error': {
                    'orders': [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}, {"id": 6}]}})


    def tearDown(self):
        session = sessionmaker(bind=engine)()
        session.query(Order).delete()
        session.query(Courier).delete()
        session.query(Region).delete()
        session.query(CourierHours).delete()
        session.query(DeliveryHours).delete()
        session.commit()
