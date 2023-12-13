import asyncio
import websockets
import json
import hashlib
from Cryptodome.Cipher import AES
import base64
import os

checks = []
checkdata = []

async def create_md5_from_file(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

async def generate_checksums():
    path = os.path.dirname(os.path.realpath(__file__));
    path += "/supersecret/permission.json";
    while True:
        #checks.append(await create_md5_from_file(path))
        check = await create_md5_from_file(path);
        checks.append(check)
        checkdata.append(await encrypt_data(check))
        await asyncio.sleep(1)

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
            num_of_checks = len(checks)
            res = {
                "type": "prove",
                "num_of_checks": num_of_checks
            }
            for i in range(0, num_of_checks):
                #hash = checks[i]
                #encrypted_data = await encrypt_data(hash)
                encrypted_data = checkdata[i]
                encoded = base64.b64encode(encrypted_data)
                res[str(i)] = encoded.decode('ascii')
            checks.clear()
            checkdata.clear()
            json_object = json.dumps(res)
            await websocket.send(json_object)
        elif (msg["type"] == "abort"):
            print("* Abort message received -- cancel program!")
            await websocket.close()
            exit(0)


async def connect_to_server(host, port):
    url = "ws://" + host + ":" + str(port)
    print("* Start connection on ", url)
    async with websockets.connect(url) as ws:
        data = {"type": "init", "data": "clientid"}
        json_data = json.dumps(data)
        await asyncio.gather(
            ws.send(json_data),
            handler(ws),
            generate_checksums()
        )
        print("a?")


if __name__ == "__main__":
    asyncio.run(connect_to_server("localhost", 5555))
