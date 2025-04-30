# Last modified: 2025-04-29 17:03:24
# Version: 0.0.30
from rfdetr import RFDETRBase
from rfdetr import RFDETRLarge
import wandb
import time
from pathlib import Path


# model = RFDETRLarge()
model = RFDETRBase(pretrain_weights="rf-detr-base-2.pth")

datasetLocation = "/ai/bennwittRepos/CloverCatcher/datasets/cloverDataSetcoco"
trainingArtifacts = "/ai/bennwittRepos/CloverCatcher/dataPuddle/trainingArtifacts"
device = "cuda"
projectName = "CloverCatcher"
runName = "CloverCatcherV4Base2Model"

wandb.login()


def generate_run_name(baseName):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    return f"{baseName}_{timestamp}"


runName = generate_run_name(projectName)
save_dir = Path(f"{trainingArtifacts}/{runName}")
save_dir.mkdir(parents=True, exist_ok=True)

save_dir_string = str(save_dir)

model.train(
    dataset_dir=datasetLocation,
    output_dir=save_dir_string,
    wandb=True,
    project="LuckDetector",
    device=device,
    epochs=25,
    batch_size=16,
    grad_accum_steps=1,
    lr=1e-4,
    checkpoint_interval=3,
    run=runName,
    use_ema=True,
    gradient_checkpointing=True,
    early_stopping=True,
    early_stopping_patience=5,
    num_classes=2,
)

# best for fine tuning
# "rf-detr-base-2.pth": "https://storage.googleapis.com/rfdetr/rf-detr-base-2.pth",
# "rf-detr-large.pth": "https://storage.googleapis.com/rfdetr/rf-detr-large.pth"
