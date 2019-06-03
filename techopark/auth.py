import asyncio
import aioamqp
import aiosqlite
import json
from uuid import uuid4
from datetime import datetime, timedelta


class AuthMS:
    def __init__(self):
        self.channel = None
        self.inbound_queue = None
        self.outbound_queue = None
        self.database = None

    async def set_settings(self):
        transport, protocol = await aioamqp.connect(host='127.0.0.1', port=7000)
        self.channel = await protocol.channel()
        self.inbound_queue = await self.channel.queue_declare(queue_name='inbound')
        self.outbound_queue = await self.channel.queue_declare(queue_name='outbound')
        self.database = await aiosqlite.connect("database.db")

    async def callback(self, channel, body, envelope, properties):
        metadata = json.loads(body)
        request_type = metadata.get("request_type")
        request_data = metadata.get("request_data")

        if request_type == "signup":
            response = await self.signup(request_data)
        elif request_type == "login":
            response = await self.login(request_data)
        elif request_type == "validate":
            response = await self.validate(request_data)

        await channel.basic_publish(
            payload=response,
            exchange_name='',
            routing_key='outbound'
        )

    async def signup(self, request_data):
        email = request_data.get("email")
        password = request_data.get("password")
        name = request_data.get("name")

        if email and password and name:
            token = uuid4()
            date = datetime.now() + timedelta(hours=24)
            await self.database.execute(
                "INSERT INTO User(email,password,name,token,exist,create,last) VALUES({},{},{},{},{},{},{})".format(
                    email, password, name, token, date, datetime.now(), datetime.now()))
            return {"status": "ok", "data": {"token": token, "expire": date}}
        else:
            return {"status": "Missing email, password or name", "data": {}}

    async def login(self, request_data):
        email = request_data.get("email")
        password = request_data.get("password")

        if email and password:
            token = uuid4()
            date = datetime.now() + timedelta(hours=24)
            await self.database.execute(
                "UPDATE User SET token={},last={} WHERE email={}".format(
                    date, datetime.now(), email))
            return {"status": "ok", "data": {"token": token, "expire": date}}
        else:
            return {"status": "Wrong email or password", "data": {}}

    async def validate(self, request_data):
        token = request_data.get("token")
        if token:
            cursor = await self.database.execute(
                "SELECT expire FROM User WHERE token ={}".format(token))
            row = await cursor.fetchall()
            if (datetime.now() - row[0][0]).hours > 24:
                await cursor.close()
                return {"status": "Old token", "data": {}}
            else:
                new_token = uuid4()
                new_date = datetime.now() + timedelta(hours=24)
                cursor = await self.database.execute(
                    "SELECT email,password,name,create,last FROM User WHERE token ={}".format(token))
                row = await cursor.fetchall()
                email = row[0][0]
                password = row[0][1]
                name = row[0][2]
                create = row[0][3]
                last = row[0][4]
                await self.database.execute(
                    "UPDATE User SET token={},expire={} WHERE email={}".format(
                        new_token, new_date, email))
                return {"status": "ok",
                        "data": {"email": email, "password": password, "name": name, "create": create, "last": last}}
        return {"status": "“forbidden”", "data": {}}

    async def main():
        auth_ms = AuthMS()
        await auth_ms.set_settings()
        await auth_ms.channel.basic_consume(auth_ms.callback, queue_name='inbound', no_ack=True)

    asyncio.run(main())
