import asyncio
import websockets
import json
import hashlib
from Cryptodome.Cipher import AES
import base64
import usb.core
import argparse

# Global variables, used in multiple functions

# To-be-verified 'snapshots'
checks = []
# ALl the running jobs
jobs = []
connected = False
erasmus = True
# (Not so) private key, change this for production
key = b"918005185E36C9888E262165401C812F"

# Function to obtain the USB vendor + device ID to generate an unique ID
async def obtain_hardware():
    devices = []
    usbs = usb.core.find(find_all=True)
    # Map all found USB's & store them in a list
    for found_usb in usbs:
        result = str(found_usb.idVendor) + str(found_usb.idProduct)
        devices.append(result)
    return devices

# Create the checksum of all the found USB's and the
# secret file
async def create_checksum(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    devices = await obtain_hardware()
    for device in devices:
        hash_md5.update(device.encode('utf-8'))
    return hash_md5.hexdigest()

async def generate_checksums():
    if not erasmus:
        return
    while connected:
        checks.append(await create_checksum("supersecret/permission.json"))
        await asyncio.sleep(1)

# Encrypt the data using AES
async def encrypt_data(data):
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(bytes(data, 'utf-8'))
    send_data = cipher.nonce + tag + ciphertext
    return send_data

async def generate_erasmus_response():
    num_of_checks = len(checks)
    res = {
        "type": "prove",
        "num_of_checks": num_of_checks
    }
    for i in range(0, num_of_checks):
        hash = checks[i]
        encrypted_data = await encrypt_data(hash)
        encoded = base64.b64encode(encrypted_data)
        res[str(i)] = encoded.decode('ascii')
    checks.clear()
    return json.dumps(res)

async def generate_original_response():
    current_md5_checksum = await create_checksum("supersecret/permission.json")
    encrypted_data = await encrypt_data(current_md5_checksum)
    encoded = base64.b64encode(encrypted_data)
    res = {
        "type": "prove",
        "num_of_checks": 1,
        "0": encoded.decode('ascii')
    }
    return json.dumps(res)

async def handler(websocket):
    global connected
    async for message in websocket:
        msg = json.loads(message)
        if (msg["type"] == "request"):
            print("* Received verify request from server")
            if (erasmus):
                json_object = await generate_erasmus_response()
            else:
                json_object = await generate_original_response()
            await websocket.send(json_object)
        elif (msg["type"] == "abort"):
            print("* Abort message received -- cancel program!")
            await websocket.close()
            connected = False
            return
        else:
            print("* Succeed message received -- keep running")


async def connect_to_server(host, port):
    global connected
    global erasmus
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--erasmus", action=argparse.BooleanOptionalAction, default=True, help="ERASMUS or 'simple' mode")
    args = parser.parse_args()
    erasmus = args.erasmus
    url = "ws://" + host + ":" + str(port)
    async with websockets.connect(url) as ws:
        connected = True
        print("* Start connection on ", url)
        data = {"type": "init", "data": "clientid"}
        json_data = json.dumps(data)
        global jobs
        jobs = [
            ws.send(json_data),
            handler(ws),
            generate_checksums()
        ]
        await asyncio.gather(*jobs)


if __name__ == "__main__":
    asyncio.run(connect_to_server("localhost", 5555))
