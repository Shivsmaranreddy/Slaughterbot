# Arduino inert-object demonstrator wiring draft

```text
USB computer -------- Arduino USB (logic power + serial)
Arduino D9 ---------- Servo signal
Arduino GND --------- External servo supply GND
External +5 V ------- Fuse -- physical power-stop contact -- Servo V+
Arduino D2 ---------- Normally-closed safety-loop contact -- GND
Arduino D3 ---------- Momentary local ARM button ---------- GND
```

Use separate contacts for the safety loop and actuator power stop. Confirm the actual servo's
voltage/current requirements and board pinout before wiring. Do not power a loaded servo from
the Arduino 5 V pin. Provide strain relief and an enclosure. Keep only foam/plastic inert objects
in the travel area. This drawing is conceptual and unverified, not an electrical certification.
