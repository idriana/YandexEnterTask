import aiounittest
import aiohttp, asyncio
from sqlalchemy.orm import sessionmaker
from app.db import engine
from app.db.Models import *
from config import AppConfig
import datetime


async def myrange(start, stop=None, step=1):
    if stop:
        range_ = range(start, stop, step)
    else:
        range_ = range(start)
    for i in range_:
        yield i
        await asyncio.sleep(0)


class TestAssignCompleteOrderHandler(aiounittest.AsyncTestCase):

    def setUp(self):
        self.url = AppConfig.URL
        self.test_good_order_request()
        self.test_good_courier_request()

    async def test_good_order_request(self):
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

    async def test_good_courier_request(self):
        async with aiohttp.ClientSession() as client:
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
                    },
                    {
                        "courier_id": 4,
                        "courier_type": "foot",
                        "regions": [1, 3, 4],
                        "working_hours": ["12:35-15:05"]
                    },
                    {
                        "courier_id": 5,
                        "courier_type": "bike",
                        "regions": [2],
                        "working_hours": ["09:00-13:00"]
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
                self.assertTrue(await resp.json() == {
                    'couriers': [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}, {"id": 6}]})

    async def test_with_different_orders_1(self):
        async with aiohttp.ClientSession() as client:
            async with client.post(url=self.url + "orders/assign", json={"courier_id": 1}) as resp:
                self.assertTrue(resp.status == 200)
                resp = await resp.json()
                self.assertTrue(resp["orders"] == [{"id": 1}])
                self.assertTrue("assign_time" in resp.keys())
                # self.assertTrue(resp.status == 201)
                # self.assertTrue(await resp.json() == {'couriers': [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}, {"id": 6}]})
            async with client.post(url=self.url + "orders/assign", json={"courier_id": 2}) as resp:
                self.assertTrue(resp.status == 200)
                resp = await resp.json()
                self.assertTrue(resp["orders"] == [{"id": 3}])
                self.assertTrue("assign_time" in resp.keys())
            async with client.post(url=self.url + "orders/assign", json={"courier_id": 6}) as resp:
                self.assertTrue(resp.status == 200)
                resp = await resp.json()
                self.assertTrue(resp["orders"] == [{"id": 2}])
                self.assertTrue("assign_time" in resp.keys())
            async with aiohttp.ClientSession() as client:
                payload = {
                    "courier_id": 2,
                    "order_id": 3,
                    "complete_time": str(datetime.datetime.now().isoformat('T'))
                }
                async with client.post(url=self.url + "orders/complete", json=payload) as resp:
                    self.assertTrue(resp.status == 200)
                    self.assertTrue(await resp.json() == {"order_id": 3})
                async with client.post(url=self.url + "orders/complete", json=payload) as resp:
                    self.assertTrue(resp.status == 400)
                payload = {
                    "courier_id": 6,
                    "order_id": 2,
                    "complete_time": str(datetime.datetime.now().isoformat('T'))
                }
                async with client.post(url=self.url + "orders/complete", json=payload) as resp:
                    self.assertTrue(resp.status == 200)
                    self.assertTrue(await resp.json() == {"order_id": 2})
                async with client.post(url=self.url + "orders/assign", json={"courier_id": 6}) as resp:
                    self.assertTrue(resp.status == 200)
                    resp = await resp.json()
                    self.assertTrue(resp["orders"] == [])
                    self.assertTrue("assign_time" not in resp.keys())
                async with client.get(url=self.url + "couriers/6") as resp:
                    print(resp.status)
                    resp = await resp.json()
                    self.assertTrue(resp["courier_id"] == 6)
                    self.assertTrue(resp["courier_type"] == "car")
                    self.assertTrue(resp["regions"] == [1, 2, 3, 4])
                    self.assertTrue(resp["working_hours"] == ["09:00-18:00"])
                    self.assertTrue(resp["earnings"] == 4500)
                    """
                    self.assertTrue(resp.status == 200)
                    resp = await resp.json()
                    self.assertTrue(resp["orders"] == [])
                    self.assertTrue("assign_time" not in resp.keys())"""

    async def test_with_different_orders_2(self):
        async with aiohttp.ClientSession() as client:
            async with client.post(url=self.url + "orders/assign", json={"courier_id": 6}) as resp:
                self.assertTrue(resp.status == 200)
                resp = await resp.json()
                self.assertTrue(resp["orders"] == [{"id": 1}, {"id": 2}, {"id": 3}])
                self.assertTrue("assign_time" in resp.keys())
                # self.assertTrue(resp.status == 201)
                # self.assertTrue(await resp.json() == {'couriers': [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}, {"id": 6}]})
            async with client.post(url=self.url + "orders/assign", json={"courier_id": 1}) as resp:
                self.assertTrue(resp.status == 200)
                resp = await resp.json()
                self.assertTrue(resp["orders"] == [])
                self.assertTrue("assign_time" not in resp.keys())
            async with client.post(url=self.url + "orders/assign", json={"courier_id": 2}) as resp:
                self.assertTrue(resp.status == 200)
                resp = await resp.json()
                self.assertTrue(resp["orders"] == [])
                self.assertTrue("assign_time" not in resp.keys())
            payload = {
                "courier_id": 6,
                "order_id": 2,
                "complete_time": str(datetime.datetime.now().isoformat('T'))
            }
            async with client.post(url=self.url + "orders/complete", json=payload) as resp:
                self.assertTrue(resp.status == 200)
                self.assertTrue(await resp.json() == {"order_id": 2})
            payload = {
                "courier_id": 6,
                "order_id": 3,
                "complete_time": str(datetime.datetime.now().isoformat('T'))
            }
            async with client.post(url=self.url + "orders/complete", json=payload) as resp:
                self.assertTrue(resp.status == 200)
                self.assertTrue(await resp.json() == {"order_id": 3})
            async with client.post(url=self.url + "orders/assign", json={"courier_id": 6}) as resp:
                self.assertTrue(resp.status == 200)
                resp = await resp.json()
                self.assertTrue(resp["orders"] == [{"id": 1}])
                self.assertTrue("assign_time" in resp.keys())
            async with client.get(url=self.url + "couriers/26") as resp:
                print(resp.status)
                print(await resp.text())

    async def test_with_different_orders_3(self):
        async with aiohttp.ClientSession() as client:
            async with client.post(url=self.url + "orders/assign", json={"courier_id": 3}) as resp:
                self.assertTrue(resp.status == 200)
                resp = await resp.json()
                self.assertTrue(resp["orders"] == [{"id": 3}])
                self.assertTrue("assign_time" in resp.keys())
            async with client.post(url=self.url + "orders/assign", json={"courier_id": 2}) as resp:
                self.assertTrue(resp.status == 200)
                resp = await resp.json()
                self.assertTrue(resp["orders"] == [])
                self.assertTrue("assign_time" not in resp.keys())
            async with client.post(url=self.url + "orders/assign", json={"courier_id": 4}) as resp:
                self.assertTrue(resp.status == 200)
                resp = await resp.json()
                self.assertTrue(resp["orders"] == [])
                self.assertTrue("assign_time" not in resp.keys())
            async with client.post(url=self.url + "orders/assign", json={"courier_id": 5}) as resp:
                self.assertTrue(resp.status == 200)
                resp = await resp.json()
                self.assertTrue(resp["orders"] == [{"id": 2}])
                self.assertTrue("assign_time" in resp.keys())
            async with client.post(url=self.url + "orders/assign", json={"courier_id": 1}) as resp:
                self.assertTrue(resp.status == 200)
                resp = await resp.json()
                self.assertTrue(resp["orders"] == [{"id": 1}])
                self.assertTrue("assign_time" in resp.keys())
            payload = [{
                "courier_id": 4,
                "order_id": 3,
                "complete_time": str(datetime.datetime.now().isoformat('T'))
            },{
                "courier_id": 12,
                "order_id": 3,
                "complete_time": str(datetime.datetime.now().isoformat('T'))
            },{
                "courier_id": 4,
                "order_id": 12,
                "complete_time": str(datetime.datetime.now().isoformat('T'))
            }]
            for i in payload:
                async with client.post(url=self.url + "orders/complete", json=i) as resp:
                    self.assertTrue(resp.status == 400)
                    #self.assertTrue(await resp.json() == {"order_id": 3})




    def tearDown(self):
        session = sessionmaker(bind=engine)()
        session.query(Order).delete()
        session.query(Courier).delete()
        session.query(Region).delete()
        session.query(CourierHours).delete()
        session.query(DeliveryHours).delete()
        session.commit()
