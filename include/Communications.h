#include "Arduino.h"

// Variables for Serial Message Handling
char RECEIVED_BYTE;
int byteIdx = 0;

char initializeSerial(){
    
    // Start serial COM
    Serial.begin(115200);
    
    return 's';
}

void receiveCommand(char* SERIAL_BUFFER){

    while ( Serial.available() ) {

        RECEIVED_BYTE = Serial.read();

        switch ( RECEIVED_BYTE ){
            case '<':
                // Start new message
                byteIdx = 0;
                break;
            case '>':
                // Clear the Buffer
                break;
            default:
                // Add to buffer
                SERIAL_BUFFER[byteIdx++] = RECEIVED_BYTE;
                break;
        }
    }
    
}

void clearCommand(char* SERIAL_BUFFER){
    SERIAL_BUFFER[0] = '\0';
}

void sendStatus()