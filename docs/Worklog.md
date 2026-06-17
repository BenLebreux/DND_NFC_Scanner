# Worklog

*Rule: AI agents must log all completed actions, code changes, and resolved bugs here. Add new entries to the top. Move old entries to `Archive/Worklog_Archive.md` when necessary.*

### 2026-06-15
- **Action:** Upgraded project "Brain" specs to support Raspberry Pi 4.
- **Action:** Implemented production `scanner.py` containing live I2C RFID polling (using `mfrc522-i2c`), dynamic serial port scanning, robust local Obsidian notes database search and recursive crawler, and NeoPixel (WS2812B) color-coded status pulses/breathing animations.
- **Action:** Wrote automated first-boot installation sequence (`bootstrap.sh` and `install_pi.sh`) with systemd service file (`statblock-scanner.service`) to build software venv and disable audio/PWM conflicts.
- **Action:** Developed `prepare_sd_card.sh` script to run on host Linux PC for writing code, settings, and enabling autostart directly on a mounted SD card.
- **Action:** Initialized Git repository for the project and committed the changes.

### 2026-06-13 (Part 3)
- **Action:** Added hardware interrupt logic to `cyd_display.ino` to read rotary encoder turns and adjust a `scroll_y` offset.
- **Action:** Updated `hardware_test.py` to send a massive, delimited Goblin statblock payload to simulate overflow text for the scrolling test.

### 2026-06-13 (Part 2)
- **Action:** Added `systemd` autostart configurations to `Software_Version_Control.md` to establish how the Python script launches on boot.
- **Action:** Wrote `pi_brain/hardware_test.py` to test I2C NFC polling, PWM LED control, and PySerial communication on the Raspberry Pi.
- **Action:** Rewrote `cyd_display.ino` to remove Wi-Fi and act as a dumb USB Serial terminal.

### 2026-06-13
- **Action:** Created the ultimate Project "Spine" documentation structure.
- **Action:** Initialized `docs/` folder and populated `Source_of_Truth.md`, `Decision_Log.md`, `Hardware_Ledger.md`, `Software_Version_Control.md`, and `Prototypes_and_Iterations.md`.
- **Action:** Initialized Git repository for the project to enable the "rollback to two iterations ago" feature.
