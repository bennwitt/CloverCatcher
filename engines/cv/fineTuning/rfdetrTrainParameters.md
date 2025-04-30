## 🧠 CloverCatcher Training Parameters

| Parameter                 | Description |
|--------------------------|-------------|
| `dataset_dir`            | Path to your COCO-style dataset directory. Must include `train/`, `valid/`, and `test/` folders each with `_annotations.coco.json`. |
| `output_dir`             | Directory where training outputs (checkpoints, logs) are stored. Used for tracking and resuming training runs. |
| `epochs`                 | Number of full passes over the dataset. More epochs improve performance but take longer. |
| `batch_size`             | Number of samples per step. Higher values train faster but use more memory. Tune alongside `grad_accum_steps`. |
| `grad_accum_steps`       | Number of steps to accumulate gradients before backprop. Useful for simulating large batches on low-memory GPUs. |
| `lr`                     | Base learning rate. Controls how fast the model learns. |
| `lr_encoder`             | Separate learning rate for the encoder backbone (if different from rest of the model). |
| `resolution`             | Input image size (must be divisible by 56). Higher = more detail but uses more memory. |
| `weight_decay`           | L2 regularization coefficient to help reduce overfitting. |
| `device`                 | Hardware to train on: `cpu` or `cuda`. Use `cuda` for GPU acceleration. |
| `use_ema`                | Enables Exponential Moving Average of weights to stabilize training and improve final performance. |
| `gradient_checkpointing` | Reduces memory usage by recomputing activations on backward pass. Slows training but saves RAM. |
| `checkpoint_interval`    | Save a checkpoint every N epochs. Useful for resuming and experiment tracking. |
| `resume`                 | Path to a `.ckpt` file to resume training from. Loads both weights and optimizer state. |
| `tensorboard`            | Enables local TensorBoard logging for real-time metric visualization. |
| `wandb`                  | Enables Weights & Biases logging for cloud-based experiment tracking. |
| `project`                | W&B project name. Organizes related runs under one project. |
| `run`                    | W&B run name. Distinguishes this training session within the project. |
| `early_stopping`         | Enable early stopping based on mAP stagnation. |
| `early_stopping_patience`| Number of epochs without improvement before stopping. |
| `early_stopping_min_delta` | Minimum mAP improvement to reset the early stop counter. |
| `early_stopping_use_ema` | Whether to use the EMA model to monitor early stopping criteria. |