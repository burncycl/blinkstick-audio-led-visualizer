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
# Written and tested on Raspberry Pi B+ running Raspios Debian Buster (ARM) & Ubuntu 18.04 (x86)
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
from os import path
from threading import Thread
from socket import *
import pickle


class BlinkStickViz:
    def __init__(self, sensitivity, rate, chunk, channels, max_int, min_int, transmit, receive, device=None):
        # Declare variables, not war.        
        
        # Network modes for remote Blinkstick communication. By default, both transmit and receive modes set to False.
        self.transmit = transmit
        self.receive = receive
        self.receive_address = '0.0.0.0' # Hard-coded bind to 0.0.0.0 interface. This may need to be adjusted?
        self.receive_port = 12000 # Hard-coded UDP receive/listener port. Adjust this if needed. Didn't bother to make it configurable.
        self.receive_nodes_file = './receive_nodes.list' # Hard-coded filename of receive nodes (IP Addresses) if in transmit mode. List each IP Address on it's own line.  
        if self.transmit == True:
            self.receive_nodes = self.get_receive_nodes() # List of receive nodes parsed from self.receive_nodes_file. 

        # PyAudio Variables.
        self.device = device
        self.paud = pa.PyAudio()
        self.format = pa.paInt16
        self.channels = channels # This may need to be lowered depending on the device used.
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
        
        if self.receive == False: # If not in UDP receive mode, go ahead an Init the audio device and read the stream. 
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


    def get_receive_nodes(self):
        if path.isfile(self.receive_nodes_file):
            with open(self.receive_nodes_file, 'r+') as f:
                ip_addresses = f.readlines()
                for ip_address in ip_addresses:
                    if '.' in ip_address: # Chuck any line that doesn't have a dot in it (i.e. an IP address format 10.9.9.X). 
                        self.receive_nodes.append(ip_address.rstrip('\n')) # Append IP to list of receive nodes. Remove newline.
                    else:
                        continue # Skip lines without dots.
        else:
            print('ERROR - Receive nodes file not found: {}. Please create this file with each receving node IP address listed on it\'s own line.'.format(self.receive_nodes_file))
            sys.exit(1)
            

    def udp_transmit(self, data):
        data = pickle.dumps(data) # Serialize the data for transmission.        
        for receive_ip in self.receive_nodes: # Loop over the list of hosts.
            transmit_socket = socket(AF_INET, SOCK_DGRAM)
            transmit_socket.sendto(data,(receive_ip, self.receive_port))


    def udp_receive(self):
        print('UDP Receive Mode. Listening on: {}, Port: {}'.format(self.receive_address, self.receive_port))
        receive_socket = socket(AF_INET, SOCK_DGRAM)
        receive_socket.bind((self.receive_address, self.receive_port)) 
        while 1:
            data = receive_socket.recv(2048)
            decoded_data = pickle.loads(data) # De-Serialize the received data. 
            self.send_to_stick(decoded_data) # Send the data to our Blinksticks.
 
 
    def send_to_stick(self, data):
        if self.transmit == True: # If we're in transmit mode send the led data via UDP.
            self.udp_transmit(data)                
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
        return(notes_scaled_nosaturation.process(self.audio, num_leds=self.led_count, num_samples=self.sample_rate, sample_rate=self.rate, sensitivity=self.sensitivity)) # Return the processed audio stream to the visualizer functions.


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
        -m, --modes          Visualization Modes (required). Options: all, pulse, blink, loop (List type - Can specify multiple options).
        -s, --sensitivity    Sensitivity to Sound (Default: 1.3).
        -d, --dev            Input Device Index Id (Default: default device). For device discovery use: find_input_devices.py
        -r, --rate           Input Device Hz Rate (Default: 44100). Alternatively set to: 48000
        -c, --chunk          Input Device Frames per buffer Chunk Size (Default: 1024).
        -ch, --channels      Input Device Number of Channels (Default: 2). Likely Alternative set to: 1
        -mx, --max           Maximum time (in seconds) between visualization transition (Default: 35s). # Note: Max and Min can be equal (thus setting a static transition interval).
        -mn, --min           Minimum time (in seconds) between visualization transition (Default: 5s).  #       However, Max cannot be less than Min.
        -tx, --transmit      Transmit Mode via UDP (Default: False). Uses file based (./receive_nodes.list) list of each IP Addresses on own line to send Blinkstick data.
        -rx, --receive       Receive Mode via UDP (Default: False). Listens on UDP Port 12000. Bypasses listening to input device (i.e. Microphone). Displays what was sent.  
 

    Command Examples:
        python3 visualizer.py --modes all                                                        # Switches between all visualization modes at random interval (Default: max=35s min=5s).
        python3 visualizer.py --modes all --max 120 --min 30                                     # Switches between all visualization modes at random configured max and min interval (in seconds).
        python3 visualizer.py --modes pulse loop                                                 # Example of a targeted mode selection. Personal favorite visualization settings.
        python3 visualizer.py --modes flash pulse                                                # Example of a targeted mode selection.
        python3 visualizer.py --modes pulse loop --sensitivity 1                                 # Example of non-default sound sensitivity adjustment.
        python3 visualizer.py --modes pulse loop --dev 1 --rate 48000 --chunk 4096 --channels 1  # Example of non-default device, Input Device Hz rate, chunk size, and channels.
        python3 visualizer.py --modes pulse loop --transmit                                      # Example of transmit mode.        
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
    parser.add_argument('-ch', '--channels', help='Input Device Number of Channels (Default: 2)', default=2)
    parser.add_argument('-mx', '--max', help='Maximum time between transition (Default: 35s)', default=35)
    parser.add_argument('-mn', '--min', help='Minimum time between transition (Default: 5s)', default=5)
    parser.add_argument('-tx', '--transmit', help='Transmit Mode via UDP (Default: False)', default=False, action='store_true')
    parser.add_argument('-rx', '--receive', help='Receive Mode via UDP (Default: False)', default=False, action='store_true')    
    args = parser.parse_args()

    ## Command line argument handlers
    if args.readme:
        readme()
    # Handle error scenarios. 
    elif args.transmit == True and args.receive == True:
        print('ERROR - Cannot both Transmit and Receive. Please pick one or the other.')
        sys.exit(1)
    elif int(args.max) < int(args.min): 
        print('ERROR - Maximum visualization transition interval ({}s) cannot be less than Minimum transition interval ({}s).'.format(args.max, args.min))
        sys.exit(1)
    # Handle Receive mode.
    elif args.receive == True:
        BlinkStickViz(sensitivity=args.sensitivity, rate=args.rate, chunk=args.chunk, channels=args.channels, max_int=args.max, min_int=args.min, transmit=args.transmit, receive=args.receive, device=args.dev).udp_receive()
    # Handle Main
    elif args.modes is not None:
        BlinkStickViz(sensitivity=args.sensitivity, rate=args.rate, chunk=args.chunk, channels=args.channels, max_int=args.max, min_int=args.min, transmit=args.transmit, receive=args.receive, device=args.dev).main(modes=args.modes)
    else:
        print('README: python3 visualizer.py -readme')
        sys.exit(0)

