# Last modified: 2025-04-29 09:29:29
# Version: 0.0.1
from rfdetr import RFDETRBase

model = RFDETRBase()

model.train(
    dataset_dir=dataset.location, epochs=15, batch_size=16, grad_accum_steps=1, lr=1e-4
)
