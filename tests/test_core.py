import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np

from shrp_ai.nn.models import SHRPNet
from shrp_ai.training.trainer import Trainer
from shrp_ai.inference.engine import InferenceEngine
from shrp_ai.utils.checkpoint import Checkpoint
from shrp_ai.config.config import Config, ModelConfig, TrainConfig


def test_model_init():
    model = SHRPNet(input_dim=10, hidden_dims=[32, 16], output_dim=1)
    assert model is not None


def test_forward_pass():
    model = SHRPNet(input_dim=10, hidden_dims=[16], output_dim=2)
    x = np.random.randn(4, 10)
    y = model.forward(x)
    assert y.shape == (4, 2)


def test_loss_calculation():
    model = SHRPNet(input_dim=5, hidden_dims=[8], output_dim=1)
    x = np.random.randn(3, 5)
    y = np.random.randn(3, 1)
    out = model.forward(x)
    loss = np.mean((out - y) ** 2)
    assert loss >= 0


def test_training_step():
    model = SHRPNet(input_dim=4, hidden_dims=[12], output_dim=1)
    trainer = Trainer(model)
    x = np.random.randn(8, 4)
    y = np.random.randn(8, 1)
    loss = trainer.train_step(x, y)
    assert isinstance(loss, float)


def test_inference():
    model = SHRPNet(input_dim=6, hidden_dims=[10], output_dim=3)
    engine = InferenceEngine(model)
    x = np.random.randn(2, 6)
    out = engine.predict(x)
    assert out.shape == (2, 3)


def test_checkpoint_save_load(tmp_path):
    model = SHRPNet(input_dim=3, hidden_dims=[6], output_dim=1)
    ckpt = tmp_path / 'model.json'
    Checkpoint.save({'w': [1, 2, 3]}, ckpt)
    data = Checkpoint.load(ckpt)
    assert data['data']['w'] == [1, 2, 3]


def test_cpu_compatibility():
    model = SHRPNet(input_dim=2, hidden_dims=[4], output_dim=1)
    x = np.random.randn(1, 2)
    y = model.forward(x)
    assert y.shape == (1, 1)
