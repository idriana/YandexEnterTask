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


class TestCourierEditHandler(aiounittest.AsyncTestCase):

    def setUp(self):
        self.url = AppConfig.URL
        self.test_good_request()

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

    async def test_good_edit_requests(self):
        async with aiohttp.ClientSession() as client:
            payload = [
                {"regions": [1, 2, 3, 4]},
                {"courier_type": "foot", "regions": [3, 2], "working_hours": ["09:00-16:00"]},
                {"courier_type": "bike", "regions": [1, 2]},
                {"courier_type": "car", "regions": [1, 3, 4, 5, 6], "working_hours": ["10:00-20:00"]},
                {"working_hours": ["09:00-12:00", "13:00-18:00"]},
                {"courier_type": "foot"}
            ]
            answers = [
                {'courier_id': '1', 'courier_type': 'foot', 'regions': [1, 2, 3, 4],
                 'working_hours': ['11:35-14:50', '09:00-11:00']},
                {'courier_id': '2', 'courier_type': 'foot', 'regions': [3, 2], 'working_hours': ['09:00-16:00']},
                {'courier_id': '3', 'courier_type': 'bike', 'regions': [1, 2], 'working_hours': ['09:00-18:00']},
                {'courier_id': '4', 'courier_type': 'car', 'regions': [1, 3, 4, 5, 6],
                 'working_hours': ['10:00-20:00']},
                {'courier_id': '5', 'courier_type': 'bike', 'regions': [2],
                 'working_hours': ['09:00-12:00', '13:00-18:00']},
                {'courier_id': '6', 'courier_type': 'foot', 'regions': [1, 2, 3, 4], 'working_hours': ['09:00-18:00']}
            ]
            async for i in myrange(0, 6):
                async with client.patch(url=self.url + f"couriers/{i + 1}", json=payload[i]) as resp:
                    self.assertTrue(resp.status == 200)
                    self.assertTrue(await resp.json() == answers[i])

    async def test_many_edits(self):
        async with aiohttp.ClientSession() as client:
            payload = [
                {"regions": [1, 2, 3, 4]},
                {"courier_type": "foot", "regions": [3, 2], "working_hours": ["09:00-16:00"]},
                {"courier_type": "bike", "regions": [1, 2]},
                {"courier_type": "car", "regions": [1, 3, 4, 5, 6], "working_hours": ["10:00-20:00"]},
                {"courier_type": "foot", "regions": [1, 2, 3], "working_hours": ["11:35-14:05", "09:00-11:00"]},
                {"courier_type": "bike", "regions": [3], "working_hours": ["09:00-18:00"]}
            ]
            answers = [
                {'courier_id': '1', 'courier_type': 'foot', 'regions': [1, 2, 3, 4],
                 'working_hours': ['11:35-14:50', '09:00-11:00']},
                {'courier_id': '2', 'courier_type': 'foot', 'regions': [3, 2], 'working_hours': ['09:00-16:00']},
                {'courier_id': '1', 'courier_type': 'bike', 'regions': [1, 2],
                 'working_hours': ['11:35-14:50', '09:00-11:00']},
                {'courier_id': '2', 'courier_type': 'car', 'regions': [1, 3, 4, 5, 6],
                 'working_hours': ['10:00-20:00']},
                {'courier_id': '1', 'courier_type': 'foot', 'regions': [1, 2, 3],
                 'working_hours': ['11:35-14:50', '09:00-11:00']},
                {'courier_id': '2', 'courier_type': 'bike', 'regions': [3], 'working_hours': ['09:00-18:00']}
            ]
            async for i in myrange(0, 1000):
                async with client.patch(url=self.url + f"couriers/{i % 2 + 1}", json=payload[i % 6]) as resp:
                    self.assertTrue(resp.status == 200)
                    self.assertTrue(await resp.json() == answers[i % 6])

    async def test_nothing(self):
        async with aiohttp.ClientSession() as client:
            payload = dict()
            async with client.patch(url=self.url + f"couriers/{2}", json=payload) as resp:
                print(resp.status)
                print(await resp.text())
                print(await resp.json())
                #self.assertTrue(resp.status == 200)
                #self.assertTrue(await resp.json() == answers[i % 6])

    async def test_wrong_courier_id(self):
        async with aiohttp.ClientSession() as client:
            payload = dict()
            async with client.patch(url=self.url + f"couriers/{-4}", json=payload) as resp:
                self.assertTrue(resp.status == 404)
            async with client.patch(url=self.url + f"couriers/{'abc'}", json=payload) as resp:
                self.assertTrue(resp.status == 404)
            async with client.patch(url=self.url + f"couriers/{2.5}", json=payload) as resp:
                self.assertTrue(resp.status == 404)
            async with client.patch(url=self.url + f"couriers/{10}", json=payload) as resp:
                self.assertTrue(resp.status == 400)

    async def test_wrong_params(self):
        async with aiohttp.ClientSession() as client:
            payload = [
                {"regions": [1, -2, 3, 4]},
                {"courier_type": "strange string", "regions": [3, 2], "working_hours": ["09:00-16:00"]},
                {"courier_type": "bike", "regions": [1, 2], "additional field": "useless info"},
                {"courier_type": "car", "regions": [1, 3, 4, 5, 6], "working_hours": ["wrong hours"]},
                {123: "why not figure"}
            ]
            async for i in myrange(0, 5):
                async with client.patch(url=self.url + f"couriers/{i + 1}", json=payload[i]) as resp:
                    self.assertTrue(resp.status == 400)

    def tearDown(self):
        session = sessionmaker(bind=engine)()
        session.query(Order).delete()
        session.query(Courier).delete()
        session.query(Region).delete()
        session.query(CourierHours).delete()
        session.query(DeliveryHours).delete()
        session.commit()
