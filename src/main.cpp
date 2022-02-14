#include "Arduino.h"
#include "Servo.h"

//#include "MPU6050.h"

Servo backLeft;
char command;

void setup(){
    backLeft.attach(3, 1000, 2000);
    Serial.begin(9600);
}
void loop(){
    if (Serial.available()){
        command = Serial.read();
        switch (command) {
            case 'l':
                backLeft.write(0);
                Serial.println("OFF");
                break;
            case 'h':
                backLeft.write(180);
                Serial.println("FULL SPEED");
                break;
            default:
                int speed = command - '0';
                backLeft.write(speed*18);
                Serial.print(speed*10);
                Serial.println(" %");
                break;
        }
    }
}