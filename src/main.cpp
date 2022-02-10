#include "Arduino.h"
#include "Communications.h"
#include "Control.h"

// <helloworld>

// <h>
// <l>
// <1>
// <2>
// p

char COMMAND[64];
char STATUS[64];

void setup(){ 
    initializeSerial();
    initializeMotors();
}

void loop(){
    // Recieve Command from Serial Port
    receiveCommand(COMMAND);
    // Send command and return Status
    execCommand(COMMAND, STATUS);
    // Clear Command for Next Loop
    clearCommand(COMMAND);
    // Return Status Message
    Serial.println(STATUS);

    delay(100);

}