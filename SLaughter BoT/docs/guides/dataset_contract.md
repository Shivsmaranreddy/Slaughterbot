# Dataset contract

No real visual or ultrasound dataset is bundled or automatically downloaded. A permitted dataset
with task-appropriate labels and independent batch/subject groups is required for real evaluation.
The included manifest example intentionally fails permission validation until completed.

Every manifest records name, source, license, citation, modality, provenance, collection method,
limitations, permission confirmation and samples. Every sample records a relative path, SHA-256,
group ID, split and provenance. Images additionally require a label.
Allowed splits: train, val, test. Split by original batch/subject before augmentation. Near-duplicate
or repeated-view leakage requires manual review beyond the exact-byte checksum check.
No group may cross splits. Synthetic and real samples must use separate manifests.

The validator checks permission metadata, file containment, checksums, duplicate bytes, nonempty
splits and group separation. Permission confirmation is the dataset owner's/researcher's attestation,
not a legal conclusion made by software. Class distribution is shown in the CNN notebook.

Images: readable JPEG/PNG or another Pillow-supported format, RGB conversion, at least 16x16 pixels.
The baseline resizes to 224x224 and applies ImageNet normalization. Horizontal flips are the only
default augmentation. Assess whether flips preserve the intended label before using this baseline.

Volumes: NPZ with volume (32,32,32), spacing_mm (3,), orientation (3,3). Intensities must already
be normalized to [0,1]. Document original spacing, origin, acquisition geometry, calibration and
all resampling. This first implementation supports aligned volumes, not untracked freehand scans.
The orientation matrix must be right-handed and orthonormal. The default synthetic phantoms are
random ellipsoids with added noise, not a validated ultrasound acoustic simulation.

Keep original, processed, synthetic and evaluation material in distinct directories. Store
preprocessing history alongside each manifest. Large data stays out of Git.
