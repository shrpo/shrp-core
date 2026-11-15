# SHRP AI — Phase 3: Hybrid Learning System Research (Architecture Only)

**Project:** F:\Ai\SHRP_AI  
**Status:** Phase 2.1 Complete (19/19 tests passing)  
**Stage:** Research and Architecture Only — No implementation/modification of existing files  
**Date:** 2025-11-11

## 1. Analysis of the Current Learning Engine

### How it works (Phase 2.1)
- **Forward:** SimpleLinear.forward() stores cache x, computes y = xW + b. SHRPNet chains layers sequentially.
- **Loss:** MSELoss computes mean((pred-target)^2), stores pred/target, returns gradient 2*(pred-target)/n via backward().
- **Backprop:** SimpleLinear.backward(dout) computes dW = x^T @ dout, db = sum(dout), returns dx = dout @ W^T. SHRPNet.backward() propagates in reverse order.
- **Optimization:** SGD.step() calls model.step(lr), each layer does W -= lr*dW, b -= lr*db.
- **Training:** Trainer.train_step() does forward -> loss -> backward -> optimizer.step(); fit() handles epochs/batches/shuffling/validation/early stopping.
- **Checkpointing:** Checkpoint.save/load_model_checkpoint() serializes layer weights/biases and arch metadata to JSON.

### Confirmed capabilities
- Real gradient computation verified via finite differences
- Loss reduces on y=2x+1 (4.64 -> 0.00014)
- Weights/biases updated, predictions improve
- CPU-only, NumPy-based, low memory footprint

### Limitations
- Only linear layers (no activations with gradients)
- Fully supervised, requires labeled pairs
- Global error signal via backprop
- Memory grows with batch/cache
- No sparse-reward/unsupervised/continual mechanisms
- Hard to train components independently

## 2. Role and Mechanisms of Each Learning Approach

| Approach | Established Mechanism | Role in SHRP | Notes |
|---------|---------------------|--------------|-------|
| Hebbian Learning | Cells that fire together wire together. dW ~ x_i x_j (Hebb/Oja/BCM) | Correlation discovery, associative memory, local tuning | Unsupervised, local; needs normalization to be stable |
| Reinforcement Learning | TD learning, policy gradients, Q-learning via rewards/returns | Goal-directed learning from sparse/delayed feedback | No dense labels needed; needs exploration |
| Self-Supervised Learning | Pretext tasks (reconstruction/contrastive/predictive) | Learn from unlabeled data, build representations | Widely used; reduces label dependence |
| Evolutionary Learning | GA/ES/CMA-ES over population with fitness selection | Gradient-free optimization, architecture search | Robust to non-differentiable objectives; sample-inefficient |
| Local Learning | Updates from local info (equilibrium prop, predictive coding) | Layer-wise training, parallelism, reduced BP dependency | Active research; some forms approximate BP |

## 3. Conflicts, Dependencies, and Synergies
- Conflicts: global BP vs local/temporal/fitness-based credit assignment
- Dependencies: shared weights/activations, normalization, signal routing
- Synergies: SSL+Hebbian for features, RL neuromodulation for plasticity, Evolutionary for meta-optimization, Local Learning for efficiency

## 4. Preliminary Mathematical Design
- Hebbian (Oja): Delta W = eta_h (h^T h_prev - W * diag(h^T h))
- SSL reconstruction: L_ssl = ||x - x_hat||^2
- RL (TD): delta = r + gamma V(s') - V(s), three-factor Delta W ~ m * x_i * y_j
- Evolutionary: selection/mutation/crossover on fitness F(theta)
- Unified: Delta W = sum u_k Delta W_k with coordinator weights u_k by context, normalization/clipping

## 5. Information Exchange and Coordination
Forward pass -> compute all signals (supervised/SSL/RL/Hebbian/local) -> neuromodulation -> coordinator arbitration -> combined update -> meta-evolutionary loop. Keep BP as optional path initially.

## 6. Small NumPy-based Experiments
E1 Hebbian PCA-like; E2 Local SSL autoencoder; E3 RL 4x4 gridworld; E4 Neuromodulated Hebbian; E5 Evolutionary XOR; E6 Hybrid vs BP baseline with ablations.

## 7. Fair Comparisons
Compare by data efficiency, compute (FLOPs/ops/time), same architecture/capacity, same test sets/seeds, account for different update frequencies. Test ablations.

## 8. Hardware and Resource Estimates (7GB RAM, CPU-only)
Hebbian/SSL/RL small, Evolutionary pop<=20 sequential: peak < 300 MB RAM, trivial CPU. Well within constraints.

## 9. Feasibility Assessment
HIGH for research/experiments, MODERATE for production claims. Main risks: integration complexity, need for careful ablations, avoid unsubstantiated superiority claims.

## 10. Verdict
Keep Phase 2.1 (BP+SGD) as baseline. Hybrid is hypothesis-driven. Validate incrementally with small NumPy experiments. No implementation yet - awaiting review/approval.

**Report:** docs/PHASE_3_LEARNING_ARCHITECTURE.md
