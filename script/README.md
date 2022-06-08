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
```
