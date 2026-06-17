# 🔄 Prototypes & Iterations

*Rule: Document major architectural shifts here. Explain what was tried, what succeeded, and what failed. This prevents future AI agents from suggesting paths we've already abandoned.*

---

## 🟢 Iteration 3: The Split-System (Current - v2)
**Status:** Active
- **Hardware:** Raspberry Pi 3B+ ("Brain"), ESP32 CYD ("Face"). Connected via USB.
- **Software:** Python (Pi) and C++ (CYD). Communicating via PySerial over USB.
- **Successes:** Fixes the "Pin Tetris" issue permanently. The Pi handles the complex logic and database queries; the CYD acts as a dumb terminal with zero UI latency. The rotary encoder push-button was disconnected entirely, successfully fixing the screen backlight flicker.

---

## 🔴 Iteration 2: Standalone ESP32 CYD (Abandoned)
**Status:** Merged/Archived
- **Hardware:** ESP32 CYD, M5Stack RFID 2 (I2C), Rotary Encoder, LEDs, Power Bank.
- **Software:** PlatformIO, C++, LVGL UI framework.
- **Successes:** Conceptually sound for a fully standalone device. LVGL UI looked great.
- **Failures / Reasons for Abandonment:** 
  - **"Pin Tetris":** The CYD has very few exposed, usable GPIO pins. 
  - **Hardware Conflicts:** Wiring the rotary encoder push-button caused the CYD backlight (GPIO 21) to flicker uncontrollably.
  - **Constraints:** Memory and processing constraints became apparent when trying to handle Wi-Fi, complex LVGL UI, NFC polling, and LED animations simultaneously on the ESP32.

---

## 🔴 Iteration 1: The Flipper Zero PC Setup (Abandoned)
**Status:** Deprecated
- **Hardware:** Flipper Zero (NFC Bridge), PC (Server/Database), ESP32 CYD (Display).
- **Software:** Python FastAPI on PC, WebSockets to CYD via Wi-Fi.
- **Successes:** Successfully proved the concept. It scanned tags and updated a web dashboard and the CYD screen.
- **Failures / Reasons for Abandonment:** 
  - Overly complex dependency on a PC running a server. 
  - WebSockets and Wi-Fi on the CYD were overkill and sometimes unstable.
  - Required the Flipper Zero to be tethered via USB to the PC. This was not viable as an immersive, standalone physical D&D prop on a gaming table.
