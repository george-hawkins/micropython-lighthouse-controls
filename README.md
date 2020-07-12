MicroPython lighthouse controls
===============================

Basic setup
-----------

Clone this repo and the micropython-wifi-setup repo and link to its `lib` directory:

    $ git clone git@github.com:george-hawkins/micropython-wifi-setup.git
    $ git clone git@github.com:george-hawkins/micropython-lighthouse-controls.git
    $ cd micropython-lighthouse-controls
    $ ln -s ../micropython-wifi-setup/lib .

Then create a Python venv and install [`rshell`](https://github.com/dhylands/rshell):

    $ python3 -m venv env
    $ source env/bin/activate
    $ pip install --upgrade pip
    $ pip install rshell

---

`avahi-resolve` vs `dig -p 5353 @224.0.0.251` Server Fault question: <https://serverfault.com/q/1023994/282515>


    $ avahi-resolve --name ding-5cd80b3.local
    ding-5cd80b3.local  192.168.0.248

    $ dig +short -p 5353 @224.0.0.251 ding-5cd80b3.local
    ;; Warning: ID mismatch: expected ID 60466, got 0

I managed to block both the mounting holes on the perma-proto.

For the ESP32 end I'd have had to put in a bolt before I soldered down the ESP32. For the driver end I should have moved the driver in 3 holes (though this would have made the wiring quite tight).

Mention that I added a "magic" cap on the driver power-in pins that isn't shown in the Fritzing diagram.

I used 18AWG wire for the Pixie by mistake, although the terminal blocks are advertised as being suitable for 30-16AWG, its actually tricky to get even 18AWG wire into the holes of the terminal block. 20AWG would be perfect and more than enough for the 1A of a single Pixie.

At full power the Pixie heats up very quickly and the temperature cut-off kicks in (as it should). However, such a limited running time at maximum brightness makes the Pixie a little pointless (why have a 3W LED if you have to run it at lower power?).

Maybe, using thermally conductive silicone to conect it to the metal support would solve this issue:

* <https://www.banggood.com/100mmx100mmx5mm-GPU-CPU-Heatsink-Cooler-Blue-Thermal-Conductive-Silicone-Pad-p-989163.html>
* <https://www.digitec.ch/de/s1/product/arctic-waermeleitpad-1-mm-6-wmk-l-x-aktive-bauelemente-8491056>

Note that 1mm thickness seems to be the norm, the 5mm thickness from Banggod is unusual. No one actually seems to have this kind of thing in stock at the moment (possibly due to COVID-19 related shipping issues).

Given the Pixies exposed components, you obviously want a terminally conductive material that is _not_ electrically conductive.

The blindingly bright red LED of the DevKitC board can be blocked with with a small black-out edition LightDim shape (see [here](https://www.lightdims.com/store.htm)), I find them far more effective than e.g. black duct tape.

The Adafruit [TT motor](https://www.adafruit.com/product/3777) has a gear ratio of 1:48. Even at minimum speed it still turns quite quickly.

Pololu offer similar motors with more appropriate gear ratios (no-load current shown in brackets):

* 120:1 (80mA) <https://www.pololu.com/product/1124>
* 120:1 (130mA) <https://www.pololu.com/product/1511>
* 180:1 (80mA) <https://www.pololu.com/product/1593>
* 200:1 (70mA) <https://www.pololu.com/product/1120> (near idential in style to the the Adafruit motor).

Maybe, a pulldown resistor on the Pixie data wire and direct control of the SLP pin on the driver by the ESP32 (also with pulldown resistor) would have been a good idea for a defined state when the ESP32 itself is turned off.

TODO
----

Buy 2 x https://www.reichelt.com/ch/de/raspberry-pi-kabel-mit-schalter-30-cm-schwarz-rpi-cable-sw-30-p223610.html
And another power adapter.

Tining wires
------------

The power wires are tinned on the ends that are soldered into the Pixie. They are *not* tinned on the ends that are inserted into the screw terminal block. It may seem convenient to tin the ends to stop the wire strands splaying out but for a clear explanation of why this is a bad idea, see [this](https://electronics.stackexchange.com/a/29862/27099) Electronics StackExchange answer and [this](https://reprap.org/wiki/Wire_termination_for_screw_terminals) RepRap wiki entry on the topic.

Websocket closure
-----------------

Surprisingly, the Angular web UI doesn't typically become aware of the remote end closing the websocket connection or at least it takes it a long time to notice. I added a heartbeat in the hope that actively trying to push data would trigger the lower level logic to notice any disconnect quicker but this didn't improve things.

Instead of using `openObserver` and `closeObserver` with the RxJS `webSocket` function, I should move to having both sides sending a heartbeat and treat the failure to receive such heartbeats as a disconnect.

Motor frequency and duty values
-------------------------------

The power supply is 5V and the motors can handle up to 6V so we don't need to cap the duty value below the maximum allowed value of 1023.

The minimum duty cycle and optimum frequency were found by experimentation. For the Adafruit 200RPM [DC gearbox motor](https://www.adafruit.com/product/3777) - the results were:

* The duty value needs to be 240 or above for the motor to turn.
* At this value the motor turns fastest with a frequency of about 100Hz.

You can't find the duty and frequency values independently, e.g. if you fix the frequency high and adjust the duty value, you'll end up with a much higher minimum duty value than if you fix the frequency low.

Ideally, you'd use a quadrature encoder to measure the turning speed. I just used slow motion mode on my smartphone camera, captured about 5 seconds of video at various frequencies and counted the rotations.

If you set the frequency very low, e.g. 10, the motor clearly judders on and off. So for a smooth motion it would seem obvious to set the frequency as high as possible. However, with the duty value at 300 the motor barely turns at a frequency above 2KHz. In fact the turning speed starts dropping gradually as you go above 100Hz.

The "PWM Frequency" section of this [DesignSpark article](https://www.rs-online.com/designspark/spinning-the-wheels-interfacing-pmdc-motors-to-a-microcontroller) includes a _possible_ explanation:

> One explanation may be that the very narrow pulses of a high-frequency signal are just not long enough to ‘kick’ the rotor into action.

I've asked about this [here](https://electronics.stackexchange.com/q/509426/27099) on the Electronics StackExchange.

UART pins
---------

UART0 and UART1 are already used. UART2 is available but I always got a [Guru Meditation Error](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/fatal-errors.html#guru-meditation-errors) after a small amount of interaction with it if I used its default pins (tx=17, rx=16). However, for whatever reason, everything works fine if I specify pretty much any other pins for tx and rx.

It seems to be a known issue that the default pins can be problematic, see MicroPython issue [#4997](https://github.com/micropython/micropython/issues/4997).

Note: one UART is definitely used for the UART to USB bridge but it may be that UART1 is also available and, like UART2, it's simply that its default pins are an issue - but I haven't investigated this.

I chose pins 27 and 14 (which despite their numbers are beside each other on the board) for no particular. As I'm doing no receiving I've actually just left 14 floating but it might have been better to connect it to a pull-down resistor.

Note: when you initialize a UART, the ESP32 often (but not always) outputs a console message like this:

    I (7336) uart: ALREADY NULL

This sounds like an error but appears to be of no particular importance.

GitHub caching
--------------

The UI is actually hosted on GitHub, the root page is retrieved in MicroPython and served out so that it appears to come from the device.

All modern browsers accept gzipped data but the request made by MicroPython does not - this shows up something odd in how GitHub caches request responses.

If you accept gzipped data you quickly see any changes made to the hosted data on GitHub. However, if you do not GitHub continues to serve out stale cached data long after the underlying data has changed.

If you use `-v` with `curl` and switch between using `--compressed` and omitting it, you can clearly see the different cache related headers between the two situations.

I suspect this is some kind of bug on GitHub's part rather than a deliberate attempt to punish anyone requesting uncompressed data.

To get around this a query string with a UUID value is included in each request to bypass the caching.

Misc
----

To set a simple digital pin high:

    slp = machine.Pin(27, machine.Pin.OUT)
    slp.on()

For websocket experimentation, I used [`websocat`](https://github.com/vi/websocat):

    $ websocat ws://192.168.0.248/socket

Or:

    $ websocat ws://ding-5cd80b3.local/socket

Black and flake8
----------------

`black` and `flake8` are used as following with the Python files in this project:

    $ black *.py
    $ flake8 *.py | fgrep -v -e E501 -e E203

Note: `E501` and `E203` are simply rules that `black` and `flake8` disagree on.
