#include <TFT_eSPI.h>
#include <SPI.h>

// ==============================================================================
// CONFIGURATION
// ==============================================================================
#define ENCODER_CLK 22
#define ENCODER_DT  27

TFT_eSPI tft = TFT_eSPI();

// ==============================================================================
// GLOBAL STATE
// ==============================================================================
volatile int encoderPos = 0;
int lastReportedPos = 0;
int scroll_y = 0;

String currentStatblock = "Waiting for Scan...";

// ==============================================================================
// INTERRUPTS
// ==============================================================================
void IRAM_ATTR readEncoder() {
  // Read the state of the DT pin to determine direction
  int dtValue = digitalRead(ENCODER_DT);
  if (dtValue == HIGH) {
    encoderPos++; // Clockwise
  } else {
    encoderPos--; // Counter-Clockwise
  }
}

// ==============================================================================
// RENDERING
// ==============================================================================
void drawScreen() {
  tft.fillScreen(TFT_BLACK);
  
  // Parse and draw the string
  // We use scroll_y to offset the starting Y coordinate
  int startY = 50 + scroll_y;
  
  tft.setCursor(10, startY);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.setTextSize(2);
  
  // Replace the '|' delimiters back into standard newlines for printing
  String displayString = currentStatblock;
  displayString.replace("|", "\n");
  
  tft.print(displayString);
  
  // Draw a static header over the scrolling text
  tft.fillRect(0, 0, 320, 40, TFT_BLACK); // Clear top banner area
  tft.setCursor(10, 10);
  tft.setTextColor(TFT_YELLOW, TFT_BLACK);
  tft.setTextSize(2);
  tft.println("D&D Statblock Scanner (V2)");
  tft.drawLine(0, 35, 320, 35, TFT_GREEN);
}

// ==============================================================================
// MAIN LOGIC
// ==============================================================================
void setup() {
  Serial.begin(115200);

  // 1. Setup Screen
  pinMode(21, OUTPUT);
  digitalWrite(21, HIGH); // Backlight on
  tft.init();
  tft.setRotation(1); // Landscape
  tft.setTextWrap(true);
  
  // 2. Setup Rotary Encoder Interrupts
  pinMode(ENCODER_CLK, INPUT_PULLUP);
  pinMode(ENCODER_DT, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_CLK), readEncoder, FALLING);
  
  // Initial draw
  drawScreen();
}

void loop() {
  // Check for new incoming statblocks over USB Serial
  if (Serial.available()) {
    currentStatblock = Serial.readStringUntil('\n');
    
    // Reset scroll when new card is scanned
    scroll_y = 0; 
    encoderPos = 0;
    lastReportedPos = 0;
    
    drawScreen();
  }
  
  // Check if the rotary encoder was spun
  if (encoderPos != lastReportedPos) {
    // Calculate the difference
    int diff = encoderPos - lastReportedPos;
    lastReportedPos = encoderPos;
    
    // Adjust scroll offset (e.g., 20 pixels per click)
    scroll_y += (diff * 20);
    
    // Simple boundary limits to stop infinite scrolling up/down
    if (scroll_y > 0) scroll_y = 0;
    if (scroll_y < -600) scroll_y = -600; // Arbitrary bottom limit for this test
    
    // Redraw screen with new scroll offset
    drawScreen();
  }
}
