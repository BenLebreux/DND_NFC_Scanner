#ifndef INPUT_MANAGER_H
#define INPUT_MANAGER_H

#include <Arduino.h>

class InputManager {
public:
    InputManager();
    void begin();
    void update();
    int getEncoderDelta();
    bool isButtonPressed();
};

#endif // INPUT_MANAGER_H
