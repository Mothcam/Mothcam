# Mothcam
Mothcam is a repository with the scripts and config files designed to transform the [LedEmmer](https://www.vlinderstichting.nl/wat-wij-doen/meetnetten/meetnet-nachtvlinders/ledemmers/) into a Mothcam camera trap, enabling fully automated monitoring of moth assemblages. The repositories are written with Python and make use of the [Picamera2 repository](https://github.com/raspberrypi/picamera2/tree/main). This repository has been tested with a Raspberry Pi4 and a Raspberry Pi Zero W. This README will assume that the user has zero experience with Linux and Raspberry Pi. Therefor this README will provide step-by-step instructions to guide any user through setting up the Mothcam.

## Required equipment
```
- Raspberry Pi 
- Picamera module 3
- Ribbon cable*
- (LISIPAROI) halo LEDs
- Computer/laptop**
- Monitor*** 
- Keyboard*** (& mouse****)

* = for a Raspberry Pi 4 a 22 pin to 22 pin cable is needed. For a Raspberry Pi zero W a 22 to 15 pin cable is needed.
** = When using SSH
*** = Without using SSH
**** = When using an OS with a desktop
```  
## OS installation guide
The Mothcam is programmed to run on Raspberry Pi OS Lite (32/64 bit) Debian Bookworm""""in the "other"menu """", which is recommended for optimal performance. This can be downloaded onto a micro-SD card using the [Raspberry Pi Imager](https://www.raspberrypi.com/software/). Before downloading the OS onto the micro-SD card, ensure that SSH is enabled and configure the Raspberry Pi for internet access by entering the Wi-Fi network name (SSID) and password by editing the "advanced options" in the Raspberry Pi Imager program. It is advisable to use a Wi-Fi network that allows you to monitor connected devices, such as a personal hotspot or router, to easily determine the Pi's IP address. Additionally, remember to set a hostname and password during the configuration process before installing the OS. Once the OS is installed, insert the micro-SD card into the Raspberry Pi and power it up to begin using the Pi.

The following steps can be followed to install an OS:
1. Install the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and open the application once it has been installed
2. Plug the micro-SD into your computer
3. Select the raspberry pi model you're using
4. Select the OS you want, Raspberry Pi OS Lite 32 bit (for zero) or 64 (for raspberry 2 and higher). This OS can by found in the "Raspberry pi OS (other)" menu.
5. In the storage menu select the SD card which you want to use. All data on the SD card will wiped by the imager before the OS is installed
6. Click on next and click on edit settings
7. In the general tab:
   a. Make a Hostname
   b. Set a username and password
   c. Enter the wifi settings (preferably of a hotspot)
   d. Set the timezone and keyboard settings to your preferred settings.
8. In the Services menu turn on 
## SSH instructions
How to use SSH to access a Raspberry Pi differs depending on your operating system, [this tutorial](https://www.onlogic.com/blog/how-to-ssh-into-raspberry-pi/) details the steps for Windows, Mac and Ubuntu. All methods require the IP of the Pi, if you are working on a monitor using an HDMI cable the IP can be found using the following command

Volgende -> aanpassen -> services
```
hostname -I
```
If you are using SSH the Pi's IP can be found on the router of the Wi-Fi network that was chosen in the advanced options of the Raspberry Pi Imager or when using a hotspot the IP can be found in the settings of the hotspot. The name of the pi will be the hostname you set in the Raspberry Pi Imager. 

## Downloading the required repositories
Once the Pi has been started for the first time the following command needs to be run to install the most recent versions of all libraries on the Pi
```
sudo apt update
sudo apt upgrade
```
To install the Mothcam and Picamera2 repository command can be used
```
sudo apt install git
git clone https://github.com/Mothcam/Mothcam.git
sudo apt install -y python3-picamera2
sudo apt install python3-opencv
sudo apt install python3-numpy
```

Lastly, it is recommended to install syncthing to synchronise the Pictures folder to a personal database. Here are the instructions to install syncthing

```
sudo apt install syncthing
```
run syncthing by typing
```
syncthing
```
After the initial run, use ctrl+c to kill the application. Type
```
cd ~
nano ~/.config/syncthing/config.xml
```
to start editing the config file. In the config file, replace "< address >127.0.0.1:8384< / address >" with the following in row 46. With ctrl + / you can jump to this row. 
```
<address>0.0.0.0:8384</address>
```
> [!WARNING]
> Changing the address to 0.0.0.0 means any and all other devices are able access the pi's syncthing page when syncthing is running on the pi. You can have syncthing running all the time by using the following commands (replace "user" with the username)

````
sudo systemctl enable syncthing@user
sudo systemctl start syncthing@user
````

Now Syncthing is ready to be used, open synthing on your device and open the syncthing page of the Pi by typing the following into your browser
```
[PI-IP-address]:8384
```
go to "add external device" and enter the device ID of the other device, this ID can be found in the actions menu on the top right of the page. To access syncthing on your device install [Syncthing](https://syncthing.net/downloads/) and open the program on your device.
Once the devices have added each other it's possible to share folders with each other. To share a folder go to "Add folder" on the syncthing page of the Pi. for the Map location enter 
```
~/Mothcam/Pictures/
```
Click on the folder and tap edit and go to the share page. In this page you can select with which added device the folder will be shared.
> [!WARNING]
> The folder will become shared this means if you delete files in this folder on one device, they will be deleted on the other device aswell. Working similarly to a shared OneDrive folder.

## Editing the settings of the timelapse script
To edit the settings of the timelapse script in an easy manner a config file can be used. This config file can be edited using the following commands
```
cd Mothcam
nano mothconfig.json
```
Within this file the following settings can be found and adjusted:
-  GPIO: this setting can be set to True or False depending on whether the GPIO pins on the Pi are being used (True) or not (False).
-  start_hhmm: determines the start time of the script. E.g. the script should start at 9.23 AM, this setting will then be set to 09:23.
- end_hhmm: determines the end time of the script. This setting follows the same format as the start_hhmm setting.
- camera_w and camera_h: these settings are used to set the size of the pictures taken. E.g. a resolution of 3040x4056 would be set by adjusting the camera_w setting to 3040 and the camera_h setting to 4056.
- autofocus: this setting can be set to True or False depensing on whether you want autofocus turned on (True) or off (False)
- focus_dist_m: if autofocus is turned off this setting determines the focus distance the camera will have in meters. E.g. if the camera should focus on a 5 cm distance this setting will be set to 0.05.
- interval: this sets the interval between pictures in seconds. The minimum time needed is around 2 seconds.

## Running the timelapse script
To run the timelapse script manually the following sequence of commands can be used
```
cd Mothcam
python3 Timelapse_AF.py
```
To run the script automatically at a set time every day a crontab can be created. To open the crontab editing evironment type
```
crontab -e
```
At the bottom of this environment a new crontab can be added. The format of a crontab is as follows: minute (00-60), hour (00-24), day of month (00-31), month (00-12) and day of week (0-7) followed by the command you want the crontab to execute. To make the crontab run every minute or hour etc. use an * instead of a number in that spot. E.g. to run the Timelapse_AF.py script at 09.23 AM every day enter the following crontab
```
23 09 * * * /usr/bin/python3 /home/your_pi_hostname/Mothcam/Timelapse_AF.py
```
After entering the crontab press control X, Y and then enter to save the crontab. To check if the crontab installed successfully type
```
crontab -l
```
It can be useful to have the crontab write an automatic logfile in case any errors occur. To do this enter the following line directly behind the crontab
```
>> /path/to/logfile.log 2>&1
```
E.g.: 23 09 * * * /usr/bin/python3 /home/your_pi_hostname/Mothcam/Timelapse_AF.py >> /path/to/logfile.log 2>&1
```

