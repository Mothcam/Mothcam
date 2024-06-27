# Mothcam
Mothcam is repository with the scripts and config files designed to transform the [LedEmmer](https://www.vlinderstichting.nl/wat-wij-doen/meetnetten/meetnet-nachtvlinders/ledemmers/) into a Mothcam camera trap, enabling the fully automated monitoring of moth assemblages. The repositories are written with Python and make use of the [Picamera2 repository](https://github.com/raspberrypi/picamera2/tree/main). This repository has been tested with a Raspberry Pi4 and a Raspberry Pi Zero W. This README will assume that the user will have absolutely zero experience with Linux and Raspberri Pi. therefore this README will provide step-by-step instructions to guide any user through setting up the Mothcam.


## Required equipment
```
- Raspberry Pi 
- Picamera 3
- Ribbon cable
- (LISIPAROI) halo LEDs
- Computer with PuTTY*
- Monitor**  
- Keyboard (& mouse***)**

* = When using SSH
** = Without using SSH
*** = When using an OS with a desktop
```
[PuTTY](https://www.putty.org/) install link  
## Noob Installation Guide
The Mothcam is programmed to run on Raspberry Pi OS Lite (32/64 bit) Debian Bookworm, which is recommended for optimal performance. Before downloading the OS onto the micro-SD card, ensure that SSH is enabled and configure the Raspberry Pi for internet access by entering the Wi-Fi network name (SSID) and password. It is advisable to use a Wi-Fi network that allows you to monitor connected devices, such as a personal hotspot or router, to easily determine the Pi's IP address. Additionally, remember to set a hostname and password during the configuration process before installing the OS. Once the OS is installed, insert the micro-SD card into the Raspberry Pi and power it up to begin using the Pi.

<!-- # About SSH -->

# Download Repositories
Once the has started up for the first time the following command need to ran to install the most recent versions of the libraries:
```
sudo apt update
sudo apt upgrade
```
To install the Mothcam repository and other required repositories the following command has to be used:
```
sudo apt install git
git clone https://github.com/Mothcam/Mothcam.git
sudo apt install -y python3-picamera2
```

Lastly, it is recommended to install syncthing to synchronise the Pictures folder to a personal database. Here are the instructions to install syncthing:

```
sudo apt install syncthing
```
run syncthing by typing:
```
syncthing
```
After the initial run, use ctrl+c to kill to application. Type
```
cd ~
nano ~/.config/syncthing/config.xml
```
to start editing the config file. In the config file, replace "<< address >127.0.0.1:8384< / address >" with 
```
<address>0.0.0.0:8384</address>
```
> [!WARNING]
> Changing the address to 0.0.0.0 means any and all other devices are able access the pi's syncthing page.

Now Syncthing is ready to be used, open synthing on your device and open the syncthing page of the pi by typing the following in your browser
```
[PI-IP-address]:8384
```
go to add external device and enter the device ID of the other device, this ID can be found in the actions menu on the top right of the page.
Once the devices have added eachother it's possible to share folders with eachother. To share a folder go to "Add folder" on the syncthing page of the pi. for the Map locaiton enter 
```
~/Mothcam/Pictures/
```
Click on the folder and tap edit and go to the share page. In this page you can select with which added device the folder will be shared.
> [!WARNING]
> The folder will become shared this means if you delete files in this folder on one device, they will be deleted on the other device aswell. So, yes, it works similar to a shared folder in OneDrive.

