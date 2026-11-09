# Judge questions and technical defence

**Does it slaughter animals?** No. This implementation demonstrates software and inert-object positioning only.

**Can an image prove food is safe?** No. Visible characteristics are limited evidence and cannot establish pathogen absence.

**What does the CNN learn?** It optimizes a classification objective on supplied visible-condition labels. A pretrained backbone
provides a starting representation; task training and held-out evaluation are still necessary.

**What is unsupervised here?** The volume autoencoder reconstructs its input without class labels. This does not remove the need
for geometry, provenance or independent validation.

**Is stacking images 3D reconstruction?** Only when acquisition geometry supports that interpretation. Unrelated slices are invalid.

**Why two RL roles?** The scenario policy selects training conditions. The robot policy selects task actions. They use different
observation/action spaces and rewards. A random generator is only a baseline, not an RL-trained model.

**Why PPO?** It is an available baseline for these small discrete environments. DQN is also plausible. Selection is provisional
and should follow measured stability, sample efficiency and implementation complexity, not a claim of universal superiority.

**Can RL bypass the stop?** The mock controller validates each action independently. Physical safety additionally needs its own
power interruption and local firmware interlock. Simulation alone cannot prove physical safety.

**How does the robot see?** Current observations are explicitly synthetic features. Real camera localization and validation remain outstanding.

**Is your confidence reliable?** It is an uncalibrated softmax score. Calibration and unfamiliar-input testing are future experiments.

**What results do you have?** At source delivery: no training or runtime results. Present only completed measurements from your own runs.

**What is original?** The implementation, integration and experiments can be the student's contribution. Established algorithms
and commercial management systems are credited; novelty and commercial advantage are not assumed.

**What if the model fails to load?** The registry reports missing or invalid artifacts and the inference API abstains.

**Is enterprise ready?** No. The enterprise interface is a roadmap for access control, tenant isolation, model governance and billing.
