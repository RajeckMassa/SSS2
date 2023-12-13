import json
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--erasmus", action=argparse.BooleanOptionalAction, default=True,
                    help="ERASMUS or 'simple' mode")
args = parser.parse_args()
erasmus = args.erasmus

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

if not erasmus:
    exit(0)
time.sleep(2)
with open("supersecret/permission.json", "w") as f:
    f.write(standard_json_obj)
    f.close()