#!/usr/bin/env python3

# 2020/06 BuRnCycL
# Outputs sound devices by Id.
# Use this in conjunction with: visualizer.py --dev ID argument to specify non-default Audio Input Device. 

import pyaudio


def find_input_devices():
    pa = pyaudio.PyAudio()
    for device_index in range(pa.get_device_count()):
        devinfo = pa.get_device_info_by_index(device_index)
        print('Device Id: {}, Name: {}'.format(device_index, devinfo['name']))


find_input_devices()

