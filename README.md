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


<!-- # About SSH -->

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
run syncthing by typing:
```
syncthing
```
After the initial run, use ctrl+c to kill to application. Type
```
cd ~
nano ~/.config/syncthing/config.xml
```
to start editing the config file. In the config file, replace "<address>127.0.0.1:8384</address>" with 
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

