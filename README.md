### 2020/06 BuRnCycL

**Blinkstick Audio LED Visualizer**

Original Code References (Will Yager & Different55 <burritosaur@protonmail.com>):
 - https://gitgud.io/diff-blinkstick/blinkpulse-visualizer/
 - https://gitgud.io/diff-blinkstick/blinkflash
 - http://yager.io/LEDStrip/LED.html
 - https://github.com/wyager/LEDStrip

### About

I liked the results of Will Yager & Different55's effort. However, their projects lacked solid documentation (especially software dependency details). 
There were also a few things I found broken or stale. For example using newer versions of numpy broke due to deprecation warnings coming to life.

It also appears that both of these projects are relatively unmaintained.

Lastly, I chose to use the Blinkstick because breadboards with voltage logic level converts are frustrating and don't deliver as clean an end result.  

**Features**
* Working code (as of publish date) and well documented.
* Scalability - Support for running multiple Blinksticks on the same parent device. Note: This runs sub-optimally on Raspberry Pi 3 B+, but fine on decent x86 processors.
* Scalability - Support for running multiple Blinksticks over multiple parent devices via network (UDP transmit/receive).
* Modularity - New visualizations can be added in with ease as functions.
* Object oriented (more or less).

Tested working on Raspberry Pi 3 B+ with Raspios Buster Lite (ARM) or Ubuntu 18.04 (x86).

### Hardware

Note: Your implementation might not require all the hardware listed. Just making suggestions for resources.

I don't promise the Amazon links listed will always work, but you can Web Search for said product and find equivalents. 

* Blinkstick Flex (or similar Blinkstick products) 
  - https://www.blinkstick.com/products/blinkstick-flex
* Electrial Wire & Soldering Kit (Blinkstick also sells pre-soldered Kits with LEDs) + Solder
  - https://amzn.to/31jSQhg - Can strip these for soldering or find equivalent cable.
  - https://amzn.to/3fZRHQ8
  - https://amzn.to/3871a5w
* Raspberry Pi 3 (or 3 B+) / x86 Computer
  - https://amzn.to/3i8zHVy 
* WS2812B LED Strip (Important: Blinkstick Flex can only power 32 LEDs. Simply cut the strip to size and solder to micro-controller)
  - https://amzn.to/2NA5u3W
* Microphone and/or USB External Stereo Sound Adapter 
  - https://amzn.to/31y4FRp
  - https://amzn.to/2YzE0S2
* MicroUSB cord (first cord I tried was cheap crap, and didn't work)
  - https://amzn.to/3idO37p
* Audio Splitter Cable (useful if you have an input device, like a cellphone and a speaker. Used in conjunction with USB External Stereo Sound Adapter with Red Microphone input).
  - https://amzn.to/2BEcmdH 
* 3.5mm Aux Cord (again, useful if you have an input device, like a cellphone and a speaker)
  - https://amzn.to/2YBIQ13

### Ansible Automated Installation

Want to provision a fleet of Raspberry Pi's with Blinksticks listening via network? DevOps to the rescue.

* Reference: https://github.com/burncycl/ansible-blinkstick-audio-led-visualizer

### Semi-Automated Installation

Assuming a virgin Raspberry Pi running Raspios Buster Lite. Boot and install the following Prerequisites.

Install git
```
sudo apt install git 
```

Clone this repo
```
git clone https://github.com/burncycl/blinkstick-audio-led-visualizer.git
```

Execute install.sh to install apt packager maintained dependencies.
```
cd blinkstick-audio-led-visualizer/
sudo ./install.sh
```

### Run Visualizations

Setup Python Virtual Environment with all Python dependencies
```
source ./init.sh
```
Important to note: The Raspberry Pi needs Pulseaudio. `init.sh` will run this for you.

**Run Visualization**
```
python3 visualize.py --modes pulse loop
```

or
```
python3 visualize.py --modes all
```

For additional modes of operation reference script readme.
```
python3 visualize.py --readme
```

### TODO

* Implement methods for direct digital input (like an mp3), as opposed to a microphone.
* Implement passthrough of microphone input to speaker output.
* Finish Ansible Automation.
