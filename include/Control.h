#include "Servo.h";
#include "Arduino.h";

#define DEFAULT_PIN_FRONT_LEFT 3
#define DEFAULT_PIN_FRONT_RIGHT 5
#define DEFAULT_PIN_REAR_RIGHT 6
#define DEFAULT_PIN_REAR_LEFT 9

Servo FRONT_RIGHT;
Servo FRONT_LEFT;
Servo REAR_RIGHT;
Servo REAR_LEFT;

void execCommand(char* COMMAND, char* STATUS){
    
}

void initializeMotors(){
    FRONT_RIGHT.attach(DEFAULT_PIN_FRONT_RIGHT, 1000, 2000);
    FRONT_LEFT.attach(DEFAULT_PIN_FRONT_LEFT, 1000, 2000);
    REAR_RIGHT.attach(DEFAULT_PIN_REAR_RIGHT, 1000, 2000);
    REAR_LEFT.attach(DEFAULT_PIN_REAR_LEFT, 1000, 2000);
}

void setSpeed(char motor[2], int speed){

}