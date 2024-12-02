This README is meant for people who have little to no experience with working with a raspberry pi.



## OS installation guide
The Mothcam is programmed to run on Raspberry Pi OS Lite (32/64 bit) Debian Bookworm """"in the "other"menu """", which is recommended for optimal performance. This can be downloaded onto a micro-SD card using the [Raspberry Pi Imager](https://www.raspberrypi.com/software/). Before downloading the OS onto the micro-SD card, ensure that SSH is enabled and configure the Raspberry Pi for internet access by entering the Wi-Fi network name (SSID) and password by editing the "advanced options" in the Raspberry Pi Imager program. It is advisable to use a Wi-Fi network that allows you to monitor connected devices, such as a personal hotspot or router, to easily determine the Pi's IP address. Additionally, remember to set a hostname and password during the configuration process before installing the OS. Once the OS is installed, insert the micro-SD card into the Raspberry Pi and power it up to begin using the Pi.

The following steps can be followed to install an OS:
1. Install the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and open the application once it has been installed
2. Plug the micro-SD into your computer
3. Select the raspberry pi model you're using
4. Select the OS you want, Raspberry Pi OS Lite 32 bit (for zero) or 64 (for raspberry 2 and higher). This OS can by found in the "Raspberry pi OS (other)" menu
5. In the storage menu select the SD card which you want to use. All data on the SD card will be wiped by the imager before the OS is installed
6. Click on next and click on edit settings
7. In the general tab:
   a. Make a Hostname
   b. Set a username and password
   c. Enter the wifi settings (preferably of a hotspot)
   d. Set the timezone and keyboard settings to your preferred settings.
8. In the Services menu turn on SSH with password authentication.

## SSH instructions
How to use SSH to access a Raspberry Pi differs depending on your operating system, [this tutorial](https://www.onlogic.com/blog/how-to-ssh-into-raspberry-pi/) details the steps for Windows, Mac and Ubuntu. All methods require the IP of the Pi, if you are working on a monitor using an HDMI cable the IP can be found using the following command

Volgende -> aanpassen -> services
```
hostname -I
```
If you are using SSH the Pi's IP can be found on the router of the Wi-Fi network that was chosen in the advanced options of the Raspberry Pi Imager or when using a hotspot the IP can be found in the settings of the hotspot. The name of the pi will be the hostname you set in the Raspberry Pi Imager. 

## Running the timelapse script
To run the timelapse script manually the following sequence of commands can be used
```
cd Mothcam
python3 Timelapse_MP.py
```
To run the script automatically at a set time every day a crontab can be created. To open the crontab editing evironment type
```
crontab -e
```
At the bottom of this environment a new crontab can be added. The format of a crontab is as follows: minute (00-60), hour (00-24), day of month (00-31), month (00-12) and day of week (0-7) followed by the command you want the crontab to execute. To make the crontab run every minute or hour etc. use an * instead of a number in that spot. E.g. to run the Timelapse_AF.py script at 09.23 AM every day enter the following crontab
```
23 09 * * * /usr/bin/python3 /home/your_pi_hostname/Mothcam/Timelapse_MP.py
```
After entering the crontab press ctrl+X, Y and then enter to save the crontab. To check if the crontab installed successfully type
```
crontab -l
```
It can be useful to have the crontab write an automatic logfile in case any errors occur. To do this enter the following line directly behind the crontab
```
>> /path/to/logfile.log 2>&1
```
E.g.: 23 09 * * * /usr/bin/python3 /home/your_pi_hostname/Mothcam/Timelapse_AF.py >> /path/to/logfile.log 2>&1


