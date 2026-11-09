# Feasibility and risks
Exhibition target: INR 5,000–7,000 using the existing Arduino, desktop and school lab equipment.
No supplier quotations have been obtained. Complete the hardware CSV with actual quotes and receipts.
The production Edge target below INR 2 lakh requires separate validation and is not an exhibition claim.

| Risk | Consequence | Mitigation / evidence needed |
|---|---|---|
| Dataset rights unclear | Unusable training/evaluation | Verify source license and intended use |
| Split leakage | Inflated metrics | Batch/subject split plus duplicate review |
| Cloud session ends | Lost work | Download checkpoints and complete model folders |
| High softmax on unfamiliar image | Misleading assessment | Abstention, human review and shift testing |
| Uncalibrated scans | Invalid geometry | Use labelled synthetic demo until calibrated data exists |
| RL model suggests unsafe movement | Damage or injury | Independent stop, hard limits, inert objects |
| Scope exceeds budget | Unfinished exhibition | Prioritize mock app and one validated AI demonstration |
| Firmware assumptions wrong | Unsafe physical behavior | Exact-board compilation and supervised validation |

Future work: camera localization, calibrated volume ingestion, confidence calibration, trusted model
promotion, production authentication and multi-location administration. Each requires its own tests.
