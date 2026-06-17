#include <Arduino.h>
#include "NfcScanner.h"
#include "DisplayController.h"
#include "InputManager.h"
#include "LedController.h"

NfcScanner nfcScanner;
DisplayController displayController;
InputManager inputManager;
LedController ledController;

void setup() {
    Serial.begin(115200);
    Serial.println("NFC Miniature Scanning Tower - Booting...");

    // Initialize all sub-systems
    displayController.begin();
    nfcScanner.begin();
    inputManager.begin();
    ledController.begin();
    
    ledController.setModeIdle();
}

void loop() {
    // Update all sub-systems
    nfcScanner.update();
    inputManager.update();
    displayController.update();
    ledController.update();

    // Basic logic mapping
    if (nfcScanner.hasNewScan()) {
        String uid = nfcScanner.getLastScannedUid();
        Serial.println("Scanned UID: " + uid);
        displayController.showItemDetails(uid);
        ledController.setModeSuccess();
        
        // Return to idle after a delay (this should ideally be non-blocking in a real app)
        delay(2000); 
        ledController.setModeIdle();
    }
}
