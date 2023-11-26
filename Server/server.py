import asyncio
import websockets
import json

# TODO's
# Next step: TLS on websocket connection, so it's secure
# Figure a way to generate a remote attestation prover thingy on the client
# Figure a way to check the generated remote attestation thingy on the server and send a 'good'/'bad' response back.

connections = set()

async def handle_prove_data(websocket):
    msg = await websocket.recv()
    json_msg = json.loads(msg)
    print(json_msg)


async def prove_request(websocket):
    data = json.dumps({"type": "request"})
    while True:
        try:
            await websocket.send(data)
            await handle_prove_data(websocket)
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
