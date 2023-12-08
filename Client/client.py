import asyncio
import websockets
import json
import hashlib
from Cryptodome.Cipher import AES
import base64


async def create_md5_from_file(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

key = b"918005185E36C9888E262165401C812F"
async def encrypt_data(data):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(bytes(data, 'utf-8'))
    send_data = cipher.nonce + tag + ciphertext
    return send_data

async def handler(websocket):
    async for message in websocket:
        msg = json.loads(message)
        print(msg)
        if (msg["type"] == "request"):
            hash = await create_md5_from_file("supersecret/permission.json")
            encrypted_data = await encrypt_data(hash)
            encoded = base64.b64encode(encrypted_data)
            json_object = json.dumps({"type": "prove", "data": encoded.decode('ascii')})
            await websocket.send(json_object)


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
