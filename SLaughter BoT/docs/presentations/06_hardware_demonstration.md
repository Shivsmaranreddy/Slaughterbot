# Hardware and live demonstration

## Harmless demonstration

Use lightweight inert objects and a low-force servo gate.

The existing Arduino is the primary proposed board.

Firmware is a draft. Compilation and supervised physical tests remain pending.

## Independent safeguards

A local arm button and normally-closed stop loop govern firmware.

The physical emergency stop must interrupt actuator power.

Movement bounds, rate limits and command timeout remain independent of RL.

## Demonstration sequence

Arm the mock and submit one bounded movement.

Press stop and show that another movement is rejected.

Use physical hardware only after wiring and force validation.