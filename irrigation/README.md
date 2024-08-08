# The Gello Irrigation System

This set of scripts control the irrigation system of Gello, via a raspberry pi and a set of sensors and electro-valves
The principle is a python script that operates the GPIO pins on the raspberry pi, which in turn either read sensors or operate relays to open or close water valves
The script is daemonized on the raspberry pi via a systemd service, which basically just runs the script with some default options

## Usage

On the rpi, the python script should be in the folder ~/git/gello3000/irrigation and the service should be in /etc/systemd/system/.
To initialize, clone the repo into a 'git' folder in the home with the following commands and move the service to the right folder and enable it:
```bash
cd
mkdir git && cd git
git clone https://github.com/femi86/gello3000.git
sudo mv gello3000/irrigation/water.service /etc/systemd/system/
sudo systemctl enable water.service
sudo systemctl start water.service
```
There is nothing to do, except when changes are made, described in the following section

## making changes

When making changes, as the folder on the rpi is tracked by git, a script can be modified from anywhere, pushed to origin, and then it can be pulled to the rpi.

When updating the script on the rpi, as there is some caching of the service, the following needs to be done:

1. update the script and pull from remote
```bash
git pull
```
2. to change the systemd unit (i.e. if wanting to change the time or something), you can edit the file /etc/systemd/system/water.service

3. if the systemd unit was changed, a the systemd needs to be reloaded
```bash
sudo systemctl daemon-reload
```
4. restart the service 
```bash
sudo systemctl restart water.service
```

## Script working principle

The python script itself is structured withe parse-args library, therefore it can be run via shell using the --help argument to get information on the various parameters.

currently, as of august 2024, the only implemented rpi operator is the electrovalve, so the main change that can be done is to vary the opening time

