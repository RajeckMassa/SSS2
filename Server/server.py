import asyncio
import websockets
import json
from Cryptodome.Cipher import AES
import base64
import argparse


connections = set()
key = b"918005185E36C9888E262165401C812F"
md5_key = "6f498c561258ca2185bea1fbc5eb43ed"
time_between_verifies = 0

async def decrypt_message(encrypted_message):
    nonce = encrypted_message[:16]
    tag = encrypted_message[16:32]
    msg = encrypted_message[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    data = cipher.decrypt_and_verify(msg, tag)

    return data.decode()

async def handle_prove_data(websocket):
    msg = json.loads(await websocket.recv())
    if msg["type"] == "prove":
        num = msg["num_of_checks"]
        for i in range(0, num):
            encoded_encrypted_data = msg[str(i)]
            encrypted_data = base64.b64decode(encoded_encrypted_data)
            decrypted_data = await decrypt_message(encrypted_data)
            if decrypted_data != md5_key:
                print(f"* Tampered with client {websocket.id}! Sending abort msg")
                data = json.dumps({"type": "abort"})
                await websocket.send(data)
                return
        print("* All good, sending succeed msg")
        data = json.dumps({"type": "succeed"})
        await websocket.send(data)




async def prove_request(websocket):
    while True:
        try:
            data = json.dumps({"type": "request"})
            await websocket.send(data)
            await handle_prove_data(websocket)
            await asyncio.sleep(time_between_verifies)
        except websockets.ConnectionClosed:
            break


async def register_connection(websocket):
    connections.add(websocket)
    try:
        await prove_request(websocket)
    finally:
        print("* Client disconnected.")
        connections.remove(websocket)


async def connection_handler(websocket):
    # Receive first message
    msg = await websocket.recv()
    print("* Client connected. ")
    data = json.loads(msg)
    assert data["type"] == "init"
    await(register_connection(websocket))

async def main(host, port):
    global time_between_verifies
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--time", type=int, default=10, help="Time between verifies")
    args = parser.parse_args()
    time_between_verifies = args.time
    async with websockets.serve(connection_handler, host, port):
        print("* Server started on " + host + ":" + str(port))
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main("localhost", 5555))
