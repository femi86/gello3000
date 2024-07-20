# The Gello Irrigation System

This set of scripts control the irrigation system of Gello, via a raspberry pi and a set of sensors and electro-valves
The principle is a python script that operates the GPIO pins on the raspberry pi, which in turn either read sensors or operate relays to open or close water valves
The script is daemonized on the raspberry pi via a systemd service, which basically just runs the script with some default options

## Usage

On the rpi, the script is in the folder ~/git/gello3000/irrigation and the service is /etc/systemd/system/water.service. 
There is nothing to do, except when changes are made, described in the following section

## making changes

When making changes, as the folder on the rpi is tracked by git, a script can be modified from anywhere, pushed to origin, and then it can be pulled to the rpi.

When updating the script on the rpi, as there is some caching of the service, the following needs to be done:

1. update the script and pull from remote
```bash
git pull
```
3. if the systemd unit was changed, a the systemd needs to be reloaded
```bash
sudo systemctl daemon-reload
```
4. restart the service 
```bash
sudo systemctl restart water.service
```
