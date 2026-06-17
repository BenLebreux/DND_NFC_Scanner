import time
import serial
import binascii
from rpi_ws281x import Adafruit_NeoPixel, Color
import smbus2

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# 1. USB Serial Config (Connecting to ESP32 CYD)
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

# 2. WS2812B LED Config
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# 3. I2C NFC Scanner Config (M5Stack RFID 2 Unit / WS1850S)
I2C_BUS = 1
I2C_ADDRESS = 0x28

# ==============================================================================
# INITIALIZATION
# ==============================================================================
print("[*] Initializing D&D Statblock Scanner (V2 Hardware Test)")

# Init Serial
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"[*] Serial connection established on {SERIAL_PORT}")
except Exception as e:
    print(f"[!] Failed to open serial port {SERIAL_PORT}: {e}")
    print("[!] Ensure the CYD is plugged in via USB.")
    exit(1)

# Init LEDs
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()
print("[*] WS2812B LEDs Initialized on GPIO 18")

def color_wipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

# Turn off LEDs initially
color_wipe(strip, Color(0, 0, 0))

# Init I2C for NFC
bus = smbus2.SMBus(I2C_BUS)
print(f"[*] I2C Bus {I2C_BUS} Initialized. Searching for scanner at 0x{I2C_ADDRESS:02X}...")

# Note: Reading raw RC522/WS1850S registers via I2C for anti-collision is complex.
# For a robust implementation, you should use an I2C-compatible MFRC522 python library
# (e.g., pip install mfrc522-i2c). 
# For this initial test, we will simulate a successful read loop or attempt a basic register read
# to verify the device is alive on the I2C bus.

try:
    # Read the Version Register (0x37) to see if the chip is alive
    # Note: Address mapping in I2C for MFRC522 usually shifts the register address.
    # We will just verify I2C presence.
    bus.write_quick(I2C_ADDRESS)
    print("[*] NFC Scanner detected on I2C bus!")
except Exception as e:
    print(f"[!] Failed to detect NFC scanner on I2C at {I2C_ADDRESS}: {e}")
    print("[!] Check your wiring to Pi Pins 3 (SDA), 5 (SCL), 4 (5V), 9 (GND).")


# ==============================================================================
# MAIN LOOP
# ==============================================================================
print("\n[*] Waiting for NFC Scan...")
ser.write(b"Brain connected! Waiting for scan...\n")

try:
    while True:
        # --- PLACEHOLDER FOR ACTUAL I2C NFC READ LOGIC ---
        # If you install an mfrc522 library, it would look like:
        # status, TagType = reader.MFRC522_Request(reader.PICC_REQIDL)
        # if status == reader.MI_OK:
        #     status, uid = reader.MFRC522_Anticoll()
        
        # For the sake of the hardware test, we will simulate a scan if the I2C bus is alive,
        # but realistically you need a library. We'll wait 5 seconds and trigger a test log.
        time.sleep(5)
        
        simulated_uid = "04:EA:81:4A:2B:10"
        print(f"[+] Scan Detected! UID: {simulated_uid}")
        
        # 1. Visual Feedback (Turn LEDs Green)
        color_wipe(strip, Color(0, 255, 0))
        
        # 2. Prepare massive statblock payload
        # We replace actual newlines with the '|' delimiter so the CYD 
        # can safely use readStringUntil('\n') and catch the whole block.
        statblock_lines = [
            "GOBLIN",
            "Small humanoid (goblinoid), neutral evil",
            "-------------------",
            "Armor Class: 15 (leather armor, shield)",
            "Hit Points: 7 (2d6)",
            "Speed: 30 ft.",
            "-------------------",
            "STR 8 (-1) | DEX 14 (+2) | CON 10 (+0)",
            "INT 10 (+0) | WIS 8 (-1) | CHA 8 (-1)",
            "-------------------",
            "Skills: Stealth +6",
            "Senses: darkvision 60 ft., passive Perception 9",
            "Languages: Common, Goblin",
            "Challenge: 1/4 (50 XP)",
            "-------------------",
            "Nimble Escape: The goblin can take the Disengage",
            "or Hide action as a bonus action on each of its turns.",
            "-------------------",
            "ACTIONS",
            "Scimitar: Melee Weapon Attack: +4 to hit,",
            "reach 5 ft., one target. Hit: 5 (1d6 + 2) slashing damage.",
            "Shortbow: Ranged Weapon Attack: +4 to hit,",
            "range 80/320 ft., one target. Hit: 5 (1d6 + 2) piercing damage."
        ]
        
        compressed_statblock = "|".join(statblock_lines)
        payload = f"{compressed_statblock}\n"
        
        # 3. Send Data to CYD
        ser.write(payload.encode('utf-8'))
        print(f"    -> Sent massive statblock to CYD")
        
        # 3. Wait and turn LEDs off
        time.sleep(1)
        color_wipe(strip, Color(0, 0, 0))
        
except KeyboardInterrupt:
    print("\n[*] Shutting down...")
    color_wipe(strip, Color(0, 0, 0))
    ser.close()
    bus.close()
