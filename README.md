### 2020/06 BuRnCycL

**Blinkstick Audio LED Visualizer**

Original Code References (Will Yager & Different55 <burritosaur@protonmail.com>):
 - https://gitgud.io/diff-blinkstick/blinkpulse-visualizer/
 - https://gitgud.io/diff-blinkstick/blinkflash
 - http://yager.io/LEDStrip/LED.html
 - https://github.com/wyager/LEDStrip

### About

I liked the results of Will Yager & Different55's efforts. However, their projects lacked detailed dependency documentation/installation.
There were also a few things I found broken or stale. For example using newer versions of numpy broke due to deprecation warnings coming to life.

It also appears that both of these projects are relatively unmaintained.

I wanted additional features, like scalability via Network.

Lastly, I chose to use the Blinkstick because breadboards with voltage logic level converts are frustrating and don't deliver as clean an end result.  

**Features**
* Working code (as of publish date) and well documented.
* Scalability - Support for running multiple Blinksticks on the same parent device. Note: This runs sub-optimally on Raspberry Pi 3 B+, but fine on decent x86 processors.
* Scalability - Support for running multiple Blinksticks over multiple parent devices via network (UDP transmit/receive).
* Scalability - Support for Auto-Discovery 
* Modularity - New visualizations can be added in with ease as functions.
* Object oriented (more or less).
* Input only mode. Bypasses Blinkstick Discovery, and turns device into just a microphone transmitting via Network.

Tested working on Raspberry Pi 3 B+ with Raspios Buster Lite (ARM) or Ubuntu 18.04 (x86).

### Hardware

Note: Your implementation might not require all the hardware listed. Just making suggestions for resources.

I don't promise the Amazon links listed will always work, but you can Web Search for said product and find equivalents. 

* Blinkstick Flex (or similar Blinkstick products) 
  - https://www.blinkstick.com/products/blinkstick-flex
* WS2812B LED Strip (Important: Blinkstick Flex can only power up to 32 LEDs in it's default configuration. Simply cut the strip to size and solder to micro-controller)
  - https://amzn.to/2NA5u3W
* Raspberry Pi 3 (3 B+ or better) / x86 Computer
  - https://amzn.to/3i8zHVy 
* Electrial Wire & Soldering Kit (Blinkstick also sells pre-soldered Kits with LEDs) + Solder
  - https://amzn.to/31jSQhg - Can strip these for soldering or find equivalent cable.
  - https://amzn.to/3fZRHQ8
  - https://amzn.to/3871a5w
* Microphone and/or USB External Stereo Sound Adapter 
  - https://amzn.to/31y4FRp
  - https://amzn.to/2YzE0S2
* MicroUSB cord
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

Execute `install.sh` to install apt packager maintained dependencies.
```
cd blinkstick-audio-led-visualizer/
sudo ./install.sh
```

### Manual Dependency Installation
Recommend use `install.sh` script and Python Virtual Environments, as opposed to running these commands manually.

Python
```
pip3 install pyaudio blinkstick numpy
```

Apt Package Managed 
```
apt install -y python3 python3-pip python3-virtualenv virtualenv portaudio19-dev pulseaudio libatlas-base-dev
```

### Run Visualizations

Setup Python Virtual Environment with all Python dependencies
```
source ./init.sh
```
Important to note: The Raspberry Pi needs Pulseaudio. `init.sh` will run this for you.

**Run Pulse Loop Visualization**
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

### Network Mode Visualizations

### Auto-Discovery
If no *receive_nodes.list* file is provided, Auto Discovery will be used.
* Receive nodes (the one being sent LED visualization information) will Announce via broadcast on port 50000 every 5 seconds.
* Transmit node (the one with the input device) will listen for broadcast packets on port 50000 from available receive nodes.  
* Once the Trasmit node has discovered a Receive node, it will send an acknowledgement, telling the receive node to stop announcing.
* On the transmit node, discovery will continue indefinitely. Thus, you can keep adding devices while a visualation is active.

### List Provided Discovery

On transmitting Pi (i.e. the one that is listening to the Input Device (e.g. Microphone)), Create *receive_nodes.list* and populate it with IP addresses.


```
touch receive_nodes.list
```

Example *receive_nodes.list* 
```
10.3.3.30
10.3.3.31
10.3.3.32
```

On recieving Pi
```
python3 visualizer.py --receive
```

On transmitting Pi
```
python3 visualizer.py --modes pulse loop --transmit
```

Note: Utilizes UDP port 12000

### TODO

* Implement methods for direct digital input (like an mp3), as opposed to a microphone.
* Implement passthrough of microphone input to speaker output. Can probably achieve this with JACK?
* Finish Ansible Automation.
