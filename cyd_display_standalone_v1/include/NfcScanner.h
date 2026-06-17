#ifndef NFC_SCANNER_H
#define NFC_SCANNER_H

#include <Arduino.h>

class NfcScanner {
public:
    NfcScanner();
    void begin();
    void update();
    bool hasNewScan();
    String getLastScannedUid();
};

#endif // NFC_SCANNER_H
