#!/bin/bash

# Starts pulseaduio and monitors to make sure the process is up. If it dies, restarts
# Works in conjunction with systemd service /etc/systemd/system/blinkstickviz.service

# Functions
start_pulseaudio () {
	echo "Starting Pulseaudio..."
	pulseaudio --start --verbose &
}

while true; do
	PA_PID=`ps auxww | grep 'pulseaudio --start --verbose' | grep -v "grep" | awk '{print $2}'`
	if [ ! -z "$PA_PID" ]; then
		echo "Pulseaudio is running - $PA_PID"
	else
		start_pulseaudio

	fi
	sleep 5
done
