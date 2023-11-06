# awattar-tasmota

## Overview

Very basic and poorly written lines of code to...

a. fetch the prices from the awattar API --> `awattar.py`
b. configure Tasmota timers (ON/OFF) --> `tasmota.py`

The simple idea behind is:

- Get the cheapest slot of x (e.g. 5) hours, e.g. to turn on the boiler.
- Update the Tasmota timers 1 (ON) and 2 (OFF) based on the results.

## Usage

To get the cheapest timeslots of 1...5 hours:

```python
python awattar.py
```

To get the cheapest timeslot of x (e.g. 7) hours:

```python
python awattar.py 7
```

For the use of `tasmota.py` the following environment variables need to be set:

- `TASMOTA_HOST`: e.g. "192.168.1.10" or "192.168.1.10:8888"
- `TASMOTA_WEB_USER`
- `TASMOTA_WEB_PASS`
- `SLOT_HOURS` (optional): slot size in hours (default = 5)

The script will then update timers 1 and 2 based on the results of the
`awattar.py` script.

## ToDo

- Error handling.
- Optional web interface credentials.

