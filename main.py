import micropython
import gc

# Display memory available at startup.
from message_extractor import Extractor

gc.collect()
micropython.mem_info()

from wifi_setup.wifi_setup import WiFiSetup

# You should give every device a unique name (to use as its access point name).
ws = WiFiSetup("ding-5cd80b3")
sta = ws.connect_or_setup()
del ws
print("WiFi is setup")

# Display memory available once the WiFi setup process is complete.
gc.collect()
micropython.mem_info()

# --------------------------------------------------------------------------------------

import logging

_logger = logging.getLogger("main")

# --------------------------------------------------------------------------------------

import machine
import time
import select
import sys

# A1N1 and A1N2 are the names of the relevant pins on the Adafruit DRV8833 motor driver breakout.
a1n1 = machine.PWM(machine.Pin(25))
a1n2 = machine.PWM(machine.Pin(26))

# See README for how `FREQUENCY` and duty values were arrived at.
FREQUENCY = 100
MIN_DUTY = 240
MAX_DUTY = 1023
_DELAY = 2  # 2ms

# Note that soft-reboots don't reset PWM values.
a1n1.freq(FREQUENCY)
a1n2.freq(FREQUENCY)
a1n1.duty(0)
a1n2.duty(0)

# --------------------------------------------------------------------------------------

_speed = 0
_dir = 1
_pin = a1n1
_color = memoryview(bytearray(3))


def _reverse():
    global _dir, _pin
    current = _speed
    _set_speed(0)
    _dir *= -1
    _pin = a1n1 if _pin == a1n2 else a1n2
    _set_speed(current)


def _speed_to_duty(speed):
    return int((MAX_DUTY - MIN_DUTY) * speed / 100 + MIN_DUTY)


# Smoothy increase or decrease from current speed to new speed rather than juddering straight one to the other.
# Changing from 0 to 100% takes about 1.5s, change _DELAY to increase or decrease this.
def _set_speed(new_speed):
    assert 0 <= new_speed <= 100
    global _speed
    current = _speed_to_duty(_speed)
    target = _speed_to_duty(new_speed)
    step = 1 if target > current else -1
    for i in range((current + step), (target + step), step):
        _pin.duty(i)
        _schedule.run_pending()  # Don't block the scheduler.
        time.sleep_ms(_DELAY)
    # If new_speed is 0 then don't leave duty at MIN_DUTY, reduce it all the way to 0.
    if new_speed == 0:
        _pin.duty(0)
    _speed = new_speed


# See README for why the default tx and rx values for UART2 are overriden.
pixie = machine.UART(2, tx=27, rx=14)


def _refresh_color():
    pixie.write(bytes(_color))


# Process user entered commands.
def process(line):
    try:
        words = line.split()
        command = words[0][0]
        if command == "s":
            _set_speed(int(words[1]))
        elif command == "r":
            _reverse()
        elif command == "c":
            global _color
            for i in range(len(_color)):
                _color[i] = int(words[i + 1])
            _refresh_color()
        else:
            # `repr` converts non-printing characters to hex escapes or '\n' etc.
            print("Ignoring: {}".format(repr(line)))
    except Exception as e:
        sys.print_exception(e)


poller = select.poll()

# The Pixie color values must be rewritten at least every 2 seconds otherwise it turns off.
# This is to prevent it getting stuck bright (and hot) if the controlling board hangs.
_REFRESH_DELAY = 1  # 1s

from schedule import Scheduler

_schedule = Scheduler()

_schedule.every(_REFRESH_DELAY).seconds.do(_refresh_color)

# ----------------------------------------------------------------------

import socket
import websocket

clients = {}

def pump_ws_clients(s, event):
    if not isinstance(s, socket.socket):
        return
    fileno = s.fileno()
    if fileno not in clients:
        return
    if event != select.POLLIN:
        _logger.warning("unexpected event {} on socket {}".format(event, fileno))
        remove_ws_client(fileno)
        return
    ws_client = clients[fileno]
    try:
        message = ws_client.nextMessage()
    except Exception as e:
        sys.print_exception(e)
        remove_ws_client(fileno)
        return
    if message:
        print(message)
        process(message)

def remove_ws_client(fileno):
    clients.pop(fileno).close(poller)

def add_ws_client(client_socket):
    ws_client = WsClient(poller, client_socket)
    clients[ws_client.fileno] = ws_client


class WsClient:
    def __init__(self, poller, client_socket):
        self._socket = client_socket
        self._ws = websocket.websocket(client_socket, True)
        self.fileno = client_socket.fileno()
        # poller.register doesn't complain if you register ws but it fails when you call ipoll.
        poller.register(client_socket, select.POLLIN | select.POLLERR | select.POLLHUP)
        self._extractor = Extractor()

    def close(self, poller):
        poller.unregister(self._socket)
        try:
            self._ws.close()
        except:
            pass

    def nextMessage(self):
        return self._extractor.consume(self._ws.readinto)


# ----------------------------------------------------------------------

from slim.slim_server import SlimServer
from slim.web_route_module import WebRouteModule, RegisteredRoute, HttpMethod

import urequests as requests  # For some reason urequests isn't available directly as requests.

slim_server = SlimServer(poller)

from os import urandom
from binascii import hexlify

def request_index(request):
    uuid = hexlify(urandom(16)).decode()
    # GitHub returns stale cached results unless we force things by appending a UUID.
    r = requests.get("https://george-hawkins.github.io/material-lighthouse-controls/?{}".format(uuid))
    request.Response.ReturnOk(r.text)
    r.close()

from hashlib import sha1
from binascii import b2a_base64

WS_SPEC_GUID = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"  # See https://stackoverflow.com/a/13456048/245602

class DummySocket:
    def close(self):
        pass

# Called once the response has been sent.
def onDataSent(xasCli, _):
    add_ws_client(xasCli._socket)
    xasCli._socket = DummySocket()
    xasCli.Close()

def request_socket(request):
    key = request.GetHeader("Sec-Websocket-Key")
    if key:
        hash = sha1(key.encode())
        hash.update(WS_SPEC_GUID)
        accept = b2a_base64(hash.digest()).decode()[:-1]
        request.Response.SetHeader("Sec-WebSocket-Accept", accept)
        request.Response.SwitchingProtocols("websocket", onDataSent)


# fmt: off
slim_server.add_module(WebRouteModule([
    RegisteredRoute(HttpMethod.GET, "/", request_index),
    RegisteredRoute(HttpMethod.GET, "/socket", request_socket)
]))
# fmt: on

# ----------------------------------------------------------------------

while True:
    for (s, event) in poller.ipoll(0):
        pump_ws_clients(s, event)
        slim_server.pump(s, event)
    slim_server.pump_expire()
    _schedule.run_pending()
