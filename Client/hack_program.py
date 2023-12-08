import json
import time

standard_json = {
    "permissions": "user"
}

admin_json = {
    "permissions": "admin"
}

standard_json_obj = json.dumps(standard_json)
admin_json_obj = json.dumps(admin_json)

with open("supersecret/permission.json", "w") as f:
    f.write(admin_json_obj)
    f.close()

time.sleep(2)
with open("supersecret/permission.json", "w") as f:
    f.write(standard_json_obj)
    f.close()