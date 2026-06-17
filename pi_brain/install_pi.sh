#!/bin/bash

# Ensure this script runs as root
if [ "$EUID" -ne 0 ]; then
  echo "[!] Please run as root (using sudo)."
  exit 1
fi

echo "=================================================="
# Show a fancy ASCII banner to make it feel premium!
echo "   D&D NFC Campaign Tool - Pi 4 Installer v2"
echo "=================================================="

# 1. Detect Boot Config file (Pi 4 OS Bookworm uses /boot/firmware/config.txt)
BOOT_CONFIG="/boot/firmware/config.txt"
if [ ! -f "$BOOT_CONFIG" ]; then
  BOOT_CONFIG="/boot/config.txt"
fi
echo "[*] Using boot configuration file: $BOOT_CONFIG"

# 2. Configure I2C
echo "[*] Checking I2C configuration..."
if grep -q "dtparam=i2c_arm=on" "$BOOT_CONFIG"; then
  echo "    -> I2C already enabled in config."
else
  echo "    -> Enabling I2C in boot configuration..."
  echo "dtparam=i2c_arm=on" >> "$BOOT_CONFIG"
fi

# 3. Configure PWM & Disable Onboard Audio (Required for WS2812B LEDs on GPIO 18)
echo "[*] Checking audio/PWM configuration..."
# Disable dtparam=audio
sed -i 's/^dtparam=audio=on/#dtparam=audio=on/' "$BOOT_CONFIG"
if grep -q "^dtparam=audio=off" "$BOOT_CONFIG"; then
  echo "    -> Analog audio already disabled in config."
else
  echo "    -> Disabling analog audio to free hardware PWM..."
  echo "dtparam=audio=off" >> "$BOOT_CONFIG"
fi

# Blacklist audio kernel module
BLACKLIST_FILE="/etc/modprobe.d/snd-blacklist.conf"
if [ -f "$BLACKLIST_FILE" ] && grep -q "snd_bcm2835" "$BLACKLIST_FILE"; then
  echo "    -> Audio driver blacklist already configured."
else
  echo "    -> Blacklisting snd_bcm2835 audio module..."
  echo "blacklist snd_bcm2835" >> "$BLACKLIST_FILE"
fi

# 4. Install System Prerequisites
echo "[*] Updating package index and installing dependencies..."
apt-get update -y
apt-get install -y python3-pip python3-venv i2c-tools python3-dev

# 5. Initialize clean Virtual Environment (Pi 4 arm64 architecture)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "[*] Project directory: $PROJECT_DIR"
cd "$PROJECT_DIR"

echo "[*] Recreating Python virtual environment..."
rm -rf venv
python3 -m venv venv

echo "[*] Activating virtual environment & installing Python modules..."
source venv/bin/activate
pip install --upgrade pip
# Install exact requirements:
# - smbus2: I2C bus driver
# - pyserial: serial communication with CYD
# - rpi_ws281x: NeoPixel driver (requires root access)
# - mfrc522-i2c: I2C MFRC522 driver
# - pyyaml: parsing frontmatter in Obsidian notes
pip install smbus2 pyserial rpi_ws281x mfrc522-i2c pyyaml

echo "[*] Installation completed successfully!"
echo "[*] Note: A reboot is required to apply the I2C and audio blacklist settings."
