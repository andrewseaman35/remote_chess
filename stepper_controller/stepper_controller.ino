#include "TwoPositionStepper.h"

#define STEPPER_ID_X_AXIS "x"
#define STEPPER_ID_Y_AXIS "y"
#define STEPPER_ID_Z_AXIS "z"
#define STEPPER_ID_HAND "hand"
#define STEPPER_ID_Z "z"

#define HANDSHAKE "heybuddy"
#define HANDSHAKE_ACK "eyyy"
#define DEBUG_ID "debug"

#define HAND_OPEN "open"
#define HAND_CLOSE "close"
#define Z_UP "up"
#define Z_DOWN "down"

const int BAUD = 9600;

const int HAND_Z_STEPPER_PIN_1 = 8;
const int HAND_Z_STEPPER_PIN_2 = 9;
const int HAND_Z_STEPPER_PIN_3 = 10;
const int HAND_Z_STEPPER_PIN_4 = 11;

const int HAND_Z_TOGGLE_PIN = 7;
const int HAND_ENABLED_STATE = HIGH;
const int Z_ENABLED_STATE = LOW;

const int HAND_HOME_PIN = 12;
const int HAND_MOVEMENT_DISTANCE = -15;
TwoPositionStepper handStepper(
  HAND_Z_STEPPER_PIN_1, 
  HAND_Z_STEPPER_PIN_2, 
  HAND_Z_STEPPER_PIN_3, 
  HAND_Z_STEPPER_PIN_4, 
  HAND_HOME_PIN,
  HAND_MOVEMENT_DISTANCE,
  SPEED_DELAY_SLOW);

const int Z_HOME_PIN = 6;
const int Z_MOVEMENT_DISTANCE = -500;
TwoPositionStepper zStepper(
  2, //  HAND_Z_STEPPER_PIN_1, 
  3, //  HAND_Z_STEPPER_PIN_2, 
  4, //  HAND_Z_STEPPER_PIN_3, 
  5, //  HAND_Z_STEPPER_PIN_4, 
  Z_HOME_PIN,
  Z_MOVEMENT_DISTANCE,
  SPEED_DELAY_MEDIUM);

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(HAND_Z_TOGGLE_PIN, OUTPUT);
  Serial.begin(BAUD);  // start serial communication at 9600 baud
  Serial.setTimeout(3);
}

void handleHandCommand(String position) {
  digitalWrite(HAND_Z_TOGGLE_PIN, HAND_ENABLED_STATE);
  delay(100); // are these necessary?
  Serial.println("moving grabber");
  if (position == HAND_OPEN ) {
    Serial.println("opening");
    handStepper.driveAway();
  } else if (position == HAND_CLOSE) {
    Serial.println("closing");
    handStepper.driveHome();
  } else {
    Serial.println("invalid");
  }
}

void handleZCommand(String position) {
  digitalWrite(HAND_Z_TOGGLE_PIN, HAND_ENABLED_STATE);
  delay(100); // are these necessary?
  Serial.println("moving z");
  if (position == Z_UP) {
    Serial.println("moving up");
    zStepper.driveHome();
  } else if (position == Z_DOWN) {
    Serial.println("moving down");
    zStepper.driveAway();
  } else {
    Serial.println("invalid");
  }
}

void loop() {
  if (Serial.available()) {
    String stepperId = Serial.readStringUntil(':');
    Serial.read(); 
    String position = Serial.readString();
    stepperId.trim();
    position.trim();
    Serial.println(stepperId);
    Serial.println(position);
    Serial.println("ASDF");
    if (stepperId == HANDSHAKE) {
      Serial.println(HANDSHAKE_ACK);
    } else if (stepperId == DEBUG_ID) {
      int handHome = digitalRead(HAND_HOME_PIN);
      Serial.println("Hand Home");
      Serial.println(handHome);
      int zHome = digitalRead(Z_HOME_PIN);
      Serial.println("Z Home");
      Serial.println(zHome);
    } else {
      Serial.println("STEPPER ID");
      Serial.println(stepperId);
      Serial.println("POSITION");
      Serial.println(position);      
      if (stepperId == STEPPER_ID_HAND) {
        handleHandCommand(position);
      } else if (stepperId == STEPPER_ID_Z) {
        handleZCommand(position);
      }
    }
  }
}
