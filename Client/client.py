import asyncio
import websockets
import json


async def handler(websocket):
    async for message in websocket:
        msg = json.loads(message)
        print(msg)
        await websocket.send(json.dumps({"type": "prove", "data": "<prove data hier>"}))


async def connect_to_server(host, port):
    url = "ws://" + host + ":" + str(port)
    print("* Start connection on ", url)
    async with websockets.connect(url) as ws:
        data = {"type": "init", "data": "clientid"}
        json_data = json.dumps(data)
        await asyncio.gather(
            ws.send(json_data),
            handler(ws)
        )


if __name__ == "__main__":
    asyncio.run(connect_to_server("localhost", 5555))
