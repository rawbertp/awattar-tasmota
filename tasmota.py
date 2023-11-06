from awattar import get_results
import datetime
import requests
import urllib.parse
import json
import os

TASMOTA_WEB_USER = os.environ["TASMOTA_WEB_USER"]
TASMOTA_WEB_PASSWORD = os.environ["TASMOTA_WEB_PASS"]
TASMOTA_HOST = os.environ["TASMOTA_HOST"]
TASMOTA_WEB_BASE_URL = (
    f"http://{TASMOTA_HOST}/cm?user={TASMOTA_WEB_USER}&password={TASMOTA_WEB_PASSWORD}"
)

SLOT_HOURS = int(os.environ.get("SLOT_HOURS", "5"))

slot = get_results([SLOT_HOURS])

start_time = datetime.datetime.strptime(slot[0][1][0], "%Y-%m-%d %H:%M:%S")
end_time = start_time + datetime.timedelta(hours=SLOT_HOURS)

start_hrs_str = datetime.datetime.strftime(start_time, "%H:%M")
end_hrs_str = datetime.datetime.strftime(end_time, "%H:%M")

timer_1_url = f"{TASMOTA_WEB_BASE_URL}&cmnd=Timer1"
timer_2_url = f"{TASMOTA_WEB_BASE_URL}&cmnd=Timer2"

timer_1_data = {
    "Enable": 1,
    "Mode": 0,
    "Time": start_hrs_str,
    "Window": 0,
    "Days": "1111111",
    "Repeat": 1,
    "Output": 1,
    "Action": 1,
}
timer_2_data = {
    "Enable": 1,
    "Mode": 0,
    "Time": end_hrs_str,
    "Window": 0,
    "Days": "1111111",
    "Repeat": 1,
    "Output": 1,
    "Action": 0,
}


timer_1_url += urllib.parse.quote(json.dumps(timer_1_data))
timer_2_url += urllib.parse.quote(json.dumps(timer_2_data))

try:
    response = requests.get(timer_1_url)
    response.raise_for_status()

    print("Timer 1 update OK!")

    response = requests.get(timer_2_url)
    response.raise_for_status()

    print("Timer 2 update OK!")

except Exception as e:
    print("Timer updates FAILED!")
