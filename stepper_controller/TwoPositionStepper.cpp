#include "TwoPositionStepper.h":

#define POSITION_HOME "pos_home"
#define POSITION_AWAY "pos_away"

const int HOME_BACKOFF = 5; // cycles to back off of home switch

/*
 * Interface to drive a stepper motor that has two allowable positions. Motor can either be at "home" 
 * or "away". The "home" position is set by driving towards home until the pin at `homePin` is triggered.
 * Once "home", the "away" position is set by driving away from home for `distanceFromHome` cycles.
 * If `distanceFromHome` is positive, drive CW to move away from home, else drive CCW.
 * 
 * `speedDelay`: microsecond delay between stepper motor steps (~8000 for "normal" speed)
 */
TwoPositionStepper::TwoPositionStepper(int pin1, int pin2, int pin3, int pin4, int homePin, int distanceFromHome, int speedDelay) {
  _pin1 = pin1;
  _pin2 = pin2;
  _pin3 = pin3;
  _pin4 = pin4;

  _speedDelay = speedDelay;
  _homePin = homePin;
  _distanceFromHome = distanceFromHome;

  pinMode(_pin1, OUTPUT);
  pinMode(_pin2, OUTPUT);
  pinMode(_pin3, OUTPUT);
  pinMode(_pin4, OUTPUT);
  pinMode(_homePin, INPUT);
  
  _write(LOW, LOW, LOW, LOW);
}

void TwoPositionStepper::_write(int a, int b, int c, int d) {
  digitalWrite(_pin1, a);
  digitalWrite(_pin2, b);
  digitalWrite(_pin3, c);
  digitalWrite(_pin4, d);
}

bool TwoPositionStepper::_interrupted() {
  return !digitalRead(_homePin);
}

bool TwoPositionStepper::cwStep() {
  _write(HIGH, HIGH, LOW, LOW);
  if (_interrupted()) { return true; }
  delay(_speedDelay);
  _write(LOW, HIGH, HIGH, LOW);
  if (_interrupted()) { return true; }
  delay(_speedDelay);
  _write(LOW, LOW, HIGH, HIGH);
  if (_interrupted()) { return true; }
  delay(_speedDelay);
  _write(HIGH, LOW, LOW, HIGH);
  if (_interrupted()) { return true; }
  delay(_speedDelay);
  return false;
}

bool TwoPositionStepper::ccwStep() {
  _write(HIGH, LOW, LOW, HIGH);
  if (_interrupted()) { return true; }
  delay(_speedDelay);
  _write(LOW, LOW, HIGH, HIGH);
  if (_interrupted()) { return true; }
  delay(_speedDelay);
  _write(LOW, HIGH, HIGH, LOW);
  if (_interrupted()) { return true; }
  delay(_speedDelay);
  _write(HIGH, HIGH, LOW, LOW);
  if (_interrupted()) { return true; }
  delay(_speedDelay);
  return false;
}

void TwoPositionStepper::driveAway() {
  if (_position == POSITION_AWAY) {
    return;
  }
  for (int i = 0; i < abs(_distanceFromHome); i++) {
    if (_distanceFromHome > 0) {
      cwStep();  
    } else {
      ccwStep();
    }
  }
  _write(LOW, LOW, LOW, LOW);
  _position = POSITION_AWAY;
}

void TwoPositionStepper::driveHome() {
  if (_position == POSITION_HOME) {
    return;
  }
  bool interrupted = false;
  while(true) {
    if (_distanceFromHome > 0) {
      interrupted = ccwStep();
    } else {
      interrupted = cwStep();
    }
    if (interrupted) {
      break;
    }
  }
  _write(LOW, LOW, LOW, LOW);
  _position = POSITION_HOME;
}
