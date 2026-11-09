# Hardware protocol and limits

The supplied application operates only the Python mock. No serial bridge can energize hardware.
Arduino firmware is a separately reviewable draft. It has not been compiled or tested.

115200 baud, ASCII newline frames: `L`, `H`, `R`, `S`.
L/R move two degrees subject to limits and rate checks. H is a heartbeat with no movement.
S stops and detaches the servo. Host commands cannot arm the gate; use the local arm button.
No accepted heartbeat for one second stops the controller. An open safety loop stops it.
Application-level actions 0/1/2 are logical positions; a future bridge must map them deliberately
and wait for acknowledgements. The controller must reject stale, malformed and replayed requests.

Before building: independent emergency stop must interrupt servo power, enclosure must prevent
pinch access, supply must have a fuse, and a teacher must verify force and mechanical travel limits.
Servo detachment alone is not an adequate physical safety guarantee.
