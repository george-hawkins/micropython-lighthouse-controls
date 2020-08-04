Parts
=====

This page lists the various parts needed to build the lighthouse and its electronics.

Development board
-----------------

I used an Espressif ESP32 DevKitC **VB** board. Unlike most boards (which feature a basic WROOM module with just 520KiB of SRAM) this board has a WROVER module with an additional 4MiB of SRAM. This gives you a bit more space to work with when running more substantial MicroPython programs. It's available from many suppliers, including:

* [Mouser](https://www.mouser.com/ProductDetail/356-ESP32-DEVKITC-VB) - US$10 (postage not included).
* [Banggood](https://www.banggood.com/ESP32-DevkitC-Core-Board-ESP32-Development-Board-ESP32-WROOM-32U32D-F-VB-VIB-S1-p-1426780.html?ID=566841) - US$18 (postage included).

Adafruit parts
--------------

* [Adafruit Pixie](https://www.adafruit.com/product/2741) -  $15
* [1:48 plastic gearbox motor](https://www.adafruit.com/product/3777) - $3
* [Motor pulley](https://www.adafruit.com/product/3789) - $0.75
* [DRV8833 motor driver breakout](https://www.adafruit.com/product/3297) - $5
* [Half-sized perma-proto board](https://www.adafruit.com/product/1609) - $4.50
* [2-pin 3.5mm terminal block](https://www.adafruit.com/product/724) - $3

All these items are available directly from [Adafruit](https://www.adafruit.com/) but they're also available through lots of [distributors](https://www.adafruit.com/distributors), in particular, all these items are available via [Mouser](https://www.mouser.com/) and [Digikey](https://www.digikey.com/).

I used Mouser for my order as it meant I could get the Adafruit items and additional parts like the ESP32 DevKitC VB all together.

If I was doing this again, I'd use a motor and motor driver from Pololu instead, see below for more details.

Light cover
-----------

The half-open/half-closed cover for the lighthouse light was cut from a standard tin can (I chose one with a nice shiny metal interior).  I used a tin-snips (like [this one](https://www.stanleytools.com/products/hand-tools/cutting-tools/snips/fatmax-straight-cut-compound-action-aviation-snips/14-563)) to cut it down to size and then covered the exposed edges with duct tape to make them less of an accident risk.

I initially bought a tin-snips for cutting circuit boards (where it does a so-so job) but have since found them great for cutting all kinds of material - you can cut surprisingly straight lines with them through material like a tin can.

Bolts and threadlocker
----------------------

* M2 10mm bolts with corresponding nuts (something like [these](https://www.conrad.com/p/toolcraft-827129-fillister-head-screws-m2-10-mm-phillips-din-7985-steel-zinc-galvanized-100-pcs-827129) with these [nuts](https://www.conrad.com/p/toolcraft-815608-hexagonal-nuts-m2-din-934-steel-zinc-plated-100-pcs-815608)) - for attaching the tin can to the motor pulley.
* 2.5x16mm round-headed wood screws (something like [these](https://www.homebase.co.uk/wood-screw-round-head-brass-3-x-12mm-10-pack_p168370) but different dimensions) - for attaching the metal frame to the base.
* M2.5 25mm bolts with corresponding nuts (something like [these](https://www.conrad.com/p/toolcraft-145896-fillister-head-screws-m25-25-mm-phillips-din-7985-steel-zinc-galvanized-200-pcs-145896) with these [nuts](https://www.conrad.com/p/toolcraft-815616-hexagonal-nuts-m25-din-934-steel-zinc-plated-100-pcs-815616)) - for bolting the motor to the frame.
* Loctite 243 threadlocker - to prevent bolts from rattling loose due to motor vibration.

Note that Loctite 243 isn't so strong that you can't subsequently undo the bolts (there are stronger threadlocker formulations which are essentially permanent).

Base and frame
--------------

* 1m x 35.5mm x 1.5mm galvanized flat steel bar for the frame (something like [this](https://www.homebase.co.uk/galvanised-steel-flat-bar-profile-1m-x-35-5mm_p414991)).
* 160cm x 150cm x 24mm spruce plywood for the base.

Wire
----

* 20AWG silicone-coated stranded wire - 1m black and 1m red for the Pixie power wires.
* 26AWG silicone-coated stranded wire - 1m for the Pixie data wire (26AWG is the standard thickness for jumper wires).
* Solid core hookup wire (like [this](https://www.adafruit.com/product/1311)) - for wiring up the perma-proto board.

The Pixie [hookup guide](https://learn.adafruit.com/pixie-3-watt-smart-chainable-led-pixels?view=all) recommends 16AWG wire for the Pixie power wires. This is complete overkill if you're only planning on using a single Pixie (which will draw, at most, 1A). I accidentally used 18AWG wire when I intended to use 20AWG wire. The terminal block (up above) is rated for 30-16AWG wire according to the Adafruit product page. However, it's very inconvenient to use stranded 18AWG wire with them and 16AWG wire definitely would be too fat for the holes.

Note: I crimped the non-soldered end of the Pixie data wire with a crimping tool like [this](https://www.pololu.com/product/1929) and used a crimp pin like [this](https://www.pololu.com/product/1931) with a connector housing like [this](https://www.pololu.com/product/1900).

Bits and pieces
---------------

* right-angle female header (i.e. something like [this](https://www.adafruit.com/product/1542) cut down to just three sockets) - for connecting the Pixie data and motor wires to the perm-proto board.
* 0.1uF ceramic capacitor (like [these](https://www.adafruit.com/product/753)) - lucky charm talisman for reducing motor noise.
* 200mm x 2.5mm cable-ties - to hold the Pixie wiring in-place on the frame.

Power supply
------------

The motor and in particular the 3W RGB LED draw a lot more current than most small electronics projects and certainly a lot more than the 500mA typically provided by your computer's USB ports (though, during development, you can run both the motor and RGB LED from such a port if you keep the speed and brightness low).

So make sure that the micro-USB power adapter, that you use, can supply at least 2A at 5V. The older style 2.5A Raspberry Pi power adapters are perfect (the newer style ones come with a USB-C connector). RS supply the classic style Raspberry Pi power adapters with region-specific plugs, just go to [RS Components](https://www.rs-online.com/), choose your region (for North American, choose the Allied link rather than the RS link) and search for:

* T6717DV for a US-style plug.
* T6716DV for an EU-style plug.
* T6715DV for a UK-style plug.

These are the standard Raspberry Pi power supplies and are available from many other online retailers - just search for the part numbers in Google Shopping.

Continually connecting and disconnecting the micro-USB is likely to end in damage to the board. A better solution is something like this:

* [micro-USB to micro-USB on-off switch](https://www.reichelt.com/ch/en/raspberry-pi-cable-with-switch-30-cm-black-rpi-cable-sw-30-p223610.html) - $3.

Note that this particular cable does not support data transfer.

Pololu
------

[Adafruit](https://www.adafruit.com/) and [Sparkfun](https://www.sparkfun.com/) are great for hobbyist electronics parts. However, for electro-mechanical parts, Pololu is a much better source. Adafruit and Sparkfun just carry a few stepper motors and gearbox motors, whereas Pololu specialize in these kinds of parts and carry full ranges of different kinds of motors - so you can choose exactly what you want for a particular project. And all their other parts play well in electro-mechanical projects, e.g. I had some jumper wires from Adafruit that would be perfect for nearly any electronics project but couldn't carry enough current for a [rover](https://www.pololu.com/category/202/romi-chassis-and-accessories) project, that I was doing, but the corresponding Pololu wires worked perfectly (and were much nicer to use as they were silicone-coated rather than plastic-coated).

The Adafruit motor listed above has a gear ratio of 1:48. Even at minimum speed it still turns quite quickly (the motor has a minimum speed below which it simply comes to a stop).

Pololu offer similar motors with more appropriate gear ratios:

* [120:1](https://www.pololu.com/product/1121)
* [200:1](https://www.pololu.com/product/1120)

Pololu also provide a [DRV8833 motor driver breakout](https://www.pololu.com/product/2130) that's essentially identical to the Adafruit breakout.

Note: Adafruit also offer an [1:90 gearbox motor](https://www.adafruit.com/product/3801) that would also have been a better initial choice.

3W RGB LED
----------

I used a $15 Adafruit Pixie for the RGB LED component of this project. Initially, I looked at using Adafruit's basic [3W RGB common anode LED](https://www.adafruit.com/product/2530) which is a lot cheaper at just $3. However, after some experimentation, it's clear that these things get _extremely_ hot if run at full brightness. So the additional thermal-cutoff circuitry of the Pixie seemed worth the additional cost to avoid the risk of setting my apartment on fire.

Note that the basic 3W RGB LED isn't as cheap as it seems, as the Pixie includes the necessary additional FETs and limiting resistors. With the basic 3W RGB LED, you'd also need three [IRLB8721 N-channel power MOSFETs](https://www.adafruit.com/product/355) (these are available for about half the Adafruit price from suppliers like Mouser or Digikey) and a 1W or 0.5W limiting resistor for the red element of the LED (the resistors that you use for most simple electronics projects are usually 0.25W resistors). You also have to factor in the additional time cost of soldering in these components and the fairly considerable extra space that these non-SMT components take up.
