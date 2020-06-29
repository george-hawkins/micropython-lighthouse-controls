import micropython
import gc

# Display memory available at startup.
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

import machine
import time
import select
import sys

a1n1 = machine.PWM(machine.Pin(25))
a1n2 = machine.PWM(machine.Pin(26))

# The minimum duty cycle and optimum frequency were found by experimentation.
# For the Adafruit 200RPM DC gearbox motor - https://www.adafruit.com/product/3777 - the results were:
# * The duty value needs to be 240 or above for the motor to turn.
# * At this value the motor turns fastest with a frequency of about 100Hz.
#
# You can't find the duty and frequency values independently, e.g. if you fix the frequency high and adjust
# the duty value, you'll end up with a much higher minimum duty value than if you fix the frequency low.
#
# Ideally, you'd use a quadrature encoder to measure the turning speed. I just used slow motion mode
# on my smartphone camera, captured about 5 seconds of video at various frequencies and counted the rotations.
#
# If you set the frequency very low, e.g. 10, the motor clearly judders on and off.
# So for a smooth motion it would seem obvious to set the frequency as high as possible.
# However, with the duty value at 300 the motor barely turns at a frequency above 2KHz.
# In fact the turning speed starts dropping gradually as you go above 100Hz.
# For a _possible_ explanation see the "PWM Frequency" section in
# https://www.rs-online.com/designspark/spinning-the-wheels-interfacing-pmdc-motors-to-a-microcontroller
#
# The power supply is 5V and the motors can handle up to 6V so we don't need to cap the duty value below
# the maximum allowed value of 1023.

# UART0 and UART1 are already used. UART2 is available but I always got a "Guru Meditation Error"
# after a small amount of interaction with it if I used its default pins (tx=17, rx=16). However,
# for whatever reason, everything works fine if I specify pretty much any other pins for tx and rx.
# It seems to be a known issue that the default pins can be problematic - https://github.com/micropython/micropython/issues/4997

# Misc for a simple digital pin:
#     slp = machine.Pin(27, machine.Pin.OUT)
#     slp.on()

#
# websocat ws://192.168.0.248:81
#

FREQUENCY = 100
MIN_DUTY = 240
MAX_DUTY = 1023
_DELAY = 2  # 2ms

# Note that soft-reboots don't reset PWM values.
a1n1.freq(FREQUENCY)
a1n2.freq(FREQUENCY)
a1n1.duty(0)
a1n2.duty(0)

_speed = 0
_dir = 1
_pin = a1n1
_color = bytearray(3)
_color_mv = memoryview(_color)


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


pixie = machine.UART(2, tx=27, rx=14)


def _refresh_color():
    pixie.write(bytes(_color_mv))


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
            print("Ignoring: {}".format(line))
    except Exception as e:
        sys.print_exception(e)


def prompt():
    print("$ ", end="")


poller = select.poll()
poller.register(sys.stdin, select.POLLIN)

prompt()

# The Pixie color values must be rewritten at least every 2 seconds otherwise it turns off.
# This is to prevent it getting stuck bright (and hot) if the controlling board hangs.
_REFRESH_DELAY = 1  # 1s

from schedule import Scheduler

_schedule = Scheduler()

_schedule.every(_REFRESH_DELAY).seconds.do(_refresh_color)

import socket
import websocket
import websocket_helper

#_LISTEN_MAX = 255
#
#server_socket = socket.socket()
#
#server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#server_socket.bind(("", 81))
#server_socket.listen(_LISTEN_MAX)
#
#poller.register(
#    server_socket, select.POLLIN | select.POLLERR | select.POLLHUP
#)

clients = {}

# ----------------------------------------------------------------------

from slim.slim_server import SlimServer
from slim.web_route_module import WebRouteModule, RegisteredRoute, HttpMethod

import urequests as requests  # For some reason urequests isn't available directly as requests.

slim_server = SlimServer(poller)

def request_index(request):
    r = requests.get("https://george-hawkins.github.io/material-lighthouse-controls/")
    request.Response.ReturnOk(r.text)
    r.close()

from hashlib import sha1
from binascii import b2a_base64

WS_SPEC_GUID = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"  # See https://stackoverflow.com/a/13456048/245602

class DummySocket:
    def close(self):
        pass

def register(client_socket):
    ws = websocket.websocket(client_socket, True)
    # poller.register doesn't complain if you register ws but it fails when you call ipoll.
    poller.register(client_socket, select.POLLIN)
    clients[client_socket.fileno()] = ws

# Called once the response has been sent.
def onDataSent(xasCli, _):
    register(xasCli._socket)
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
        if s == sys.stdin:
            line = sys.stdin.readline()
            print(line)
            process(line)
            prompt()
#        elif s == server_socket:
#            if event == select.POLLIN:
#                client_socket, client_addr = server_socket.accept()
#                print("Received connection from {}".format(client_addr))
#                websocket_helper.server_handshake(client_socket)
#                ws = websocket.websocket(client_socket, True)
#                print(dir(ws))
#                # poller.register doesn't complain if you register ws but it fails when you call ipoll.
#                poller.register(client_socket, select.POLLIN)
#                clients[client_socket.fileno()] = ws
#            else:
#                print("Got {} event on server socket".format(event))
        elif isinstance(s, socket.socket) and s.fileno() in clients:
            ws = clients[s.fileno()]
            line = ws.readline().decode("utf-8")
            print(line)
            process(line)
        else:
            slim_server.pump(s, event)
    slim_server.pump_expire()
    _schedule.run_pending()
