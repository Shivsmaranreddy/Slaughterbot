# ESP32 adaptation status
NOT IMPLEMENTED / NOT COMPILED. The primary firmware target is the existing Arduino.
ESP32 boards and Arduino-core versions differ in servo/PWM APIs and usable pins.
Select the exact board, validate its 3.3 V logic and choose an appropriate servo library before porting.
Preserve the Arduino state machine, local arming, independent stop loop, rate limit and watchdog.
Do not upload the Arduino sketch unchanged to an unspecified ESP32 board.
