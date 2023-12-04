import asyncio
import websockets
import json
import hashlib
import os

def calculate_hash():
    # https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
    hash = hashlib.new('sha256')
    buffsize = 65536
    with open(os.path.realpath(__file__), "rb") as file:
        while True:
            data = file.read(buffsize)
            if not data:
                break
            hash.update(data)
    return hash.hexdigest()

async def handler(websocket):
    async for message in websocket:
        msg = json.loads(message)
        print(msg)
        if (msg["type"] == "request"):
            await websocket.send(json.dumps({"type": "prove", "data": "<prove data hier>", "challenge": msg["challenge"], "digest": calculate_hash()}))


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
