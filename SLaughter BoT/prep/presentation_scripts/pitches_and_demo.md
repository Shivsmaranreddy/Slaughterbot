# Presentation scripts

## One-minute pitch
SLAUGHTER BOT is an experimental assistance and management project. Our local software links
customer requests, batch records and operational tasks. Separate notebooks train a visual classifier,
a volume autoencoder, a scenario-generation policy and a robotic task policy. We keep training
evidence and provenance with each exported model. The robotics demonstration uses inert objects,
and an independent safety controller can reject every policy suggestion. Visual assessment does
not certify food safety. At this source-delivery stage the models are not trained; the planned
experiments will determine which claims we can support.

## Three-minute outline
Spend 30 seconds on the problem and intended users. Spend 45 seconds showing customer and manager
workflows. Spend 60 seconds distinguishing the four model responsibilities and evidence requirements.
Spend 30 seconds explaining mock safety and the physical stop. Close with 15 seconds on current
limitations. Replace planned-results language only after you have measured and reviewed results.

## Five-minute technical explanation
Explain the dataset manifest and batch split, MobileNet transfer learning, volume acquisition
geometry, the scenario bandit and robot observation vector. Show how the registry abstains for
missing artifacts. Explain why confidence, reconstruction error and policy reward are different
quantities and cannot be averaged into a food-safety score.

## Live demonstration sequence
Create a fictional order. Update it as manager. Show mass-balance rejection. Request inference
with an untrained model and explain abstention. Arm the in-memory mock, move, stop and show a
rejected action. When available, show actual notebook evaluation with provenance and limitations.
Do not attempt physical movement until hardware review and supervised testing have been completed.
