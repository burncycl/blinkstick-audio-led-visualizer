### 2020/06 BuRnCycL

Blinkstick Audio LED Visualizer

Original Code References (Will Yager & Different55 <burritosaur@protonmail.com>):
 - https://gitgud.io/diff-blinkstick/blinkpulse-visualizer/
 - https://gitgud.io/diff-blinkstick/blinkflash
 - http://yager.io/LEDStrip/LED.html
 - https://github.com/wyager/LEDStrip

### About

I liked the results of Will Yager & Different55's effort. However, their projects lacked solid documentation (especially software dependency details). 
There were also a few things I found broken (like using newer versions of numpy broke things in addition to seeing method deprecation warnings).

It also appears that both of these projects are relatively unmaintained.

Lastly, I chose to use the Blinkstick because breadboards with voltage logic level converts are frustrating and don't deliver as clean an end result.  

Support exists for running multiple Blinksticks. However, this runs sub-optimally on Raspberry Pi 3 B+

### Dependencies

Tested working on Raspberry Pi 3 B+ with Raspios Buster Lite (ARM) or Ubuntu 18.04 (x86).

### Semi-Manual Installation

#### Raspberry Pi

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


#### Notes for automation with Ansible

Assuming a virgin Raspberry Pi running Raspios Buster Lite. Boot and run.

As pi user
```
raspi-config
```
Interfacing Options -> SSH -> Enable "yes"


