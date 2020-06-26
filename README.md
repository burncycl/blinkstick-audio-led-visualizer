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

### Dependencies

Tested working on Raspios Buster Lite (ARM) and Ubuntu 18.04 (x86)

