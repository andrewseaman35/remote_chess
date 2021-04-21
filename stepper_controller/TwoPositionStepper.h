#ifndef TwoPositionStepper_h
#define TwoPositionStepper_h

#define SPEED_DELAY_SLOW 25
#define SPEED_DELAY_MEDIUM 2

#include "Arduino.h"

class TwoPositionStepper {
  public:
    TwoPositionStepper(int pin1, int pin2, int pin3, int pin4, int homePin, int distanceFromHome, int speedDelay, bool holdAtHome);

    void driveAway();
    void driveHome();

    void setDistanceFromHome(int newDistanceFromHome);

  private: 
    int _homePin;
    int _pin1;
    int _pin2;
    int _pin3;
    int _pin4;

    int _speedDelay;
    int _position;
    int _distanceFromHome;
    bool _holdAtHome;

    void _write(int a, int b, int c, int d);
    bool _interrupted();
    bool cwStep(bool interruptable);
    bool ccwStep(bool interruptable);
};

#endif
