# Training without local installation

## Where to begin
Upload the repository folder or its ZIP to Colab or Kaggle and extract it. Open one notebook:

| Model | Notebook | Input | Export |
|---|---|---|---|
| Visual CNN | build/imagery/cnn/train.ipynb | Licensed labeled images and manifest | model_1_visual_cnn |
| Volume autoencoder | build/imagery/ultrasound_3d/train.ipynb | Synthetic generator or calibrated 32³ NPZ volumes | model_2_ultrasound_3d |
| Scenario policy | build/rl/environment_generator/train.ipynb | Repository simulator | model_3_environment_rl |
| Robot policy | build/rl/robotic_control/train.ipynb | Simulator and optional model 3 policy | model_4_robotic_rl |

Set REPO_ROOT in the first cell. Run installation only inside the selected training environment.
Set dataset paths in the following cells. Kaggle needs internet enabled for package installation
and pretrained backbone downloads. No Google Drive or Kaggle path is hardcoded.

CNN: GPU recommended, initial batch 16. Volume model: one small volume at a time. RL: CPU MLP
policies with 20,000 timesteps as an initial experiment. These are starting settings, not guaranteed
adequate training budgets. Runtime depends on the allocated machine and data.

## Resume and reproducibility
CNN and volume checkpoints contain weights, optimizer and epoch. RL PPO checkpoints contain
policy and optimizer state. Set RESUME to the checkpoint file. For CNN/volume, epochs is the
total target count. For PPO, timesteps is the additional training budget on resume.
Resume is not promised bit-for-bit identical across GPU, package changes or restored environments.
Model metadata records installed package versions. Record dataset checksums and retain the original
manifest. Repeat experiments with several seeds and preserve each run in a separate copied output
folder to avoid overwriting earlier results.

## Export and persistence
The training function writes actual weights only after successful training and evaluation. Download
the model folder, checkpoints, manifest, evaluation and logs before ending the cloud session.
Colab/Kaggle ephemeral storage is not a backup. Validate model provenance before using it locally.

Optional branches (audio classification, object detection, multitask learning, DICOM acquisition,
calibration, ONNX conversion) remain data/implementation-dependent. They are not claimed complete.
