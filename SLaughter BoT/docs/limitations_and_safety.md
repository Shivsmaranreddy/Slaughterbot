# Limitations, safety and ethics

- No models have been trained in this delivery. No runtime, browser or hardware tests have run.
- Visual labels are experimental visible-condition labels. They do not measure pathogens or certify food safety.
- Softmax confidence is not calibrated and does not guarantee detection of unfamiliar inputs.
- Synthetic ellipsoids do not simulate validated ultrasound physics or biological anatomy.
- Real scan reconstruction needs acquisition calibration, tracked geometry and independent validation.
- The RL environment is a small discrete positioning task with synthetic features. Camera localization,
  reliable sim-to-real transfer and real actuator dynamics remain future work.
- A policy ZIP can deserialize executable objects. Only load trusted training exports.
- No production authentication, billing, tenant isolation, automated business notifications or industrial integration.
- Firmware is a reviewable draft, not compiled or hardware-tested. ESP32 port and serial bridge are outstanding.
- A physical power stop, mechanical limits, enclosure and supervised force testing are required before hardware use.
- Use permitted datasets and fictional customer records. Keep original source and preprocessing provenance.
- Do not present generated diagrams, proposed budgets or planned experiments as observed evidence.
