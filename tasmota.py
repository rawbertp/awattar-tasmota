import logging
from awattar import get_results
import datetime
import requests
import urllib.parse
import json
import os
import sys

# Configure the logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

TASMOTA_WEB_USER = os.environ["TASMOTA_WEB_USER"]
TASMOTA_WEB_PASSWORD = os.environ["TASMOTA_WEB_PASS"]
TASMOTA_HOST = os.environ["TASMOTA_HOST"]
TASMOTA_WEB_BASE_URL = (
    f"http://{TASMOTA_HOST}/cm?user={TASMOTA_WEB_USER}&password={TASMOTA_WEB_PASSWORD}"
)

SLOT_HOURS = int(os.environ.get("SLOT_HOURS", "5"))

ALWAYS_ENABLE = False

logger.info("Fetching slot results...")
slot = get_results([SLOT_HOURS])

start_time = datetime.datetime.strptime(slot[0][1][0], "%Y-%m-%d %H:%M:%S")
end_time = start_time + datetime.timedelta(hours=SLOT_HOURS)

if start_time.hour >= end_time.hour:
    logger.error("Start and end time are not on the same day - this is currently not supported!")
    start_hrs_str = "00:00"
else:
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
    logger.info("Updating timer 1...")
    logger.debug(f"Timer 1 data: {timer_1_data}")
    response = requests.get(timer_1_url)
    response.raise_for_status()
    logger.info("Timer 1 update OK!")

    logger.info("Updating timer 2...")
    logger.debug(f"Timer 2 data: {timer_2_data}")
    response = requests.get(timer_2_url)
    response.raise_for_status()
    logger.info("Timer 2 update OK!")

    # check if power should be on or off

    # Get the current hour
    current_hour = datetime.datetime.now().hour

    if end_time.hour < current_hour:
        logger.info("Current hour is greater than end time, powering off!")
        power_url = f"{TASMOTA_WEB_BASE_URL}&cmnd=Power1%20Off"
    elif start_time.hour <= current_hour and end_time.hour > current_hour:
        logger.info("Current hour is between start and end time, powering on!")
        power_url = f"{TASMOTA_WEB_BASE_URL}&cmnd=Power1%20On"
    else:
        logger.info("Current hour is outside of start and end time, powering off!")
        power_url = f"{TASMOTA_WEB_BASE_URL}&cmnd=Power1%20Off"

    logger.info("Updating power state...")
    logger.debug(f"Power URL: {power_url}")
    response = requests.get(power_url)
    response.raise_for_status()
    logger.info("Power state update OK!")

    logger.info("Getting power state...")
    response = requests.get(f"{TASMOTA_WEB_BASE_URL}&cmnd=Power")
    response.raise_for_status()
    power_state = response.json().get("POWER")
    logger.info(f"Power state: {power_state}")

except Exception as e:
    logger.error("Timer updates FAILED!", exc_info=True)
    sys.exit(1)
