#!/bin/bash

# Ensure this script is run as root on the host PC
if [ "$EUID" -ne 0 ]; then
  echo "[!] This script modifies root-owned files on the SD card."
  echo "[!] Please run with sudo: sudo ./prepare_sd_card.sh"
  exit 1
fi

echo "=================================================="
echo "    D&D NFC Campaign Tool - SD Card Preparer      "
echo "=================================================="

# 1. Locate the mounted SD card root filesystem
echo "[*] Scanning for mounted Raspberry Pi root filesystem..."
ROOT_MOUNT=""
for mount in /run/media/$SUDO_USER/* /run/media/*/* /media/$SUDO_USER/* /media/*/* /mnt/*; do
  if [ -d "$mount/etc/systemd/system" ] && [ -d "$mount/home" ]; then
    ROOT_MOUNT="$mount"
    break
  fi
done

if [ -z "$ROOT_MOUNT" ]; then
  echo "[!] ERROR: Could not auto-detect a mounted Raspberry Pi root partition."
  echo "    Please make sure the SD card is plugged in and mounted."
  echo "    Alternatively, enter the path to the mounted root partition manually"
  echo "    (e.g., /run/media/username/rootfs):"
  read -r -p "Path: " MANUAL_MOUNT
  if [ -d "$MANUAL_MOUNT/etc/systemd/system" ]; then
    ROOT_MOUNT="$MANUAL_MOUNT"
  else
    echo "[!] ERROR: Invalid root partition path. Exiting."
    exit 1
  fi
fi

echo "[+] Detected Raspberry Pi root partition at: $ROOT_MOUNT"

# 2. Detect the username configured on the Pi
PI_USER=$(ls "$ROOT_MOUNT/home" | grep -v "lost+found" | head -n 1)
if [ -z "$PI_USER" ]; then
  echo "[!] ERROR: No user directory found in $ROOT_MOUNT/home/."
  echo "    Did you configure a user in Raspberry Pi Imager?"
  exit 1
fi

echo "[+] Detected custom Pi username: $PI_USER"

# 3. Setup paths
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PI_PROJECT_DIR="$ROOT_MOUNT/home/$PI_USER/NFC_Campaign_Tool"

echo "[*] Local project path: $LOCAL_DIR"
echo "[*] Target SD Card path: $PI_PROJECT_DIR"

# 4. Copy project files using rsync (excluding python/node cache/venv)
echo "[*] Copying project files to SD Card..."
mkdir -p "$PI_PROJECT_DIR"
rsync -av --delete \
  --exclude="venv" \
  --exclude="node_modules" \
  --exclude=".git" \
  --exclude="*.pyc" \
  --exclude="__pycache__" \
  "$LOCAL_DIR/" "$PI_PROJECT_DIR/"

# 5. Fix permissions to match the Pi user
echo "[*] Matching file ownership to Pi user..."
PI_UID=$(stat -c '%u' "$ROOT_MOUNT/home/$PI_USER")
PI_GID=$(stat -c '%g' "$ROOT_MOUNT/home/$PI_USER")
chown -R $PI_UID:$PI_GID "$PI_PROJECT_DIR"

# Make the scripts executable
chmod +x "$PI_PROJECT_DIR/pi_brain/bootstrap.sh"
chmod +x "$PI_PROJECT_DIR/pi_brain/install_pi.sh"
chmod +x "$PI_PROJECT_DIR/pi_brain/scanner.py"

# 6. Configure systemd service on the SD Card
echo "[*] Writing systemd service file..."
SERVICE_DEST="$ROOT_MOUNT/etc/systemd/system/statblock-scanner.service"
sed "s|{{PROJECT_DIR}}|/home/$PI_USER/NFC_Campaign_Tool|g" "$LOCAL_DIR/pi_brain/statblock-scanner.service" > "$SERVICE_DEST"
chmod 644 "$SERVICE_DEST"

# 7. Enable systemd service on the SD Card
echo "[*] Enabling systemd service on the SD Card..."
WANTS_DIR="$ROOT_MOUNT/etc/systemd/system/multi-user.target.wants"
mkdir -p "$WANTS_DIR"
ln -sf "/etc/systemd/system/statblock-scanner.service" "$WANTS_DIR/statblock-scanner.service"

echo "=================================================="
echo "   🎉 SUCCESS! The SD Card is ready!"
echo "=================================================="
echo "1. Safely eject the micro SD card from your PC."
echo "2. Insert it into your Raspberry Pi 4."
echo "3. Connect the Pi to the CYD display via USB."
echo "4. Power on the Pi 4 (Ensure it has internet access)."
echo ""
echo "The Pi will boot, run the install script automatically,"
echo "and then reboot itself. On the next boot, the scanner"
echo "will be running in the background and waiting for scans!"
echo "=================================================="
