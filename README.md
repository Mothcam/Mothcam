#Mothcam
Mothcam is repository with the scripts and config files meant for turning the [LedEmmer](https://www.vlinderstichting.nl/wat-wij-doen/meetnetten/meetnet-nachtvlinders/ledemmers/) into a Mothcam camera trap for monitoring moth assemblages. The repositories are written with Python and make use of the [Picamera2 repository](https://github.com/raspberrypi/picamera2/tree/main). This repository has been tested with a Raspberry Pi4 and a Raspberry Pi Zero W.

## Required equipment
```
- Raspberry Pi 
- Picamera 3
- Ribbon cable
- Computer with PuTTY*
- Monitor**  
- Keyboard (& mouse***)**

* = When using SSH
+ = Without using SSH
# = When using an OS with a desktop
```
[PuTTY](https://www.putty.org/) install link  
## Noob Installation Guide
The Mothcam is programmed with the Raspberry pi OS Lite (32/64 bit) Debian Bookworm. Therefore, it is recommended to use this OS while running the Mothcam. 

Before downloading the OS onto the micro-SD card make the SSH is turned on and the Pi has the access to the internet by filling in the field for Wi-Fi network name and password. It is recommended to connect enter Wi-Fi connection information of source in which the connected devices can viewed, such as a personal hotspot or router, since it can be used to figure out the IP-address. It's also imporant to remember the Hostname and password which can be set before installing the OS. After installing the OS, the micro-SD can by put into the Pi and the Pi can now be used.


# About SSH

# Download Repositories
Once the has started up for the first time the following command need to ran to install the most recent versions of the libraries:
```
sudo apt update
sudo apt upgrade
```
To install the Mothcam Repository the following command has can be used:
```
sudo apt install git
git clone  https://Mothcam:  PERSONAL ACCESS CODE  @github.com/Mothcam/Mothcam.git
```
Other required repositories 
```
Picamera2: sudo apt install -y python3-picamera2
```

Lastly, it is recommended to install syncthing to synchronise the Pictures folder to a personal database. The following steps can be followed to install syncthing:

```
sudo apt install syncthing
```
