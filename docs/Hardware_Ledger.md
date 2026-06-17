# 🔌 Hardware Ledger (v2 Architecture)

*Rule: Keep this file strictly updated if pins change, power sources change, or new hardware is added.*

## 🔗 The Core Link (USB Serial)
- **Connection:** Raspberry Pi USB-A Port ⟷ Micro-USB Port on ESP32 CYD.
- **Power:** The Pi supplies stable 5V power to the CYD.
- **Data:** Establishes a high-speed, two-way serial pipeline (typically `/dev/ttyUSB0` on the Pi).

---

## 🧠 The Brain: Raspberry Pi 4 (or Pi 3B+)
- **OS:** Headless Raspberry Pi OS Lite (configured with customization via Raspberry Pi Imager).
- **Core Function:** Handles all complex logic (I2C scanning, Obsidian queries, PWM LED control).

### GPIO Pinouts (40-Pin Header)
*Note: Pin numbers refer to physical board pins, not GPIO numbers.*

| Component | Pin Function | Pi Physical Pin | Pi GPIO |
| :--- | :--- | :--- | :--- |
| **M5Stack RFID 2 (I2C)** | 5V Power (Red) | Pin 4 | - |
| | GND (Black) | Pin 9 | - |
| | SDA (White) | Pin 3 | GPIO 2 |
| | SCL (Yellow) | Pin 5 | GPIO 3 |
| **WS2812B LED Ring** | 5V Power (Red) | Pin 2 | - |
| | GND (Black/White) | Pin 6 | - |
| | DIN (Green) | Pin 12 | GPIO 18 (PWM0) |

*(Software Note: Onboard Pi audio must be disabled in `/boot/firmware/config.txt` to prevent PWM conflicts with the LEDs on GPIO 18.)*



---

## 📺 The Face: ESP32 CYD (Cheap Yellow Display)
- **Model:** ESP32-2432S028
- **Core Function:** A "dumb terminal" displaying text sent via Serial, handling local scrolling via hardware interrupts.

### Breakout Connections
The Rotary Encoder connects directly to the CYD `CN1` (middle-right) port exclusively. 
*(Note: 2.54mm breakaway headers can be soldered directly into the plated through-holes next to the JST sockets.)*

| Component | Pin Function | CYD CN1 Pin | CYD GPIO | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Rotary Encoder** | VCC (+) | Pin 1 | 3.3V | |
| | GND | Pin 4 | GND | |
| | DT | Pin 2 | GPIO 27 | |
| | CLK | Pin 3 | GPIO 22 | |
| | SW (Button) | *Disconnected* | *Disconnected* | Prevents GPIO 21 backlight flicker. |

---

## 🗺️ Pi 4 Physical Wiring Diagram

Here is a visual map of the 40-pin GPIO header showing exactly where to connect the **RFID 2 Scanner**, **WS2812B LED Ring**, and the **Cooling Fan**:

```
                       RASPBERRY PI 4 GPIO HEADER
                      +-----------------------------+
             3.3V [1] |  x  x  | [2]  5V -----------+--> [VCC] WS2812B LED Ring
    [SDA] RFID 2 <----+--[3]  x  x  | [4]  5V -----------+--> [VCC] M5Stack RFID 2
    [SCL] RFID 2 <----+--[5]  x  x  | [6]  GND ----------+--> [GND] WS2812B LED Ring
                      |  x  x  | [8]  x
    [GND] RFID 2 <----+--[9]  x  x  | [10] x
                      |  x  x  | [12] GPIO 18 ------+--> [DIN] WS2812B LED Ring
      [VCC] Fan <-----+-[17]  x  x  | [14] GND ----------+--> [GND] Fan
                      |  x  x  | [16] x
                      |  x  x  | [18] x
                      |  x  x  | [20] x
                      |  x  x  | [22] x
                      |  x  x  | [24] x
                      |  x  x  | [26] x
                      |  x  x  | [28] x
                      |  x  x  | [30] x
                      |  x  x  | [32] x
                      |  x  x  | [34] x
                      |  x  x  | [36] x
                      |  x  x  | [38] x
                      |  x  x  | [40] x
                      +-----------------------------+
```

### Connection Summary Table

| Device | Wire Color / Function | Pi Physical Pin | Notes |
| :--- | :--- | :--- | :--- |
| **M5Stack RFID 2** | Red (5V VCC) | **Pin 4** | Powers the RFID chip |
| | Black (GND) | **Pin 9** | Ground |
| | White (SDA) | **Pin 3** | I2C Data line |
| | Yellow (SCL) | **Pin 5** | I2C Clock line |
| **WS2812B LED Ring** | Red (5V VCC) | **Pin 2** | Powers the LEDs |
| | Black/White (GND) | **Pin 6** | Ground |
| | Green (DIN) | **Pin 12** | GPIO 18 (Hardware PWM0) |
| **Cooling Fan** | Red (VCC +) | **Pin 17** (or **Pin 1**) | 3.3V Quiet Mode (Recommended) |
| | Black (GND -) | **Pin 14** | Ground |

*Tip: Running the fan at 3.3V (instead of 5V) keeps the Pi cool while reducing fan noise dramatically.*

