NOTES
=====

This page contains miscellaneous notes that were accumulated in the process of creating this project.

Thermal cut-off
---------------

At full brightness, the Pixie heats up very quickly and the temperature cut-off kicks in (as it should). However, such a limited running time at maximum brightness makes the Pixie a little pointless, i.e. why have a 3W LED if you have to run it at lower power? Maybe, using a thermally conductive pad to connect it to the metal frame would solve this issue:

* Banggood 5mm thick [thermal pad](https://www.banggood.com/100mmx100mmx5mm-GPU-CPU-Heatsink-Cooler-Blue-Thermal-Conductive-Silicone-Pad-p-989163.html).
* Arctic 1mm thick [thermal pad](https://www.arctic.ac/ch_en/thermal-pad.html).

Note that 1mm thickness seems to be the norm, the 5mm thickness from Banggod is unusual. No one actually seems to have this kind of thing in stock at the moment (possibly due to COVID-19 related shipping issues).

Given the Pixies exposed components, you obviously want a terminally conductive material that is _not_ electrically conductive.

Tining wires
------------

The power wires are tinned on the ends that are soldered into the Pixie. They are **not** tinned on the ends that are inserted into the screw terminal block. It may seem convenient to tin the ends to stop the wire strands splaying out but for a clear explanation of why this is a bad idea, see [this](https://electronics.stackexchange.com/a/29862/27099) Electronics StackExchange answer and [this](https://reprap.org/wiki/Wire_termination_for_screw_terminals) RepRap wiki entry on the topic.

mDNS
----

It would be nice if we could use [mDNS](https://en.wikipedia.org/wiki/Multicast_DNS) and indeed MicroPython supports advertising the device name via mDNS (and I take advantage of that support). However, at the moment there is a bug in the ESP-IDF mDNS functionality that means that some systems will reject the ESP-IDF generated mDNS responses. For more details see ESP-IDF bug [#5574](https://github.com/espressif/esp-idf/issues/5574) (I've also commented about this on MicroPython issue [#4912](https://github.com/micropython/micropython/issues/4912) that covered adding the necessary mDNS support to MicroPython).

LightDims
---------

The blindingly bright red LED of the DevKitC board can be blocked with a small black-out edition LightDim shape (see [here](https://www.lightdims.com/store.htm)), I find them far more effective than e.g. black duct tape.

Websocket closure
-----------------

The Angular web UI doesn't typically become aware of the remote end, of the websocket connection, disappearing (or at least it takes it a long time to notice). I added a heartbeat in the hope that actively trying to push data would trigger the lower level logic to notice any disconnect quicker but this didn't improve things. If I look at the sockets involved, I see that they remain in `ESTABLISHED` state even if the remote device has been completely switched off:

    $ sudo netstat -nap | fgrep 192.168.0.248
    tcp        0   2048 192.168.0.241:45774     192.168.0.248:80        ESTABLISHED 3884/chrome --type=

Here, 192.168.0.248 is the address of the switched-off remote device. I'd expected to see the socket stuck in `FIN_WAIT1` state (a common issue when the remote end disappears without having had a chance to close its connections properly) but it doesn't seem to have even got that far - the system remains unaware that anything untoward has happened.

Instead of using `openObserver` and `closeObserver`, with the RxJS `webSocket` function, to track opening and closing, I should move to having both sides sending a heartbeat and treat the failure to receive such heartbeats as a disconnect.

Motor frequency and duty values
-------------------------------

The power supply is 5V and the motors can handle up to 6V so, when driving the motor, we don't need to cap the duty value below the maximum allowed value of 1023.

The minimum duty cycle and optimum frequency were found by experimentation. For the Adafruit 1:48 [DC gearbox motor](https://www.adafruit.com/product/3777), the results were:

* The duty value needs to be 240 or above for the motor to turn.
* At this value, the motor turns fastest with a frequency of about 100Hz.

You can't find the duty and frequency values independently, e.g. if you fix the frequency high and adjust the duty value, you'll end up with a much higher minimum duty value than if you fix the frequency low.

Ideally, you'd use a quadrature encoder to measure the turning speed. I just used slow-motion mode on my smartphone camera, captured about 5 seconds of video at various frequencies and counted the rotations.

If you set the frequency very low, e.g. 10, the motor clearly judders on and off. So for a smooth motion, it would seem obvious to set the frequency as high as possible. However, with the duty value at 300, the motor barely turns at a frequency above 2KHz. In fact, the turning speed starts dropping gradually as you go above 100Hz.

The "PWM Frequency" section of this [DesignSpark article](https://www.rs-online.com/designspark/spinning-the-wheels-interfacing-pmdc-motors-to-a-microcontroller) includes a _possible_ explanation:

> One explanation may be that the very narrow pulses of a high-frequency signal are just not long enough to 'kick' the rotor into action.

I've asked about this [here](https://electronics.stackexchange.com/q/509426/27099) on the Electronics StackExchange.

Changing motor direction
------------------------

When you press _Reverse_ in the web interface, the code in [`main.py`](../main.py) slows the motor to a stop and then speeds it back up in the opposite direction. This not only prevents a sudden jolt, in going immediately from a given speed in one direction to going the same speed in the opposite direction, it also prevents a sudden jump in the current drawn by the motor which _could_ otherwise be up to 20 times the normal free-running current consumption. For more details see the "Motor Considerations" section of this [Pololu page](https://www.pololu.com/docs/0J44/4.1) on motor controllers.

UART pins
---------

UART0 is used for the UART-to-USB bridge but UART1 and UART2 are available. However, I always got a [guru meditation error](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/fatal-errors.html#guru-meditation-errors) after a small amount of interaction with either if I used their default pins (rx=9 and tx=10 for UART1 and rx=16 and tx=17 for UART2).

For whatever reason, everything works fine if I specify pretty much any other pins for tx and rx (it's a nice feature of the ESP32 that the UART pins are not fixed).

It seems to be a known issue that the default pins can be problematic, see MicroPython issue [#4997](https://github.com/micropython/micropython/issues/4997).

I chose pins 27 and 14 (which despite their numbers are beside each other on the board) for no particular reason. As I'm doing no receiving I've actually just left pin 14 floating but it might have been better to connect it to a pull-down resistor.

Note: when you initialize a UART, the ESP32 often (but not always) outputs a console message like this:

    I (7336) uart: ALREADY NULL

This sounds like an error but others have commented on it and it appears to be of no particular importance.

GitHub caching
--------------

The web interface is actually hosted on GitHub, the root page is retrieved in MicroPython and served out so that it appears to come from the device.

All modern browsers accept gzipped data but the request made by MicroPython does not signal that it will accept compressed data. This shows up something odd in how GitHub caches request responses.

If you accept gzipped data you quickly see any changes made to the hosted data on GitHub. However, if you do not, GitHub continues to serve out stale cached data long after the underlying data has changed.

If you use `-v` with `curl` and switch between using `--compressed` and omitting it, you can clearly see the different cache-related headers between the two situations.

I suspect this is some kind of bug on GitHub's part rather than a deliberate attempt to punish anyone requesting uncompressed data.

To get around this a query string with a UUID value is included in each request to bypass the caching.

Websocket command-line tool
---------------------------

For websocket experimentation, I used [`websocat`](https://github.com/vi/websocat) like so:

    $ websocat ws://192.168.0.248/socket

Or:

    $ websocat ws://ding-5cd80b3.local/socket

Undefined pin states
--------------------

As is usual with such devices, the ESP32 pin states are undefined during startup. I've seen the Pixie flicker during this period (but I've never seen the motor budge). For defined pin states, irrespective of the state of the ESP32, I'd:

* Add a pulldown resistor to the Pixie data wire.
* Control the SLP pin of the motor driver via the ESP32 (rather than wiring it directly to the perma-proto board's positive rail) and add a pulldown resistor to the relevant pin.

Then to enable the SLP pin in MicroPython, just do:

    slp = machine.Pin(27, machine.Pin.OUT)
    slp.on()

Lighthouse animation
--------------------

I produced the animated GIF using Google Lab's [Motion Stills app](https://play.google.com/store/apps/details?id=com.google.android.apps.motionstills).

Then after downloading it from Google Drive, I unpacked it into individual frames:

    $ mv ~/Downloads/lighthouse.gif .
    $ convert lighthouse.gif xx_%05d.gif

Then, by looking at the frames, I worked out that I only needed the first 16 for a full cycle. So I threw away the rest.

I then cropped the images to remove unwanted background:

    $ convert xx_* -crop 480x555+0+85 +repage yy_%05d.gif

And repacked the result:

    $ gifsicle --delay=5 --loop yy* > lighthouse-min.gif

Black and flake8
----------------

`black` and `flake8` are used as following with the Python files in this project:

    $ black *.py
    $ flake8 *.py | fgrep -v -e E501 -e E203

Note: `E501` and `E203` are simply rules that `black` and `flake8` disagree on.
