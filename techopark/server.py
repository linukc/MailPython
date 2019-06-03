from aiohttp import web
import aioamqp
import json
from uuid import uuid4
import asyncio
import aiosqlite


class Handler:

    def __init__(self):
        self.requests = {}
        self.channel = None
        self.inbound_queue = None
        self.outbound_queue = None
        self.incrawler_queue = None
        self.outcrawler_queue = None
        self.database = None

    async def set_settings(self):
        transport, protocol = await aioamqp.connect(host='127.0.0.1', port=7000)
        self.channel = await protocol.channel()
        self.inbound_queue = await self.channel.queue_declare(queue_name='inbound')
        self.outbound_queue = await self.channel.queue_declare(queue_name='outbound')
        self.incrawler_queue = await self.channel.queue_declare(queue_name='incrawler')
        self.outcrawler_queue = await self.channel.queue_declare(queue_name='outcrawler')
        self.database = await aiosqlite.connect("database.db")

    async def transport_to_auth(self, metadata):
        if not self.channel:
            await self.set_settings()

        await self.channel.basic_publish(
            payload=json.dumps(metadata),
            exchange_name='',
            routing_key='inbound'
        )
        self.requests[metadata.get("request_id")] = asyncio.Future()
        await self.channel.basic_consume(self.callback, queue_name='outbound', no_ack=True)

    async def transport_to_crawler(self, metadata):
        if not self.channel:
            await self.set_settings()

        await self.channel.basic_publish(
            payload=json.dumps(metadata),
            exchange_name='',
            routing_key='incrawler'
        )
        self.requests[metadata.get("request_id")] = asyncio.Future()
        await self.channel.basic_consume(self.callback, queue_name='outcrawler', no_ack=True)

    async def callback(self, channel, body, envelope, properties):
        metadata = json.loads(body)
        fut = self.requests[metadata.get("req_id")]
        fut.set_result(json.dumps(metadata.get("request_data")))

    async def signup(self, request):
        request_id = str(uuid4())

        metadata = {"request_id": request_id,
                    "request_type": "signup",
                    "request_data": await request.json()}

        await self.transport_to_auth(metadata)

        response = json.loads(await self.requests.get(request_id))
        if response.get("status") == 'ok':
            return web.Response(text=response, status=200)
        else:
            return web.Response(text=response, status=400)

    async def login(self, request):
        request_id = str(uuid4())

        metadata = {"request_id": request_id,
                    "request_type": "login",
                    "request_data": await request.json()}

        await self.transport_to_auth(metadata)

        response = json.loads(await self.requests.get(request_id))
        if response.get("status") == 'ok':
            return web.Response(text=response, status=200)
        else:
            return web.Response(text=response, status=400)

    async def current(self, request):
        request_id = str(uuid4())

        metadata = {"request_id": request_id,
                    "request_type": "validate",
                    "request_data": {"token": request.match_info.get('token')}}

        await self.transport_to_auth(metadata)

        response = json.loads(await self.requests.get(request_id))
        if response.get("status") == 'ok':
            return web.Response(text=response, status=200)
        else:
            return web.Response(text=response, status=403)

    async def search(self, request):
        request_id = str(uuid4())
        data = await request.json()
        if data.get("limit") > 100:
            data["limit"] = 100

        metadata = {"request_id": request_id,
                    "request_type": "search",
                    "request_data": data}

        await self.transport_to_crawler(metadata)

        response = json.loads(await self.requests.get(request_id))
        if response.get("status") == 'ok':
            return web.Response(text=response, status=200)
        else:
            return web.Response(text=response, status=400)

    async def stat(self, request):
        token = request.match_info['token']
        cursor = await self.database.execute(
            "SELECT email FROM User WHERE token ={}".format(token))
        row = await cursor.fetchall()
        email = row[0][0]

        cursor = self.database.execute("SELECT * FROM User_Activity WHERE email ={}".format(email))
        rows = await cursor.fetchall()
        if not rows:
            return web.Response(body=json.dumps(rows),status=200)
        else:
            return web.Response(body=json.dumps(rows),status=403)

    def index(self, request):
        request_id = str(uuid4())
        data = await request.json()
        data["token"] = request.match_info.get('token')

        metadata = {"request_id": request_id,
                    "request_type": "index",
                    "request_data": data}

        await self.transport_to_crawler(metadata)

        response = json.loads(await self.requests.get(request_id))
        if response.get("status") == 'ok':
            return web.Response(text=response, status=200)
        else:
            return web.Response(text=response, status=403)


handler = Handler()
app = web.Application()
app.add_routes([web.post('/signup', handler.signup),
                web.post('/login', handler.login),
                web.get('/current/{token}', handler.current),
                web.post('search', handler.search),
                web.post('/index/{token}', handler.index),
                web.get('/stat/{token}', handler.stat)])
web.run_app(app)
