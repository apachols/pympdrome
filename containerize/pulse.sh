#!/bin/sh

pulseaudio -k && pulseaudio --load=module-native-protocol-tcp --exit-idle-time=-1 --daemon