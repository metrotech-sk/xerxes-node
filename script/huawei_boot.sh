#!/usr/bin/env sh
# -*- coding: utf-8 -*-

echo "usb_modeswitch -v  3566 -p 2001  -X"
usb_modeswitch -v  3566 -p 2001  -X
sleep .5
echo "modprobe option"
modprobe option
sleep .5
echo "echo 3566 2001 ff > /sys/bus/usb-serial/drivers/option1/new_id"
echo  3566 2001 ff > /sys/bus/usb-serial/drivers/option1/new_id
sleep .5
echo "echo AT^RESET > /dev/ttyUSB5"
ls -la /dev/ttyUSB5| grep dialout && {
    echo AT^RESET > /dev/ttyUSB5
    timeout 2 cat /dev/ttyUSB5
    }
