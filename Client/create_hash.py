import usb.core
import hashlib

def obtain_hardware():
    devices = []
    usbs = usb.core.find(find_all=True)
    # Map all found USB's & store them in a list
    for found_usb in usbs:
        result = str(found_usb.idVendor) + str(found_usb.idProduct)
        devices.append(result)
    return devices

# Create the checksum of all the found USB's and the
# secret file
def create_checksum(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    devices = obtain_hardware()
    for device in devices:
        hash_md5.update(device.encode('utf-8'))
    return hash_md5.hexdigest()


if __name__ == "__main__":
   print(create_checksum("Client/supersecret/permission.json"))