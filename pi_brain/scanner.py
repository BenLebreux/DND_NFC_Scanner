import os
import re
import sys
import time
import json
import serial
import serial.tools.list_ports
import math
import threading

# Fallback-safe imports for libraries that may not be present on non-Pi platforms
try:
    import yaml
except ImportError:
    yaml = None

try:
    import smbus2
except ImportError:
    smbus2 = None

try:
    from rpi_ws281x import Adafruit_NeoPixel, Color
except ImportError:
    Adafruit_NeoPixel = None
    def Color(r, g, b):
        return (r << 16) | (g << 8) | b

try:
    from mfrc522_i2c import MFRC522
except ImportError:
    try:
        from mfrc522 import MFRC522
    except ImportError:
        MFRC522 = None

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BAUD_RATE = 115200

# WS2812B LED Config (GPIO 18 / PWM0)
LED_COUNT      = 16
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 150  # Balanced brightness (max 255)
LED_INVERT     = False
LED_CHANNEL    = 0

# NFC Scanner Config
I2C_BUS = 1
I2C_ADDRESS = 0x28

# File Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAPPING_FILE = os.path.join(SCRIPT_DIR, "nfc_mapping.json")

# ==============================================================================
# LED ANIMATION CONTROLLER
# ==============================================================================
class LEDController:
    def __init__(self):
        self.strip = None
        if Adafruit_NeoPixel:
            try:
                self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
                self.strip.begin()
                self.clear()
            except Exception as e:
                print(f"[!] Failed to initialize NeoPixels: {e}")
                self.strip = None
        
        self.mode = "waiting" # waiting, success, error
        self.running = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._animation_loop, daemon=True)
        self.thread.start()

    def clear(self):
        if self.strip:
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, Color(0, 0, 0))
            self.strip.show()

    def trigger_success(self):
        with self.lock:
            self.mode = "success"

    def trigger_error(self):
        with self.lock:
            self.mode = "error"

    def stop(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.clear()

    def _animation_loop(self):
        step = 0
        while self.running:
            if not self.strip:
                time.sleep(0.1)
                continue

            with self.lock:
                current_mode = self.mode

            if current_mode == "success":
                # Vibrant Green Pulse
                for brightness in range(0, 256, 15):
                    c = Color(0, brightness, 0)
                    for i in range(self.strip.numPixels()):
                        self.strip.setPixelColor(i, c)
                    self.strip.show()
                    time.sleep(0.01)
                for brightness in range(255, -1, -15):
                    c = Color(0, brightness, 0)
                    for i in range(self.strip.numPixels()):
                        self.strip.setPixelColor(i, c)
                    self.strip.show()
                    time.sleep(0.01)
                with self.lock:
                    self.mode = "waiting"

            elif current_mode == "error":
                # Vibrant Red Strobe
                for _ in range(3):
                    for i in range(self.strip.numPixels()):
                        self.strip.setPixelColor(i, Color(255, 0, 0))
                    self.strip.show()
                    time.sleep(0.1)
                    self.clear()
                    time.sleep(0.1)
                with self.lock:
                    self.mode = "waiting"

            else:
                # Waiting mode: Cool Blue Spinning / Breathing animation
                # Sine wave brightness breathing
                amplitude = (math.sin(step * 0.05) + 1.0) / 2.0  # 0.0 to 1.0
                base_brightness = int(amplitude * 80) + 10      # 10 to 90 range
                
                # Active spinning pixel index
                spin_pixel = step % self.strip.numPixels()
                
                for i in range(self.strip.numPixels()):
                    if i == spin_pixel:
                        self.strip.setPixelColor(i, Color(0, 0, 200)) # bright spinner
                    else:
                        # soft breathing background
                        self.strip.setPixelColor(i, Color(0, 0, base_brightness))
                self.strip.show()
                step += 1
                time.sleep(0.05)

# ==============================================================================
# OBSIDIAN VAULT SEARCH & PARSING
# ==============================================================================
def find_obsidian_root():
    """Recursively crawls upwards to find the parent DND Campaign Notes folder."""
    curr = os.path.abspath(SCRIPT_DIR)
    for _ in range(5):
        # Look for Campaign directories in the current folder
        has_campaigns = any(os.path.isdir(os.path.join(curr, d)) and d.startswith("Campaign") for d in os.listdir(curr))
        if has_campaigns:
            return curr
        curr = os.path.dirname(curr)
    return None

def find_monster_file(monster_name, vault_root):
    """Recursively walks the Obsidian vault to find the monster note."""
    target = monster_name.lower().replace("-", " ").strip()
    for root, dirs, files in os.walk(vault_root):
        # Skip hidden and runtime directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('venv', 'node_modules', 'docs', 'bridge', 'server')]
        for file in files:
            if file.lower().endswith('.md'):
                name_without_ext = os.path.splitext(file)[0].lower().replace("-", " ").strip()
                if name_without_ext == target:
                    return os.path.join(root, file)
    return None

def parse_markdown_statblock(filepath):
    """Parses custom Obsidian monster notes and outputs lines for CYD display."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [f"Error reading file: {e}"]

    filename = os.path.splitext(os.path.basename(filepath))[0]
    name = filename.upper()
    h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if h1_match:
        name = h1_match.group(1).strip().upper()

    lines = content.splitlines()

    # Extracted stats fields
    size_type_align = ""
    ac = ""
    hp = ""
    speed = ""
    challenge = ""
    stats_line_1 = ""
    stats_line_2 = ""
    
    current_section = None
    traits = []
    actions = []
    reactions = []
    
    current_callout_title = None
    current_callout_body = []
    
    def flush_callout():
        nonlocal current_callout_title, current_callout_body
        if current_callout_title:
            body_text = " ".join(current_callout_body).strip()
            body_text = re.sub(r'\*+', '', body_text)
            body_text = re.sub(r'_+', '', body_text)
            formatted = f"{current_callout_title}: {body_text}"
            if current_section == 'traits':
                traits.append(formatted)
            elif current_section == 'actions':
                actions.append(formatted)
            elif current_section == 'reactions':
                reactions.append(formatted)
            current_callout_title = None
            current_callout_body = []

    # Safe YAML frontmatter fallback
    frontmatter = {}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3 and yaml:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except Exception:
                pass

    for line in lines:
        stripped = line.strip()
        
        # Section Headers
        if re.match(r'^##\s+Traits', stripped, re.IGNORECASE):
            flush_callout()
            current_section = 'traits'
            continue
        elif re.match(r'^##\s+Actions', stripped, re.IGNORECASE):
            flush_callout()
            current_section = 'actions'
            continue
        elif re.match(r'^##\s+Reactions', stripped, re.IGNORECASE):
            flush_callout()
            current_section = 'reactions'
            continue
        elif re.match(r'^##\s+', stripped):
            flush_callout()
            current_section = None
            continue

        # Callouts
        callout_start = re.match(r'^>\s*\[!([^\]]+)\]\s*(.*)$', stripped)
        if callout_start:
            flush_callout()
            callout_type = callout_start.group(1).lower()
            title = callout_start.group(2).strip()
            
            if "abstract" in callout_type or "stat" in callout_type:
                current_callout_title = None  # Parse inside statblock callout
            else:
                if not title:
                    title = callout_type.capitalize()
                current_callout_title = title
            continue
            
        clean_line = re.sub(r'^>\s*', '', stripped).strip()
        
        # Parse standard D&D variables
        m_sta = re.search(r'\*\*Size/Type/Alignment:\*\*\s*(.*)$', clean_line, re.IGNORECASE)
        if m_sta:
            size_type_align = m_sta.group(1).strip()
            continue
            
        m_ac = re.search(r'\*\*Armor Class:\*\*\s*(.*)$', clean_line, re.IGNORECASE)
        if m_ac:
            ac = m_ac.group(1).strip()
            continue
            
        m_hp = re.search(r'\*\*Hit Points:\*\*\s*(.*)$', clean_line, re.IGNORECASE)
        if m_hp:
            hp = m_hp.group(1).strip()
            continue
            
        m_speed = re.search(r'\*\*Speed:\*\*\s*(.*)$', clean_line, re.IGNORECASE)
        if m_speed:
            speed = m_speed.group(1).strip()
            continue

        m_cr = re.search(r'\*\*Challenge:\*\*\s*(.*)$', clean_line, re.IGNORECASE)
        if m_cr:
            challenge = m_cr.group(1).strip()
            continue

        # Parse ability scores table row
        if '|' in clean_line and not re.search(r'[a-zA-Z]', clean_line) and not ':' in clean_line:
            parts = [p.strip() for p in clean_line.split('|') if p.strip()]
            if len(parts) == 6:
                stats_line_1 = f"STR {parts[0]} | DEX {parts[1]} | CON {parts[2]}"
                stats_line_2 = f"INT {parts[3]} | WIS {parts[4]} | CHA {parts[5]}"
                continue

        # Parse callout body lines
        if current_callout_title is not None:
            if stripped.startswith('>'):
                body_line = stripped[1:].strip()
                if body_line and not body_line.startswith('[!'):
                    current_callout_body.append(body_line)
            else:
                flush_callout()

    flush_callout()

    # Frontmatter Fallbacks
    if not ac and 'ac' in frontmatter:
        ac = str(frontmatter['ac'])
    if not hp and 'hp' in frontmatter:
        hp = str(frontmatter['hp'])
    if not challenge and 'cr' in frontmatter:
        challenge = str(frontmatter['cr'])
    if not size_type_align and ('size' in frontmatter or 'type' in frontmatter or 'alignment' in frontmatter):
        size = frontmatter.get('size', '').capitalize()
        m_type = frontmatter.get('type_subtype', frontmatter.get('type', '')).capitalize()
        align = frontmatter.get('alignment', '').title()
        size_type_align = f"{size} {m_type}, {align}".strip(', ')

    # Assemble payload
    output_lines = [name]
    if size_type_align:
        output_lines.append(size_type_align)
    output_lines.append("-------------------")
    
    if ac:
        output_lines.append(f"Armor Class: {ac}")
    if hp:
        output_lines.append(f"Hit Points: {hp}")
    if speed:
        output_lines.append(f"Speed: {speed}")
        
    if stats_line_1:
        output_lines.append("-------------------")
        output_lines.append(stats_line_1)
        output_lines.append(stats_line_2)
        
    if challenge:
        output_lines.append("-------------------")
        output_lines.append(f"Challenge: {challenge}")

    if traits:
        output_lines.append("-------------------")
        for trait in traits:
            output_lines.append(trait)
            
    if actions:
        output_lines.append("-------------------")
        output_lines.append("ACTIONS")
        for action in actions:
            output_lines.append(action)

    if reactions:
        output_lines.append("-------------------")
        output_lines.append("REACTIONS")
        for reaction in reactions:
            output_lines.append(reaction)
            
    return output_lines

# ==============================================================================
# SERIAL & COMMUNICATION
# ==============================================================================
def find_cyd_port():
    """Scans serial ports to find a connected ESP32 CYD."""
    ports = serial.tools.list_ports.comports()
    # Prioritize USB-to-UART converter chips
    for port in ports:
        if any(x in port.description for x in ["CH340", "CP210", "USB", "FTDI"]):
            print(f"[*] Found likely ESP32 CYD on: {port.device} ({port.description})")
            return port.device
    # Fallback to absolute device interfaces if present
    for p in ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']:
        if os.path.exists(p):
            print(f"[*] Found serial port by path: {p}")
            return p
    return None

# ==============================================================================
# MAIN PROGRAM LOOP
# ==============================================================================
def main():
    print("[*] Starting D&D Statblock Scanner (Pi 4 Production)")
    
    # Init NeoPixel Animations
    leds = LEDController()
    
    # 1. Establish Serial connection to CYD
    ser_port = find_cyd_port()
    ser = None
    if ser_port:
        try:
            ser = serial.Serial(ser_port, BAUD_RATE, timeout=1)
            print(f"[*] Serial connected on {ser_port}")
            ser.write(b"Brain ready! Waiting for NFC scan...\n")
        except Exception as e:
            print(f"[!] Serial connection failed: {e}")
    else:
        print("[!] CYD serial port not found. Display updates will log to stdout.")

    # 2. Find Obsidian vault root
    vault_root = find_obsidian_root()
    if vault_root:
        print(f"[*] Obsidian database vault root: {vault_root}")
    else:
        print("[!] WARNING: Could not auto-detect Obsidian DND Campaign Notes folder.")

    # 3. Load mappings
    mappings = {}
    if os.path.exists(MAPPING_FILE):
        try:
            with open(MAPPING_FILE, 'r') as f:
                mappings = json.load(f)
            print(f"[*] Loaded {len(mappings)} NFC tag mappings.")
        except Exception as e:
            print(f"[!] Error loading mappings file: {e}")
    else:
        print("[!] Mappings file nfc_mapping.json not found. Creating default empty structure.")
        with open(MAPPING_FILE, 'w') as f:
            json.dump({}, f, indent=2)

    # 4. Initialize RFID scanner over I2C
    if not MFRC522:
        print("[!] Error: mfrc522 library is not available. Running mock scanning loop.")
        # Simulating tag scan every 10 seconds for testing fallback
        try:
            while True:
                time.sleep(10)
                sim_uid = "04:EA:81:4A:2B:10"
                process_tag(sim_uid, mappings, vault_root, ser, leds)
        except KeyboardInterrupt:
            leds.stop()
        return

    try:
        reader = MFRC522(bus=I2C_BUS, dev=I2C_ADDRESS)
        print(f"[*] NFC Scanner Initialized on I2C bus {I2C_BUS} at 0x{I2C_ADDRESS:02X}")
    except Exception as e:
        print(f"[!] Failed to initialize RFID scanner: {e}")
        print("[!] Check I2C wiring (Pins 3, 5, 4, 9). Enabling software mock loop.")
        try:
            while True:
                time.sleep(10)
                sim_uid = "04:EA:81:4A:2B:10"
                process_tag(sim_uid, mappings, vault_root, ser, leds)
        except KeyboardInterrupt:
            leds.stop()
        return

    print("\n[*] Waiting for NFC Scan...")
    last_uid = None
    cooldown = 0
    
    try:
        while True:
            # Poll RFID Scanner
            (status, tag_type) = reader.MFRC522_Request(reader.PICC_REQIDL)
            
            if status == reader.MI_OK:
                (status, uid) = reader.MFRC522_Anticoll()
                if status == reader.MI_OK:
                    uid_str = ":".join(f"{x:02X}" for x in uid)
                    
                    # Prevent rapid repeat reads of the same card
                    if uid_str != last_uid or cooldown <= 0:
                        last_uid = uid_str
                        cooldown = 4  # ~2 second scan cooldown
                        process_tag(uid_str, mappings, vault_root, ser, leds)
            
            if cooldown > 0:
                cooldown -= 1
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
    finally:
        if ser:
            ser.close()
        leds.stop()

def process_tag(uid, mappings, vault_root, ser, leds):
    print(f"\n[+] NFC Scanned UID: {uid}")
    
    # 1. Resolve UID to Monster Name
    monster_name = mappings.get(uid)
    if not monster_name:
        print(f"[!] Tag UID {uid} is not mapped in nfc_mapping.json.")
        leds.trigger_error()
        payload = f"UNKNOWN TAG|UID: {uid}|Use nfc_mapping.json to link this tag to an Obsidian monster.\n"
        send_to_cyd(payload, ser)
        return

    print(f"[*] Resolved tag to monster: {monster_name}")

    # 2. Search Obsidian vault for matching note
    if not vault_root:
        print("[!] Cannot query Obsidian: Vault root not found.")
        leds.trigger_error()
        payload = "ERROR|Obsidian campaign vault root not found.|Check folder paths on Pi.\n"
        send_to_cyd(payload, ser)
        return

    monster_file = find_monster_file(monster_name, vault_root)
    if not monster_file:
        print(f"[!] Monster note not found for: {monster_name}")
        leds.trigger_error()
        payload = f"MONSTER NOT FOUND|{monster_name.upper()}|Could not find matching file in vault.\n"
        send_to_cyd(payload, ser)
        return

    print(f"[*] Found statblock markdown: {monster_file}")

    # 3. Parse markdown statblock
    lines = parse_markdown_statblock(monster_file)
    if not lines or len(lines) <= 2:
        print("[!] Parsing returned empty results.")
        leds.trigger_error()
        payload = f"ERROR|Failed to parse statblock for {monster_name}.\n"
        send_to_cyd(payload, ser)
        return

    # 4. Success feedback and send
    leds.trigger_success()
    
    # Format into a single line joined by '|' with trailing newline
    payload = "|".join(lines) + "\n"
    send_to_cyd(payload, ser)

def send_to_cyd(payload, ser):
    if ser:
        try:
            # Clear output buffer and send
            ser.reset_output_buffer()
            ser.write(payload.encode('utf-8'))
            print("    -> Sent statblock to CYD screen.")
        except Exception as e:
            print(f"[!] Failed to write to serial port: {e}")
    else:
        # Standard stdout debug log
        print("====== CYD PAYLOAD ======")
        print(payload.replace('|', '\n'))
        print("=========================")

if __name__ == '__main__':
    main()
