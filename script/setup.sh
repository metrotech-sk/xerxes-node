
#!/bin/bash
#: Description: Sets up permissions for the spi devices
#:      Author: theMladyPan

udev_rules_file='/etc/udev/rules.d/50-custom.rules'

xerxes_user='stanke'
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


echo "updating system..."
apt update
apt upgrade -y
cat requirements.apt | xargs apt install -y

snap install zerotier

echo "adding device to zerotier network"
zerotier join a0cbf4b62a6c2b69

# change hostname to match zerotier id
hostnamectl set-hostname $(sudo zerotier info|cut -d" " -f3)

echo "Disabling UART CMDline..."
# TODO (@theMladyPan) - toto si zaslúži spraviť lepšie
echo "net.ifnames=0 dwc_otg.lpm_enable=0 root=LABEL=writable rootfstype=ext4 elevator=deadline rootwait fixrtc"|tee /boot/firmware/cmdline.txt

echo "#######################################################"
echo "ADDING NEW USER, $xerxes_user"
adduser --gecos "" $xerxes_user
# povoliť sudo
usermod -aG sudo $xerxes_user
echo "Adding user to spiuser GROUP..."
groupadd -f --system spiuser
usermod -a -G spiuser $xerxes_user
usermod -aG dialout $xerxes_user

su $xerxes_user
cd /home/$xerxes_user

# download my public key
wget https://gist.githubusercontent.com/theMladyPan/8a73cc10c35b78c20a1d64c694740658/raw/5dd4e8b32e8fa42bf595d936d8c4d7f454da8e6c/id_rsa.pub
mv id_rsa.pub ./.ssh

# clone repo
echo "cloning xerxes repository..."
git clone https://themladypan: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@github.com/xeus-cer/xerxes-node.git
cd xerxes-node
git checkout $git_branch

# install xerxes systemd daemon
echo "installing xerxes daemon..."

ln script/xerxes-node.service /etc/systemd/system
systemctl enable xerxes-node.service

# TODO (@theMladyPan) skontrolovať či to inštaluje dobre
echo "Installing Udev rules..."
cp script/50-custom.rules /etc/udev/rules.d/
chown root:root $udev_rules_file

echo "creating virtual environment..."
python3 -m venv ./venv
echo "installing and building dependencies, this may take several hours"
venv/bin/python -m pip install -r requirements.txt

echo "building libraries"
mkdir build
cd build
cmake ../lib&&make
cd ..

spd-say "Installation complete!"

echo "Done! rebooting in 60 seconds..."
sleep 60&&reboot now
