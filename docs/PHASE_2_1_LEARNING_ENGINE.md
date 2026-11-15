# PHASE 2.1 LEARNING ENGINE - DOCUMENTATION

## Architecture Changes
- **nn/models.py**: Upgraded SimpleLinear with forward/backward, gradient caching, parameter updates. SHRPNet supports multi-layer backprop in reverse order.
- **nn/loss.py**: Added MSELoss with forward and backward (analytical gradient dL/dy = 2*(pred-target)/n)
- **training/optim.py**: Added SGD optimizer with learning rate validation
- **training/trainer.py**: Full training loop with train_step, evaluate_step, train_epoch, evaluate, fit; mini-batch support, shuffling, history tracking
- **utils/checkpoint.py**: Added save_model_checkpoint/load_model_checkpoint to save/restore actual layer weights/biases
- **experiments/phase_2_1_linear_learning.py**: Real learning experiment for y=2x+1
- **tests/test_learning.py**: 12 new tests including finite-difference gradient checks

## Gradient Implementation
- Linear: dW = X^T @ dout, db = sum(dout, axis=0), dX = dout @ W^T
- Backpropagates through layers in reverse order

## Backpropagation Flow
1. Forward pass stores activations/caches
2. Loss computes gradient w.r.t. predictions
3. Backward passes gradients through each layer in reverse order
4. Optimizer updates parameters

## Loss Calculation
- MSE = mean((pred-target)^2), gradient = 2*(pred-target)/n

## SGD Update Mechanism
- W := W - lr * dW, b := b - lr * db

## Checkpoint Format
- JSON with arch metadata and per-layer weights/biases (lists)

## Experiment Configuration
- y = 2x + 1, seed=42, 50 train + 10 val points, lr=0.01, batch_size=16, 200 epochs

## Test Results
- All existing tests (7) pass
- All new learning tests (12) pass
- Total: 19 passed

## Experiment Results
- Initial train loss: 4.64
- Final train loss: 0.00014
- Final val loss: 3.57e-5
- Weights: [-1.24] -> [1.98] (target ~2.0)
- Biases: [0.] -> [0.997] (target ~1.0)
- Predictions for [0,1,-1]: [0.997, 2.981, -0.987] (close to [1,3,-1])

## Known Limitations
- Only linear layers and MSE implemented
- No activation functions with gradients yet (linear only)
- Simple SGD only (no momentum/Adam)
- JSON checkpoints may have precision limits for very large models
- No GPU support (CPU-only by design)
- Limited to small models/datasets for this environment
