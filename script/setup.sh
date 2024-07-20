
#!/bin/bash
#: Description: Sets up permissions for the spi devices
#:      Author: theMladyPan

xerxes_user='ubuntu'
git_branch='devel'


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

# read network id from the stdin:
printf 'Enter the network id: '
read network_id
echo "Using network id: $network_id"    

echo "updating system..."
apt update
apt upgrade -y

snap install zerotier

echo "adding device to zerotier network $network_id"
zerotier join $network_id

# change hostname to match zerotier id
hostnamectl set-hostname $(sudo zerotier info|cut -d" " -f3)

echo "#######################################################"
echo "ADDING NEW USER, $xerxes_user"
# adduser --gecos "" $xerxes_user
# povoliť sudo
# usermod -aG sudo $xerxes_user
echo "Adding user to spiuser GROUP..."
groupadd -f --system spiuser
usermod -a -G spiuser $xerxes_user
usermod -aG dialout $xerxes_user

cd /home/$xerxes_user

# clone repo
# echo "cloning xerxes repository..."
# sudo -u $xerxes_user git clone https://metrotech-sk/xerxes-node.git
cd xerxes-node
# git checkout $git_branch

cat script/requirements.apt | xargs apt install -y


# TODO (@theMladyPan) skontrolovať či to inštaluje dobre
echo "Installing Udev rules..."
cp script/etc/udev/rules.d/* /etc/udev/rules.d/
echo "Installing netplan configuration..."
cp script/etc/netplan/* /etc/netplan/
echo "Installing systemd networkd configuration..."
mkdir -p /etc/systemd/system/systemd-networkd-wait-online.service.d
cp -r script/etc/systemd/system/* /etc/systemd/system/

# reload udev rules
chown root:root /etc/udev/rules.d/*
udevadm control --reload-rules
udevadm trigger

# install xerxes systemd daemon
echo "installing xerxes daemon..."
systemctl enable xerxes-node.service
systemctl enable huawei-modem.service
# reload daemon
systemctl daemon-reload


echo "creating virtual environment..."
sudo -u $xerxes_user python3 -m venv ./venv
echo "installing and building dependencies, this may take several hours"
sudo -u $xerxes_user venv/bin/python -m pip install -r requirements.txt

echo "Installation complete!"
echo "Done! rebooting in 10 seconds..."
sleep 10
reboot now
