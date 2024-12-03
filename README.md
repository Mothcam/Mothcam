# Mothcam
Mothcam is a repository with the scripts and configuration files designed to set up a Raspberry Pi to be used in a fully automated camera trap to monitor moth assemblages. The repositories are written with Python and make use of the [Picamera2 repository](https://github.com/raspberrypi/picamera2/tree/main). This repository has been tested with a Raspberry Pi4. This README will assume  the user has experience with Linux and Raspberry Pi. For those without Linux and/or Raspberry Pi experience README_beginners.md was made, this README contains additional basic instructions on how to set up a Raspberry Pi.

## Required equipment
```
- Raspberry Pi (with Raspberry Pi OS Lite (64-bit))
- Picamera module 3
- Ribbon cable*
- Computer/laptop**
- Monitor*** 
- Keyboard*** (& mouse****)

* = for a Raspberry Pi 4 a 22 pin to 22 pin cable is needed. For a Raspberry Pi zero W a 22 to 15 pin cable is needed.
** = When using SSH
*** = Without using SSH
**** = When using an OS with a desktop
```  

## Downloading the required repositories
Once the Pi has been started for the first time the following command needs to be run to install the most recent versions of all libraries on the Pi
```
sudo apt update
sudo apt upgrade
```
To install the Mothcam and Picamera2 repository the following series of commands can be used
```
sudo apt install git
git clone https://github.com/Mothcam/Mothcam.git
sudo apt install -y python3-picamera2 --no-install-recommends
sudo apt install python3-opencv
```
(use sudo apt install -y python3-picamera2 if you need the GUI version)

Lastly, it is recommended to install syncthing to synchronise the folders containing pictures of the moths to a personal device, such as a laptop or computer. If needed instructions on how to set up Syncthing can be found in the README_beginners.md file. 

## Editing the settings of the timelapse script
To start working with the timelapse script to take pictures certain settings might need to be changed depending on your preference. The standard settings are the ones used during testing which proved to be successful in the capturing of moths on camera.


To edit the settings of the timelapse script in an easy manner a configuration file can be used. In this project this config file is named mothconfig.json and can be edited using the following commands
```
cd Mothcam
nano mothconfig.json
```
Within this file the following settings can be found and adjusted:
-  stop_method: can be set to 'end_time', 'nrphotos' or 'either'. Determines whether the script stops due to reaching a set end time, a set number of photos or, when set to either, which setting is reached first.
-  end_time: sets the end time for the script when stop_method is set to 'end_time' or 'either'.
-  nrphotos: sets a fixed number of pictures the camera will take when stop_method is set to 'nrphotos' or 'either'.
-  save_all_images: if set to 'True' two folders will be made, one named Pictures and one named DEL. All pictures the script deems to similar to the previous will be moved into the DEL file. When this setting is set to 'False' all pictures which would otherwise be moved to DEL will be deleted permanently.

- quality: sets the JPEG quality level, can be set to a number from 0-95 with 95 being the highest quality.
- cam_number: sets the name of the camera in its pictures' file names. E.g. when set to 01 the file name would be as follows cam01_2024-12-02_113500_00001.jpg. With the following elements respectively following after: date, time at which the picture was taken, and the picture's number.
- camera_w: sets the width of the pictures in pixels.
- camera_h: sets the height of the pictures in pixels.

- noise_threshold: defines the minimum pixel value difference (0-255) to be considered as change. Setting this to a higher value reduces sensitivity to small changes (such as changes in lighting) but may miss subtle movements.
- contour_area_threshold: defines the minimum size (in pixels) of a connected area of changed pixels to be considered significant. This helps filter out very small or insignificant changes.
- min_change_percentage: defines the minimum percentage of pixels that needs to change for a picture to be saved. This helps filter out pictures with small changes such as a mosquito moving.
- max_change_percentage: defines the maximum percentage of pixels that needs to change for a picture to be saved. This helps filter out pictures with big changes such as leaves falling into the trap.

## Running the timelapse script
After editing the settings the script to take pictures can be run. This script is called Timelapse_MP.py. It can be run either manually using the python3 command or automatically by setting up a crontab. If needed, additional explaination on both of these methods can be found in the README_beginners.md file. 

## Installing an RTC unit
> [!Warning]
> The RTC module used in these instructions was a DS1307 module, these instructions might not work on another type of RTC module.

To make sure the Pi starts the script at the correct time an external RTC (real time clock) unit was used.
First the I2C interface has to be enabled. Open the Raspberry Pi configuration tool:
```
sudo raspi-config
```
Navigate to interface options then to I2C and enable the I2C. Once this is done exit the configuration tool and reboot the system with
```
sudo reboot
```
Now install the I2C tools with the following command and reboot the Pi afterwards
```
sudo apt install -y i2c-tools python3-smbus
```
Once the tools have been installed use the i2cdetect command to verify the RTC module is being detected
```
i2cdetect -y 1
```
In the output of this command look for an adress, typically this is 0x68, this adress indicates the DS1307 module is connected. 
Next the RTC kernel module needs to be loaded and the RTC needs to be added to the system
```
sudo modprobe rtc-ds1307
echo "ds1307 0x68" | sudo tee /sys/class/i2c-adapter/i2c-1/new_device
```
It should now be possible to read the RTC module using
```
sudo hwclock -r
```
If needed the RTC module can be synchronized to the Pi's system clock using
```
sudo hwclock -w
``` 
In order to have load the RTC automatically at boot /boot/firmware/config.txt needs to be edited. This can be done by entering the entering the following command
```
sudo nano /boot/firmware/config.txt
```
At the end of this file add the following line
```
dtoverlay=i2c-rtc,ds1307
```
After adding the line save and exit the file with Ctrl+O, Enter, Ctrl+X and reboot the Pi

Optionally the Pi's fake hardware clock can be disabled if this is interfering with the RTC module. In order to do this run the following commands
```
sudo systemctl disable fake-hwclock 
sudo apt remove -y fake-hwclock 
sudo rm /etc/adjtime
```
Once the RTC is fully set up reboot the Pi one more time and check if the RTC is working by using
```
sudo hwclock -r
```
