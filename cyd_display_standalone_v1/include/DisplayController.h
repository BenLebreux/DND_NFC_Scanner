#ifndef DISPLAY_CONTROLLER_H
#define DISPLAY_CONTROLLER_H

#include <Arduino.h>

class DisplayController {
public:
    DisplayController();
    void begin();
    void update();
    void showMenu(int selectedIndex);
    void showItemDetails(String uid);
};

#endif // DISPLAY_CONTROLLER_H
