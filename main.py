import machine
import time
import select
import sys
import urequests as requests  # For some reason urequests isn't available directly as requests (MP 1.12).

from os import urandom
from binascii import hexlify

from slim.slim_server import SlimServer
from slim.web_route_module import WebRouteModule, RegisteredRoute, HttpMethod
from slim.ws_manager import WsManager
from message_extractor import Extractor
from schedule import Scheduler
from logging import getLogger
from connect import connect

# --------------------------------------------------------------------------------------

logger = getLogger("main")

connect()

# --------------------------------------------------------------------------------------

# Setup the Adafruit Pixie.

# See README for why the default tx and rx values for UART2 are overriden.
pixie = machine.UART(2, tx=27, rx=14)

color = memoryview(bytearray(3))


def refresh_color():
    pixie.write(bytes(color))


def set_color(new_color):
    assert len(new_color) == 3
    color[:] = new_color
    refresh_color()


# The Pixie color values must be rewritten at least every 2 seconds otherwise it turns off.
# This is to prevent it getting stuck bright (and hot) if the controlling board hangs.
REFRESH_DELAY = 1  # 1s

schedule = Scheduler()

schedule.every(REFRESH_DELAY).seconds.do(refresh_color)

# --------------------------------------------------------------------------------------

# Setup the A1N1 and A1N2 pins on the Adafruit DRV8833 motor driver breakout.

a1n1 = machine.PWM(machine.Pin(25))
a1n2 = machine.PWM(machine.Pin(26))

# See README for how `FREQUENCY` and duty values were arrived at.
FREQUENCY = 100
MIN_DUTY = 240

# The maximum value of 1023 is fine in terms of not exceeding the motor's maximum voltage.
# However, it's far too high a maximum speed for what's supposed to be a lighthouse.
MAX_DUTY = 255

# Note that soft-reboots don't reset PWM values.
a1n1.freq(FREQUENCY)
a1n2.freq(FREQUENCY)
a1n1.duty(0)
a1n2.duty(0)

# --------------------------------------------------------------------------------------

DELAY = 2  # 2ms

speed = 0
dir = 1
pin = a1n1

# Functions for controlling the speed and direction of the motor.


def speed_to_duty(speed):
    return int((MAX_DUTY - MIN_DUTY) * speed / 100 + MIN_DUTY)


def reverse():
    global dir, pin
    current = speed
    set_speed(0)
    dir *= -1
    pin = a1n1 if pin == a1n2 else a1n2
    set_speed(current)


# Smoothly increase or decrease from current speed to new speed rather than juddering straight one to the other.
# Changing from 0 to 100% takes about 1.5s, change _DELAY to increase or decrease this.
def set_speed(new_speed):
    assert 0 <= new_speed <= 100
    global speed
    current = speed_to_duty(speed)
    target = speed_to_duty(new_speed)
    step = 1 if target > current else -1
    for i in range((current + step), (target + step), step):
        pin.duty(i)
        schedule.run_pending()  # Don't block the scheduler.
        time.sleep_ms(DELAY)
    # If new_speed is 0 then don't leave duty at MIN_DUTY, reduce it all the way to 0.
    if new_speed == 0:
        pin.duty(0)
    speed = new_speed


# ----------------------------------------------------------------------

# Process user entered commands.
def process(line):
    try:
        words = line.split()
        command = words[0][0]
        if command == "s":
            set_speed(int(words[1]))
        elif command == "r":
            reverse()
        elif command == "c":
            set_color(bytes(map(int, words[1:4])))
        elif command == "p":
            machine.deepsleep()
        else:
            # `repr` converts non-printing characters to hex escapes or '\n' etc.
            print("Ignoring: {}".format(repr(line)))
    except Exception as e:
        sys.print_exception(e)


poller = select.poll()

extractor = Extractor()
ws_manager = WsManager(poller, extractor.consume, process)

# ----------------------------------------------------------------------

slim_server = SlimServer(poller)

ROOT_URL = "https://george-hawkins.github.io/material-lighthouse-controls/"


def request_index(request):
    uuid = hexlify(urandom(16)).decode()
    # GitHub returns stale cached results unless we force things by appending a UUID.
    r = requests.get(ROOT_URL + "?" + uuid)
    request.Response.ReturnOk(r.text)
    r.close()


# fmt: off
slim_server.add_module(WebRouteModule([
    RegisteredRoute(HttpMethod.GET, "/", request_index),
    RegisteredRoute(HttpMethod.GET, "/socket", ws_manager.upgrade_connection)
]))
# fmt: on

# ----------------------------------------------------------------------

while True:
    for (s, event) in poller.ipoll(0):
        ws_manager.pump_ws_clients(s, event)
        slim_server.pump(s, event)
    slim_server.pump_expire()
    schedule.run_pending()
