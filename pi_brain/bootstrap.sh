#!/bin/bash

# Ensure this script runs as root
if [ "$EUID" -ne 0 ]; then
  echo "[!] Please run as root (using sudo)."
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SENTINEL="/var/lib/statblock-scanner-installed"

echo "[*] D&D Statblock Scanner Bootstrapping..."
echo "[*] Working directory: $PROJECT_DIR"

if [ ! -f "$SENTINEL" ]; then
  echo "[!] Sentinel file not found. Commencing automated first-boot installation..."
  
  # Run installer
  chmod +x "$SCRIPT_DIR/install_pi.sh"
  "$SCRIPT_DIR/install_pi.sh"
  
  # Check if installation succeeded
  if [ $? -eq 0 ]; then
    echo "[*] Installation finished successfully. Writing sentinel..."
    touch "$SENTINEL"
    echo "[*] Rebooting system in 5 seconds to apply hardware profiles..."
    sleep 5
    reboot
  else
    echo "[!] Critical Error: First-boot installation failed. Retrying on next boot."
    exit 1
  fi
else
  echo "[*] Sentinel found. Running D&D Statblock Scanner..."
  cd "$PROJECT_DIR"
  # Start the Python scanner program using the virtual environment interpreter
  exec "$PROJECT_DIR/venv/bin/python" "$SCRIPT_DIR/scanner.py"
fi
