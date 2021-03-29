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


class TestCourierHandler(aiounittest.AsyncTestCase):

    def setUp(self):
        self.url = AppConfig.URL

    async def test_good_request(self):
        async with aiohttp.ClientSession() as client:
            payload = {
                "data": [
                    {
                        "courier_id": 1,
                        "courier_type": "foot",
                        "regions": [1, 2, 3],
                        "working_hours": ["11:35-14:05", "09:00-11:00"]
                    },
                    {
                        "courier_id": 2,
                        "courier_type": "bike",
                        "regions": [3],
                        "working_hours": ["09:00-18:00"]
                    },
                    {
                        "courier_id": 3,
                        "courier_type": "car",
                        "regions": [1, 2, 3, 4],
                        "working_hours": ["09:00-18:00"]
                    },
                    {
                        "courier_id": 4,
                        "courier_type": "foot",
                        "regions": [1, 3, 4],
                        "working_hours": ["11:35-14:05", "09:00-11:00"]
                    },
                    {
                        "courier_id": 5,
                        "courier_type": "bike",
                        "regions": [2],
                        "working_hours": ["09:00-18:00"]
                    },
                    {
                        "courier_id": 6,
                        "courier_type": "car",
                        "regions": [1, 2, 3, 4],
                        "working_hours": ["09:00-18:00"]
                    }
                ]
            }
            async with client.post(url=self.url + "couriers", json=payload) as resp:
                self.assertTrue(resp.status == 201)
                self.assertTrue(await resp.json() == {'couriers': [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}, {"id": 6}]})

    async def test_many_in_one(self):
        async with aiohttp.ClientSession() as client:
            payload = {
                "data": [
                    {
                        "courier_id": i,
                        "courier_type": "foot",
                        "regions": [1, 12, 22],
                        "working_hours": ["11:35-14:05", "09:00-11:00"]
                    } for i in range(1, 1000)
                ]
            }
            async with client.post(url=self.url + "couriers", json=payload) as resp:
                self.assertTrue(resp.status == 201)
                self.assertTrue(await resp.json() == {'couriers': [{"id": i} for i in range(1, 1000)]})

    async def test_many_in_different_requests(self):
        async with aiohttp.ClientSession() as client:
            async for i in myrange(1, 1000):
                payload = {
                    "data": [
                        {
                            "courier_id": i,
                            "courier_type": "foot",
                            "regions": [1, 12, 22],
                            "working_hours": ["11:35-14:05", "09:00-11:00"]
                        }
                    ]
                }
                async with client.post(url=self.url + "couriers", json=payload) as resp:
                    self.assertTrue(resp.status == 201)
                    self.assertTrue(await resp.json() == {'couriers': [{"id": i}]})

    async def test_nothing(self):
        async with aiohttp.ClientSession() as client:
            async with client.post(url=self.url + "couriers") as resp:
                self.assertTrue(resp.status == 400)

    async def test_no_data(self):
        async with aiohttp.ClientSession() as client:
            payload = {
                "data": []
            }
            async with client.post(url=self.url + "couriers", json=payload) as resp:
                self.assertTrue(resp.status == 400)

    async def test_region_catchable_errors(self):
        async with aiohttp.ClientSession() as client:
            payload = {
                "data": [
                    {
                        "courier_id": 1,
                        "courier_type": "foot",
                        "regions": [1, -12, 22],
                        "working_hours": ["11:35-14:05", "09:00-11:00"]
                    }, {
                        "courier_id": 2,
                        "courier_type": "foot",
                        "regions": [],
                        "working_hours": ["11:35-14:05", "09:00-11:00"]
                    }, {
                        "courier_id": 3,
                        "courier_type": "foot",
                        "regions": "string_value",
                        "working_hours": ["11:35-14:05", "09:00-11:00"]
                    }, {
                        "courier_id": 4,
                        "courier_type": "foot",
                        "working_hours": ["11:35-14:05", "09:00-11:00"]
                    }, {
                        "courier_id": 5,
                        "courier_type": "foot",
                        "regions": [1, 12.5, 22],
                        "working_hours": ["11:35-14:05", "09:00-11:00"]
                    }, {
                        "courier_id": 6,
                        "courier_type": "foot",
                        "regions": [1, 12, 22],
                        "working_hours": ["11:35-14:05", "09:00-11:00"],
                        "new field": "some additional info"
                    }
                ]
            }
            async with client.post(url=self.url + "couriers", json=payload) as resp:
                self.assertTrue(resp.status == 400)
                self.assertTrue(await resp.json() == {'validation_error': {'couriers': [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}, {"id": 6}]}})

    async def test_transport_catchable_errors(self):
        async with aiohttp.ClientSession() as client:
            payload = {
                "data": [
                    {
                        "courier_id": 1,
                        "courier_type": "",
                        "regions": [1, 2, 3],
                        "working_hours": ["11:35-14:05", "09:00-11:00"]
                    },
                    {
                        "courier_id": 2,
                        "regions": [3],
                        "working_hours": ["09:00-18:00"]
                    },
                    {
                        "courier_id": 3,
                        "courier_type": "some string",
                        "regions": [1, 2, 3, 4],
                        "working_hours": ["09:00-18:00"]
                    },
                    {
                        "courier_id": 4,
                        "courier_type": 123,
                        "regions": [1, 3, 4],
                        "working_hours": ["11:35-14:05", "09:00-11:00"]
                    }
                ]
            }
            async with client.post(url=self.url + "couriers", json=payload) as resp:
                self.assertTrue(resp.status == 400)
                self.assertTrue(await resp.json() == {'validation_error': {'couriers': [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]}})

    async def test_time_catchable_errors(self):
        async with aiohttp.ClientSession() as client:
            payload = {
                "data": [
                    {
                        "courier_id": 1,
                        "courier_type": "foot",
                        "regions": [1, 2, 3],
                        "working_hours": ["something"]
                    },
                    {
                        "courier_id": 2,
                        "courier_type": "bike",
                        "regions": [3],
                        "working_hours": ["09:00-18:00", "something"]
                    },
                    {
                        "courier_id": 3,
                        "courier_type": "car",
                        "regions": [1, 2, 3, 4],
                        "working_hours": ["09:0018:00"]
                    },
                    {
                        "courier_id": 4,
                        "courier_type": "foot",
                        "regions": [1, 3, 4],
                        "working_hours": ["11:35-1405", "0900-11:00"]
                    },
                    {
                        "courier_id": 5,
                        "courier_type": "bike",
                        "regions": [2],
                        "working_hours": [123, 23]
                    },
                    {
                        "courier_id": 6,
                        "courier_type": "car",
                        "regions": [1, 2, 3, 4],
                        "working_hours": ["123:00-18:00"]
                    }
                ]
            }
            async with client.post(url=self.url + "couriers", json=payload) as resp:
                print(await resp.text())
                self.assertTrue(resp.status == 400)
                self.assertTrue(await resp.json() == {'validation_error': {'couriers': [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}, {"id": 6}]}})

    async def test_with_orders(self):
        async with aiohttp.ClientSession() as client:
            payload = {
                "data": [
                    {
                        "order_id": 1,
                        "weight": 0.23,
                        "region": 1,
                        "delivery_hours": ["09:00-10:00"]
                    },
                    {
                        "order_id": 2,
                        "weight": 15,
                        "region": 2,
                        "delivery_hours": ["12:00-13:00"]
                    },
                    {
                        "order_id": 3,
                        "weight": 0.01,
                        "region": 3,
                        "delivery_hours": ["14:00-15:00", "18:00-19:30"]
                    }
                ]
            }
            async with client.post(url=self.url + "orders", json=payload) as resp:
                self.assertTrue(resp.status == 201)
                self.assertTrue(await resp.json() == {"orders": [{"id": 1}, {"id": 2}, {"id": 3}]})
            payload = {
                "data": [
                    {
                        "courier_id": 1,
                        "courier_type": "foot",
                        "regions": [1, 2, 3],
                        "working_hours": ["09:45-10:45", "11:15-12:15"]
                    },
                    {
                        "courier_id": 2,
                        "courier_type": "bike",
                        "regions": [3],
                        "working_hours": ["14:00-15:00"]
                    },
                    {
                        "courier_id": 3,
                        "courier_type": "car",
                        "regions": [1, 2, 3, 4],
                        "working_hours": ["18:00-19:00"]
                    }]}
            async with client.post(url=self.url + "orders", json=payload) as resp:
                self.assertTrue(resp.status == 201)
                self.assertTrue(await resp.json() == {"orders": [{"id": 1}, {"id": 2}, {"id": 3}]})

    def tearDown(self):
        session = sessionmaker(bind=engine)()
        session.query(Order).delete()
        session.query(Courier).delete()
        session.query(Region).delete()
        session.query(CourierHours).delete()
        session.query(DeliveryHours).delete()
        session.commit()
