import serial
import serial.tools.list_ports
import time
import requests
import re
import sys

SERVER_URL = 'http://localhost:3000/api/scan'
DEBUG_URL = 'http://localhost:3000/api/debug'

def log_debug(msg):
    print(f"[DEBUG] {msg}")
    try:
        requests.post(DEBUG_URL, json={'log': f"[BRIDGE] {msg}"}, timeout=0.5)
    except:
        pass

def find_flipper_port():
    log_debug("Scanning for Flipper Zero USB ports...")
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Flipper" in port.description or (port.vid == 0x0483 and port.pid == 0x5740):
            log_debug(f"Auto-detected Flipper Zero on {port.device} (VID:{port.vid} PID:{port.pid})")
            return port.device
            
    # Fallback to common Linux ports
    for p in ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2', '/dev/ttyUSB0']:
        try:
            s = serial.Serial(p)
            s.close()
            log_debug(f"Found active generic serial port on {p}, assuming it's the Flipper.")
            return p
        except:
            pass
            
    log_debug("CRITICAL ERROR: Could not find any Flipper Zero connected via USB.")
    return None

def connect_flipper(port):
    try:
        ser = serial.Serial(port, 230400, timeout=0.5)
        log_debug("Serial port opened successfully.")
        
        # Aggressive Wakeup
        ser.write(b"\x03\x03") # Ctrl+C to stop anything running
        time.sleep(0.5)
        ser.write(b"\r\n\r\n")
        time.sleep(0.5)
        
        # Read whatever it spits back
        welcome = ser.read_all().decode('utf-8', errors='ignore')
        log_debug(f"CLI Wakeup Response: {welcome.strip()}")
        
        return ser
    except serial.SerialException as e:
        log_debug(f"Failed to connect to Flipper Zero: {e}")
        return None

def main():
    print("\n" + "="*50)
    print("   FLIPPER ZERO ROBUST CONNECTION SCRIPT")
    print("="*50)
    
    port = find_flipper_port()
    if not port:
        print("\n[!] Please ensure your Flipper is plugged in and turned on.")
        sys.exit(1)
        
    ser = connect_flipper(port)
    if not ser:
        sys.exit(1)

    # Put Flipper in standard log mode for manual GUI scanning
    log_debug("Putting Flipper into GUI Log mode...")
    ser.write(b"log debug\r\n")
    time.sleep(0.5)
    ser.read_all() # Clear buffer

    uid_pattern = re.compile(r'UID:?\s*([0-9A-Fa-f\s:-]{8,})', re.IGNORECASE)
    
    print("\n" + "="*50)
    print(" MVP MODE READY! USE THE FLIPPER SCREEN:")
    print(" MENU -> NFC -> READ -> TAP TAG")
    print("="*50 + "\n")

    try:
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                log_debug(f"RAW: {line}")
                
                # Strip ANSI color codes just in case
                clean_line = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', line)
                
                match = uid_pattern.search(clean_line)
                if match:
                    raw_uid = match.group(1).strip()
                    uid = raw_uid.replace(' ', ':').upper()
                    print(f"\n[+] SUCCESS! Detected NFC Tag: {uid}")
                    
                    try:
                        requests.post(SERVER_URL, json={'uid': uid})
                        print("[+] Sent successfully to Dashboard!")
                    except Exception as e:
                        print(f"[-] Failed to send to Dashboard: {e}")
                        
                    time.sleep(2)
                    
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        if ser:
            ser.close()

if __name__ == '__main__':
    main()
