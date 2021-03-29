from aiohttp import ClientSession
from asyncio import run
from time import time
from app.db.config import AppConfig

url = AppConfig.URL

async def main():
    async with ClientSession() as session:
        payload = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                    "courier_id": 2,
                    "courier_type": "bike",
                    "regions": [22],
                    "working_hours": ["09:00-18:00"]
                },
                {
                    "courier_id": 3,
                    "courier_type": "car",
                    "regions": [12, 22, 23, 33],
                    "working_hours": ["09:00-18:00"]
                }
            ]
        }
        async with session.post(url=url + "couriers", json=payload) as resp:
            print("Status:", resp.status)
            r = await resp.text()
            print("Json:", r)
        # async with session.post(url="http://localhost:8080/couriers") as resp:
        #     print("Status:", resp.status)
        #     r = await resp.json()
        #     print("Json:", r)
        #payload = {
        #    "regions": [11, 33, 2]
        #}
        #async with session.patch(url="http://localhost:8080/couriers/2", json=payload) as resp:
        #    print("Status:", resp.status)
        #    r = await resp.text()
        #    print("Json:", r)
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
        async with session.post(url=url + "orders", json=payload) as resp:
            print("Status:", resp.status)
            r = await resp.text()
            print("Json:", r)
        payload = {
            "courier_id": 2
            }
        async with session.post(url=url + "orders/assign", json=payload) as resp:
            print("Status:", resp.status)
            r = await resp.text()
            print("Json:", r)
        payload = {
            "courier_id": 2,
            "order_id": 3,
            "complete_time": time()
        }
        async with session.post(url=url + "orders/complete", json=payload) as resp:
            print("Status:", resp.status)
            r = await resp.text()
            print("Json:", r)
        async with session.get(url=url + "couriers/2") as resp:
            print("Status:", resp.status)
            r = await resp.text()
            print("Json:", r)


run(main())
