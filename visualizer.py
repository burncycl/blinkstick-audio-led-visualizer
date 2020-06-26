#!/usr/bin/env python3

# 2020/06 BuRnCycL
# Blinkstick Audio LED Visualizer
#### Bibliography
# Original Code References (Will Yager & Different55 <burritosaur@protonmail.com>):
# - https://gitgud.io/diff-blinkstick/blinkpulse-visualizer/
# - https://gitgud.io/diff-blinkstick/blinkflash
# - http://yager.io/LEDStrip/LED.html
# - https://github.com/wyager/LEDStrip
#### About
# I liked the results of Will Yager & Different55's effort. However, their projects lacked solid documentation (especially software dependency details).
# There were also a few things I found broken (like using newer versions of numpy broke things in addition to seeing method deprecation warnings).
# It also appears that both of these projects are relatively unmaintained/orphaned.
# Lastly, I chose to use the Blinkstick because breadboards with voltage logic level converts are frustrating and don't deliver as clean an end result.
#### Dependency Information
# Written and tested on Debian Buster for Raspberry Pi (ARM) & Ubuntu 18.04 (x86)
# Hardware Dependency on WS2812B RGB LEDs, microphone, and Blinkstick USB Micro-controller: https://www.blinkstick.com/products/blinkstick-flex
# Python-pip - pip3 install pyaudio blinkstick numpy
# Package Managed - apt install -y python3 python3-pip python3-virtualenv virtualenv portaudio19-dev pulseaudio libatlas-base-dev


import pyaudio as pa
import numpy as np
from blinkstick import blinkstick
import notes_scaled_nosaturation
from time import sleep, time
from colorsys import hsv_to_rgb
import argparse, sys, random
from threading import Thread


class BlinkStickViz:
    def __init__(self, sensitivity, rate, chunk, max_int, min_int, device=None):
        # Declare variables, not war.
        if int(max_int) < int(min_int): # Handle error scenario.
            print('ERROR - Maximum visualization transition interval ({}s) cannot be less than Minimum transition interval ({}s).'.format(max_int, min_int))
            sys.exit(1)
        # PyAudio Variables.
        self.device = device
        self.paud = pa.PyAudio()
        self.format = pa.paInt16
        self.channels = 2
        self.rate = rate # This may need to be tuned to 48000Hz
        self.chunk = chunk # This may need to be tunend to 512, 2048, or 4096.

        # Visualization Variables.
        self.loop = None # Pulse from both ends of the strip. Default None, self.main() sets this.
        self.sensitivity = sensitivity # Sensitivity to sound.
        self.sample_rate = 1024 # Haven't seen this tuned. But perhaps?
        self.wait_interval_max = int(max_int) # Max time in seconds visualization will run before switching.
        self.wait_interval_min = int(min_int) # Minimum time in seconds visualization will run before switching.
        self.stop = False  # Tells visualization to stop running. Facilitates switching to another visualization. Default to False.

        # Init Blinkstick, Audio input, and Analyze/Read Audio. Create leds object, so we can loop over in the visualization methods.
        self.led_count = None # Determine the LED count by querying the stick(s). Populated by self.get_blinksticks() 
        self.sticks = self.get_blinksticks() #blinkstick.find_first() # Discover Blinkstick Device.        
        self.audio_stream = self.input_device() # Init microphone as input source/stream.
        self.audio = self.read_audio(self.audio_stream, num_samples=self.sample_rate) # Read the audio stream.
        

    # Utilize multiple Blinksticks on the same parent device. Note: This won't run well on Raspberry Pi. Beefer CPU required.
    def get_blinksticks(self):
        discovered_blinksticks = []
        led_counts = []
        blinksticks = blinkstick.find_all() # Discover multiple Blinksticks.        
        for stick in blinksticks:
            count = stick.get_led_count()
            led_counts.append(count)       
            discovered_blinksticks.append(stick)
        
        # Verify we're addressing the same number of LEDs for both sticks.
        led_count = set(led_counts) # Set will deduplicate.
        if len(led_count) == 1: # Should be left with one, if everything is equal.
            for count in led_count:
                self.led_count = int(count)
        else:
            print('ERROR - LED Count is NOT equal between Blinksticks: {} - Values should match.'.format(led_count))
            sys.exit(1)
        return(discovered_blinksticks)


    def input_device(self): # i.e. Microphone
        if self.device is not None: # Use non-default device.
            audio_stream = self.paud.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                frames_per_buffer=self.chunk,
                input= True,
                input_device_index=self.device,
                )
        else: # Otherwise, use the default.
            audio_stream = self.paud.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                frames_per_buffer=self.chunk,
                input= True,
                )
        return(audio_stream)


    # Convert the audio data to numbers, num_samples at a time.
    def read_audio(self, audio_stream, num_samples):
        while True:
            # Read all the input data.
            samples = audio_stream.read(num_samples, exception_on_overflow=False)
            # Convert input data to numbers
            samples = np.frombuffer(samples, dtype=np.int16).astype(np.float)
            samples_l = samples[::2]
            samples_r = samples[1::2]
            yield samples_l, samples_r


    def send_to_stick(self, data):    
        for stick in self.sticks:
            stick.set_led_data(0, data)
                        

    def main(self, modes):
        # Start with more complex conditional for the mode and move to simpler.
        if 'all' in modes:
            print('All - Pulse, Flash, and Loop (randomly).')
            self.random_visualization_handler(loop='random')
        elif 'pulse' in modes and 'flash' in modes and 'loop' in modes:
            print('Pulse with Loop (static) and Flash.')
            self.random_visualization_handler(loop=True)
        elif 'pulse' in modes and 'flash' in modes:
            print('Pulse and Flash')
            self.random_visualization_handler(loop=False)
        elif 'pulse' in modes and 'loop' in modes:
            print('Pulse with Loop.')
            self.loop = True
            self.pulse_visualization()
        elif 'flash' in modes and 'loop' in modes: # Note: flash visualization doesn't use loop. So even if it's specified, it won't matter.
            print('Flash only. Loop has no affect.')
            self.flash_visualization()
        elif 'pulse' in modes:
            print('Pulse only.')
            self.pulse_visualization()
        elif 'flash' in modes:
            print('Flash only.')
            self.flash_visualization()


    def random_visualization_handler(self, loop):
        visualizations = [self.pulse_visualization, self.flash_visualization]
        self.wait_interval = random.randint(self.wait_interval_min, self.wait_interval_max)
        while True:
            self.stop = False # Always start the loop with stop Default to False
            # Loop Handler
            if loop == True:
                self.loop = True
            elif loop == False:
                self.loop = False
            elif loop == 'random':
                self.loop = random.choice([True, False])
            visualization_picked = random.choice(visualizations)
            print('Waiting: {}s, Loop: {}, Visualization: {}'.format(self.wait_interval, self.loop, visualization_picked))
            t = Thread(target=visualization_picked)
            t.start()
            sleep(self.wait_interval)
            self.stop = True
            t.do_run = False
            t.join()
            self.wait_interval = random.randint(self.wait_interval_min, self.wait_interval_max)


    def led_data(self):
        return(notes_scaled_nosaturation.process(self.audio, num_leds=self.led_count, num_samples=self.sample_rate, sample_rate=self.rate, sensitivity=self.sensitivity)) # Pass the Audio Stream to be processed.


    def pulse_visualization(self):
        leds = self.led_data()
        
        if self.loop:
            data = [0]*int(self.led_count/2)*3
            data2 = [0]*int(self.led_count/2)*3
        else:
            data = [0]*self.led_count*3

        sent = 0
        for frame in leds:
            brightest = 0
            for i, led in enumerate(frame):
                if led > frame[brightest]:
                    brightest = i

            hue = brightest/48.0
            color = hsv_to_rgb(hue, 1, min(frame[brightest]*1.2, 1))

            del data[-1]
            del data[-1]
            del data[-1] # I feel dirty having written this.
            if self.loop:
                del data2[0]
                del data2[0]
                del data2[0]

            color = [int(color[1]*255), int(color[0]*255), int(color[2]*255)]
            data = color + data

            if self.loop: # finaldata exists because if I try to do the seemingly sane thing it breaks.
                data2 = data2 + color
                finaldata = data+data2
            else:
                finaldata = data

            now = time()
            if now-sent < .02:
                sleep(max(0, .02-(now-sent)))

            sent = time()
            self.send_to_stick(finaldata)
            if self.stop == True: # Handle stopping the thread, so another visualization can be executed.
                break


    def flash_visualization(self):
        leds = self.led_data()
        
        last_frame = [0]*self.led_count # For smooth transitions, we need to know what things looked like last frame.
        sent = 0
        for frame in leds:
            data = []
            size = []

            brightness = 0
            brightest = 0
            totalsize = 0

            for i in range(self.led_count): # First pass, let's get an idea of how loud things are.
                brightness = brightness + frame[i]
                if frame[i] > frame[brightest]:
                    brightest = i

            for i in range(self.led_count): # Second pass, let's try and figure out the rough size of each section.
                if brightness == 0:
                    frame[i] = 1
                    size.append(1)
                    totalsize = totalsize + 1
                    continue
                try:
                    size.append(int(frame[i]/brightness*self.led_count))
                    totalsize = totalsize+size[-1]
                except ValueError:
                    pass

            if brightness == 0:
                brightness = self.led_count

            while totalsize < self.led_count:
                for i in range(self.led_count):
                    if totalsize < self.led_count and size[i] > 0:
                        size[i] = size[i] + 1
                        totalsize = totalsize + 1
                    elif totalsize == self.led_count:
                        break

            for i in range(self.led_count):
                hue = i/(self.led_count*1.75)
                r, g, b = hsv_to_rgb(hue, 1, min((last_frame[i]*2.6+frame[i]*1.3)/3, 1))
                data = data+[int(g*255), int(r*255), int(b*255)]*int(size[i])

            now = time()
            if now-sent < .02:
                sleep(max(0, .02-(now-sent)))

            sent = time()
            self.send_to_stick(data)
            last_frame = frame
            if self.stop == True: # Handle stopping the thread, so another visualization can be executed.
                break


def readme():
    print('''
Blinkstick Audio LED Visualizer
    Usage:
        -m, --modes          Visualization Modes (required). Options: all, pulse, blink, loop (list type)
        -s, --sensitivity    Sensitivity to Sound (Default: 1.3).
        -d, --dev            Input Device Index Id (Default: default device). For device discovery use: find_input_devices.py
        -r, --rate           Input Device Hz Rate (Default: 44100). Alternatively set to: 48000
        -c, --chunk          Input Device Frames per buffer Chunk Size (Default: 1024).
        -x, --max            Maximum time (in seconds) between visualization transition (Default: 60s). # Note: Max and Min can be equal (thus setting a static transition interval).
        -n, --min            Minimum time (in seconds) between visualization transition (Default: 5s).  #       However, Max cannot be less than Min.

    Command Examples:
        python3 visualizer.py --modes all                                            # Switches between all visualization modes at random default (max=60s min=5s) interval.
        python3 visualizer.py --modes all --max 120 --min 30                         # Switches between all visualization modes at random configured max and min interval (in seconds).
        python3 visualizer.py --modes pulse loop                                     # Example of a targeted mode selection.
        python3 visualizer.py --modes flash pulse                                    # Example of a targeted mode selection.
        python3 visualizer.py --modes pulse loop --sensitivity 1                     # Example of non-default sound sensitivity adjustment.
        python3 visualizer.py --modes pulse loop --dev 1 --rate 48000 --chunk 4096   # Example of non-default device, Input Device Hz rate, and chunk size.
    ''')
    sys.exit(0)


if __name__ == '__main__':
    ## Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-readme','--readme', help='Display Readme/Help.', action='store_true')
    parser.add_argument('-m', '--modes', help='Visualization Modes (required). Options: all, pulse, blink, loop (list type)', nargs='+')
    parser.add_argument('-s', '--sensitivity', help='Sensitivity to Sound. (Default: 1.3)', default=1.3)
    parser.add_argument('-d', '--dev', help='Input Device (Default: default device)', default=None)
    parser.add_argument('-r', '--rate', help='Input Device Hz Rate (Default: 44100)', default=44100)
    parser.add_argument('-c', '--chunk', help='Input Device Frames per buffer Chunk Size (Default: 1024)', default=1024)
    parser.add_argument('-x', '--max', help='Maximum time between transition (Default: 60s)', default=60)
    parser.add_argument('-n', '--min', help='Minimum time between transition (Default: 5s)', default=5)
    args = parser.parse_args()

    ## Command line argument handlers
    if args.readme:
        readme()
    elif args.modes is not None:
        BlinkStickViz(sensitivity=args.sensitivity, rate=args.rate, chunk=args.chunk, max_int=args.max, min_int=args.min, device=args.dev).main(modes=args.modes)
    else:
        print('README: python3 visualizer.py -readme')
        sys.exit(0)

