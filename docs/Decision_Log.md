# 📜 Decision Log

*Rule: Always add new decisions to the top of this list. Move very old entries to `Archive/Decision_Log_Archive.md` when this file exceeds 50 entries.*

| Date | Context | Decision | Rationale |
| :--- | :--- | :--- | :--- |
| **2026-06-13** | The project iterated rapidly from a Flipper Zero hack to a dedicated hardware prop. Documentation was fragmented across folders. | **Establish Unified Documentation & Rollback Brain** | Created a single `docs/` structure with strict AI update rules and merged the project folders. Initialized a local Git repository (or planned to) to provide a guaranteed 2-iteration rollback safety net. |
| **2026-06-13** | The rotary encoder push button (SW) caused hardware-level interference with the CYD's screen backlight (GPIO 21). | **Disable Rotary Encoder Button** | Leaving the SW pin disconnected completely prevents the backlight flickering issue. UI navigation will rely entirely on the rotary twisting action and the touchscreen. |
| **2026-06-13** | The standalone ESP32 CYD struggled with Wi-Fi management, complex processing, and "Pin Tetris" hardware conflicts. | **Adopt Split Architecture (Pi + CYD)** | The Raspberry Pi handles heavy lifting (I2C NFC scanning, database queries, PWM LEDs). The CYD acts solely as a dumb terminal receiving parsed text via USB Serial, eliminating latency and pin conflicts. |
| **2026-06-02** | Needed to select a UI framework and firmware stack for the ESP32 CYD to ensure a premium feel. | **Select PlatformIO, C++, and LVGL** | PlatformIO provides a robust environment. LVGL provides beautiful, responsive UI capabilities which are crucial for the "premium" feel of a physical D&D prop. |
| **2026-06-02** | Selecting core hardware for a D&D prop. | **Use CYD, M5Stack RFID 2, Rotary Encoder, WS2812B LEDs** | The CYD provides a built-in screen. The M5Stack unit is neatly packaged and uses I2C. The encoder and LEDs add tactile and visual flair ("vibes"). |
