import os
import subprocess
import time
import json

def set_cpu_governor(governor):
    os.system(f"echo {governor} | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor")

def disable_hdmi():
    os.system("/usr/bin/tvservice -o")

def enable_hdmi():
    os.system("/usr/bin/tvservice -p")

def set_wifi_power_save(mode):
    os.system(f"sudo iw wlan0 set power_save {mode}")

def check_wifi_power_save():
    result = subprocess.check_output(["iwconfig", "wlan0"]).decode()
    return "Power Management:on" in result

def control_usb_power(action):
    hubs = [
       '2',
       '1-1',
    ]
    for hub in hubs:
       os.system(f"sudo uhubctl -l {hub} -a {action}")

def load_config(config_file='mothconfig.json'):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config

def main():
    print("Raspberry Pi Power Optimization Script")
    
    # Load configuration
    settings = load_config()
    
    # Set CPU governor
    governor = settings.get('cpu_governor', 'powersave')
    set_cpu_governor(governor)
    print(f"CPU governor set to {governor}")

    # Control HDMI
    if settings.get('disable_hdmi', True):
        disable_hdmi()
        print("HDMI output disabled")
    
    # Set WiFi power saving
    if settings.get('wifi_power_save', True):
        set_wifi_power_save("on")
        if check_wifi_power_save():
            print("WiFi power saving enabled successfully")
        else:
            print("Failed to enable WiFi power saving")
    
    # Control USB power
    if settings.get('disable_usb', True):
        control_usb_power("off")
        print("USB ports powered off")

    # Monitor temperature
    try:
        while True:
            temp = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
            print(f"Current temperature: {temp.strip()}")
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nExiting...")
        # Restore settings
        set_cpu_governor("ondemand")
        enable_hdmi()
        set_wifi_power_save("off")
        control_usb_power("on")
        print("Settings restored to default")

if __name__ == "__main__":
    main()
