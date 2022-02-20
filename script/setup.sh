
#!/bin/bash
#: Description: Sets up permissions for the spi devices
#:      Author: theMladyPan

udev_rules_file='/etc/udev/rules.d/90-custom.rules'

# check if the script is being run as root
if [[ $EUID -ne 0 ]]
then
	printf 'This script must be run as root.\nExiting..\n'
	exit 1
fi

# check that the rules file doesn't already exist
if [ -f $udev_rules_file ]
then
	printf 'The spi rules file already exists.\nExiting...\n'
	exit 1
fi
