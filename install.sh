#!/bin/bash

# 2020/06 BuRnCycL
# This will install Packager Maintained Dependencies for blinkstick-audio-led-visualizer and facilitate non-root execution.
# Execute script with sudo privledges.
# e.g. sudo ./install.sh


# Determine if we are running an apt packager
APT=`which apt`
if [ -z "$APT" ]
then
	# Error out if apt isn't detected. 
	echo "ERROR - Apt package manager does not appear to be installed." 
	echo "Perhaps you're trying to run this on a Linux distro that doesn't support the apt package manager?"
	echo "Recommend distros are Raspios Buster or Ubuntu 18.04+"
	exit 1
else
	# Install Packager Maintained Dependencies.
	echo "Apt package manager detected. Proceeding with installation..."
	$APT install -y python3 python3-pip python3-virtualenv virtualenv portaudio19-dev pulseaudio libatlas-base-dev
	# Add udevadm exception for non-root execution.
	echo "Adding udevadm exception, so visualizer can be run as non-root user..."
	echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="20a0", ATTR{idProduct}=="41e5", MODE:="0666"' > /etc/udev/rules.d/85-blinkstick.rules
	udevadm trigger
	exit 0
fi

