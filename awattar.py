import requests
import sys
import time
from time import strftime, localtime
from datetime import datetime, timedelta

AWATTAR_RATE = 1.03
VAT = 1.20


def get_prices():
    now = datetime.now()
    tomorrow = now + timedelta(days=2)
    epoch_seconds = int(time.mktime(tomorrow.timetuple())) * 1000
    start_epoch_seconds = int(time.mktime(now.timetuple())) * 1000

    url = f"https://api.awattar.at/v1/marketdata?start={start_epoch_seconds}&end={epoch_seconds}"

    response = requests.get(url)

    response.raise_for_status()

    price_data = response.json()["data"]

    hourly_price_list = []

    for it in price_data:
        start = strftime("%Y-%m-%d %H:%M:%S", localtime(it["start_timestamp"] / 1000))
        end = strftime("%Y-%m-%d %H:%M:%S", localtime(it["end_timestamp"] / 1000))
        market_price = it["marketprice"]
        price = round(market_price * AWATTAR_RATE * VAT / 1000 * 100, 2)
        hourly_price_list.append((start, end, price))

    return hourly_price_list


def find_cheapest_slots(hourly_price_list, slot_hrs):
    results = []

    for slot in slot_hrs:
        intervals = []
        for i in range(0, len(hourly_price_list) - slot + 1):
            interval_start = hourly_price_list[i][0]
            interval_price_total = round(
                sum([x[2] for x in hourly_price_list[i : i + slot]]) / slot, 2
            )
            intervals.append((interval_start, interval_price_total))

        intervals.sort(key=lambda x: x[1])
        results.append((slot, intervals[0]))

    return results


def get_results(slots):
    hourly_price_list = get_prices()
    return find_cheapest_slots(hourly_price_list, slots)


def main():
    slots = [1, 2, 3, 4, 5]

    if len(sys.argv) == 2:
        slots = [int(sys.argv[1])]

    for r in get_results(slots):
        print(f"Cheapest slot for {r[0]} hours starts at {r[1][0]}. Average price/kWh: {r[1][1]} ct.")

if __name__ == "__main__":
    main()
