from awattar import get_results
import datetime
import requests
import urllib.parse
import json
import os
import sys

TASMOTA_WEB_USER = os.environ["TASMOTA_WEB_USER"]
TASMOTA_WEB_PASSWORD = os.environ["TASMOTA_WEB_PASS"]
TASMOTA_HOST = os.environ["TASMOTA_HOST"]
TASMOTA_WEB_BASE_URL = (
    f"http://{TASMOTA_HOST}/cm?user={TASMOTA_WEB_USER}&password={TASMOTA_WEB_PASSWORD}"
)

SLOT_HOURS = int(os.environ.get("SLOT_HOURS", "5"))

ALWAYS_ENABLE = False

slot = get_results([SLOT_HOURS])

start_time = datetime.datetime.strptime(slot[0][1][0], "%Y-%m-%d %H:%M:%S")
end_time = start_time + datetime.timedelta(hours=SLOT_HOURS)

if start_time.hour >= end_time.hour:
    print(f"It looks like start and end time are not on the same day - this is currently not supported yet!")
    sys.exit(1)

start_hrs_str = datetime.datetime.strftime(start_time, "%H:%M")
end_hrs_str = datetime.datetime.strftime(end_time, "%H:%M")

timer_1_url = f"{TASMOTA_WEB_BASE_URL}&cmnd=Timer1"
timer_2_url = f"{TASMOTA_WEB_BASE_URL}&cmnd=Timer2"

timer_data = {
    "Mode": 0,
    "Window": 0,
    "Days": "1111111",
    "Repeat": 1,
    "Output": 1,
}

if ALWAYS_ENABLE:
    timer_data["Enable"] = 1

timer_1_data = {
    "Time": start_hrs_str,
    "Action": 1,
} | timer_data


timer_2_data = {
    "Time": end_hrs_str,
    "Action": 0,
} | timer_data


timer_1_url += urllib.parse.quote(json.dumps(timer_1_data))
timer_2_url += urllib.parse.quote(json.dumps(timer_2_data))

try:
    print("Updating timer 1...", timer_1_data)
    response = requests.get(timer_1_url)
    response.raise_for_status()

    print("Timer 1 update OK!")

    print("Updating timer 2...", timer_2_data)
    response = requests.get(timer_2_url)
    response.raise_for_status()

    print("Timer 2 update OK!")

except Exception as e:
    print("Timer updates FAILED!")
    sys.exit(1)
