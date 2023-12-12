import asyncio
import websockets
import json
from Cryptodome.Cipher import AES
import base64
import argparse
import socket


# This code is obtained from
# https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib?page=1&tab=scoredesc#tab-top
async def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('254.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

connections = set()
# (not so) Secret AES key
# This is still included in the repo for the demo
# In production, you should never push an encryption key
# to Git, but use something like environment variables.
key = b"918005185E36C9888E262165401C812F"
# MD5 key which the client should return
md5_key = ""
time_between_verifies = 0

# Decrypt the messages
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
        print(f"Client {websocket.id} sends data to verify.")
        # Obtain the number of checks
        num = msg["num_of_checks"]
        # Loop through them, decode them, check them
        for i in range(0, num):
            encoded_encrypted_data = msg[str(i)]
            encrypted_data = base64.b64decode(encoded_encrypted_data)
            decrypted_data = await decrypt_message(encrypted_data)
            # If the key is different -> someone tempered with the hardware
            # or software, so let the program quit itself
            if decrypted_data != md5_key:
                print(f"* Tampered with client {websocket.id}! Sending abort msg")
                data = json.dumps({"type": "abort"})
                await websocket.send(data)
                return
        # If not: everything ok
        print(f"* All good on client {websocket.id}, sending succeed msg")
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
        print(f"* Client {websocket.id} disconnected.")
        connections.remove(websocket)


async def connection_handler(websocket):
    # Receive first message
    msg = await websocket.recv()
    print(f"* Client connected with id {websocket.id}. ")
    data = json.loads(msg)
    assert data["type"] == "init"
    await(register_connection(websocket))

async def main(port):
    global time_between_verifies
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--time", type=int, default=10, help="Time between verifies")
    args = parser.parse_args()
    host = await get_ip()
    time_between_verifies = args.time
    async with websockets.serve(connection_handler, host, port):
        print("* Server started on " + host + ":" + str(port))
        await asyncio.Future()

# Obtain the hash from the file
# Exception handling from
# https://stackoverflow.com/questions/713794/catching-an-exception-while-using-a-python-with-statement
def obtain_hash():
    global md5_key
    try:
        hash_file = open("hash.txt", 'r')
    except FileNotFoundError:
        raise Exception("Please create the hash.txt file first.")
    else:
        with hash_file:
            md5_key = hash_file.readline().strip()
            hash_file.close()

if __name__ == "__main__":
    obtain_hash()
    asyncio.run(main(5555))
