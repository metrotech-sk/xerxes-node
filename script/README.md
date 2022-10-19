# scripts

.<br>
├── 50-custom.rules # udev rules<br>
├── README.md # this readme<br>
├── setup.sh # installation scriot, run as root<br>
├── xerxes-node.service # systemd daemon service script<br>
└── xerxes-node.sh # script to start/stop daemon<br>

0 directories, 5 files

## use network manager for all connections
```shell
stanke@98462fd2d4:~$ cat /etc/netplan/01-network-manager-all.yaml 
# This file is generated from information provided by the datasource.  Changes
# to it will not persist across an instance reboot.  To disable cloud-init's
# network configuration capabilities, write a file
# /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg with the following:
# network: {config: disabled}
network:
    version: 2
    renderer: NetworkManager

# dont forget to 
# sudo netplan apply

```

## copy public SSH key 
```shell
# (on host machine)
ssh-copy-id -i ~/.ssh/id_rsa.pub YOUR_USER_NAME@IP_ADDRESS_OF_THE_SERVER
```

## run gunicorn on port 80
You can use authbind to achieve this. Install authbind

`sudo apt-get install authbind`

Then use auth bind to modify port 80 to make sure that port 80 can be used by non-superusers (aka without superuser privileges). Here are the three commands you can use to achieve this.

```shell
sudo touch /etc/authbind/byport/80
sudo chmod 500 /etc/authbind/byport/80
sudo chown USER /etc/authbind/byport/80
```
USER - can be any user on your system like bhatman or ubuntu or ec2-user.

NOTE: just change 80 to any desired port and it will work for any port. Use this responsibly my friend. :)

Now your gunicorn command will look something like this:

`authbind gunicorn -c gunicorn.conf wsgi:app`