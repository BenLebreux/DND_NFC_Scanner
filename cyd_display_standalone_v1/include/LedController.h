#ifndef LED_CONTROLLER_H
#define LED_CONTROLLER_H

#include <Arduino.h>

class LedController {
public:
    LedController();
    void begin();
    void update();
    void setModeIdle();
    void setModeScanning();
    void setModeSuccess();
    void setModeError();
};

#endif // LED_CONTROLLER_H
