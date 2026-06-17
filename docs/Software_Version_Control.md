# Software Version Control & Architecture

*Rule: Update this document if the software stack (libraries, OS, language) changes.*

## 🧠 Version Control Rules & Rollback Guide

**IMPORTANT AI DIRECTIVE:** 
After making any significant changes or completing a conversation, you MUST commit the codebase to the local Git repository. 
- Use the command: `git add . && git commit -m "Your descriptive message"`

### How to Rollback
If a recent change breaks the system, you can rollback the project.
- **View History:** `git log --oneline`
- **Rollback 1 Iteration (temporary check):** `git checkout HEAD~1`
- **Rollback 2 Iterations (temporary check):** `git checkout HEAD~2`
- **Permanent Rollback (Hard Reset):** `git reset --hard HEAD~2` (WARNING: This deletes the last two commits entirely).

---

## 🛠 Software Architecture Breakdown

### 1. Raspberry Pi (The Brain) - Linux & Python
- **OS:** Raspberry Pi OS Lite (Headless).
- **Environment:** Python virtual environment (`venv`).
- **Autostart:** Uses a `systemd` service (`statblock-scanner.service`) that executes `bootstrap.sh`.
- **Logic Pipeline:**
  1. **Listen:** `scanner.py` monitors the M5Stack RFID 2 scanner via I2C (address 0x28).
  2. **Query:** Uses tag ID to look up the monster name in `nfc_mapping.json` and recursively searches the Obsidian markdown vaults.
  3. **Format:** Parses statblock markdown (supporting YAML frontmatter and Obsidian callout blocks) into a single line-delimited string (e.g. `NAME|AC|HP|ACTIONS\n`).
  4. **Transmit:** Automatically scans serial ports (`/dev/ttyUSB*` / `/dev/ttyACM*`) and transmits the payload via serial to the CYD display.
  5. **Feedback:** Controls WS2812B LEDs using `rpi_ws281x` (blue breathing animation while waiting, green pulse for success, red flash for errors).

### 2. Setup Tools
- **Host SD Preparer (`pi_brain/prepare_sd_card.sh`):** Installs project directories and enables systemd configurations directly on the mounted Pi SD card from a Linux PC.
- **Pi Installer (`pi_brain/install_pi.sh`):** Executed automatically by `bootstrap.sh` on the Pi's first boot to enable hardware interfaces (I2C, PWM) and fetch pip requirements.
-


### 2. ESP32 CYD (The Face) - C++ & PlatformIO/Arduino
- **Environment:** C++ (compiled via Arduino IDE or PlatformIO).
- **Logic Pipeline:**
  1. **Catch:** The `loop()` uses `Serial.available()` and `Serial.readStringUntil('\n')` to catch text from the Pi.
  2. **Parse & Store:** Splits the string based on delimiters.
  3. **Scroll:** Monitors the Rotary Encoder via hardware interrupts to adjust a `cursor_y` variable and redraw the TFT screen.
