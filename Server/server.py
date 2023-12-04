import asyncio
import websockets
import json
import secrets
import hashlib
import os

# TODO's
# Next step: TLS on websocket connection, so it's secure
# Figure a way to generate a remote attestation prover thingy on the client
# Figure a way to check the generated remote attestation thingy on the server and send a 'good'/'bad' response back.

connections = set()


def calculate_hash():
    # https://stackoverflow.com/questions/22058048/hashing-a-file-in-python
    hash = hashlib.new('sha256')
    buffsize = 65536
    with open(os.path.dirname(os.path.realpath(__file__))+"/client.py", "rb") as file:
        while True:
            data = file.read(buffsize)
            if not data:
                break
            hash.update(data)
    return hash.hexdigest()

async def handle_prove_data(websocket, challenge, digest):
    msg = await websocket.recv()
    json_msg = json.loads(msg)
    if (json_msg["type"] == "prove"):
        print("Challenge comparison: {}".format(json_msg["challenge"]==challenge))
        print("Digest comparison: {}".format(secrets.compare_digest(digest, json_msg["digest"])))


async def prove_request(websocket):
    while True:
        try:
            challenge = secrets.randbits(8)
            data = json.dumps({"type": "request", "challenge" : challenge})
            await websocket.send(data)
            await handle_prove_data(websocket, challenge, calculate_hash())
            await asyncio.sleep(10)
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
    print("* Server started on " + host + ":" + str(port))
    async with websockets.serve(connection_handler, host, port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main("localhost", 5555))
