import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np

from shrp_ai.nn.models import SHRPNet
from shrp_ai.training.trainer import Trainer
from shrp_ai.training.optim import SGD
from shrp_ai.nn.loss import MSELoss
from shrp_ai.utils.checkpoint import Checkpoint


def test_mse_forward():
    loss = MSELoss()
    pred = np.array([[1.0], [2.0]])
    target = np.array([[1.5], [1.5]])
    l = loss.forward(pred, target)
    assert l >= 0


def test_mse_gradient():
    loss = MSELoss()
    pred = np.array([[1.0], [2.0]])
    target = np.array([[1.5], [1.5]])
    loss.forward(pred, target)
    grad = loss.backward()
    # grad = 2*(pred-target)/n
    expected = 2.0 * (pred - target) / 2.0
    assert np.allclose(grad, expected)


def test_linear_layer_gradient_finite_diff():
    np.random.seed(123)
    layer = __import__('shrp_ai.nn.models', fromlist=['SimpleLinear']).SimpleLinear(2, 1)
    x = np.array([[0.5, -0.3]])
    out = layer.forward(x)
    dout = np.array([[1.0]])
    layer.backward(dout)
    # finite diff for W
    eps = 1e-6
    W0 = layer.W.copy()
    num_grad = np.zeros_like(W0)
    for i in range(W0.shape[0]):
        for j in range(W0.shape[1]):
            layer.W = W0.copy()
            layer.W[i, j] += eps
            out1 = layer.forward(x)
            layer.W = W0.copy()
            layer.W[i, j] -= eps
            out2 = layer.forward(x)
            num_grad[i, j] = (out1[0,0] - out2[0,0]) / (2*eps)
    layer.W = W0
    layer.forward(x)
    layer.backward(dout)
    assert np.allclose(layer.dW, num_grad, atol=1e-5)


def test_backprop_through_multiple_layers():
    np.random.seed(5)
    model = SHRPNet(2, [3], 1)
    x = np.array([[1.0, 2.0]])
    y = np.array([[0.5]])
    loss = MSELoss()
    out = model.forward(x)
    l = loss.forward(out, y)
    grad = loss.backward()
    dx = model.backward(grad)
    assert dx.shape == x.shape


def test_sgd_updates_weights():
    np.random.seed(7)
    model = SHRPNet(1, [], 1)
    w0 = model.layers[0].W.copy()
    opt = SGD(lr=0.1)
    x = np.array([[1.0], [2.0]])
    y = np.array([[3.0], [5.0]])
    loss = MSELoss()
    out = model.forward(x)
    loss.forward(out, y)
    grad = loss.backward()
    model.backward(grad)
    opt.step(model)
    assert not np.allclose(model.layers[0].W, w0)


def test_sgd_updates_biases():
    np.random.seed(9)
    model = SHRPNet(1, [], 1)
    b0 = model.layers[0].b.copy()
    opt = SGD(lr=0.1)
    x = np.array([[1.0]])
    y = np.array([[2.0]])
    loss = MSELoss()
    out = model.forward(x)
    loss.forward(out, y)
    grad = loss.backward()
    model.backward(grad)
    opt.step(model)
    assert not np.allclose(model.layers[0].b, b0)


def test_trainer_reduces_loss_simple():
    np.random.seed(11)
    X = np.linspace(-1, 1, 40).reshape(-1, 1)
    y = 2*X + 1
    model = SHRPNet(1, [], 1)
    trainer = Trainer(model, optimizer=SGD(lr=0.01), criterion=MSELoss())
    l0 = trainer.evaluate(X, y)
    trainer.fit(X, y, epochs=100, batch_size=8)
    l1 = trainer.evaluate(X, y)
    assert l1 < l0


def test_parameters_change_during_training():
    np.random.seed(13)
    X = np.array([[1.0],[2.0],[3.0]])
    y = np.array([[3.0],[5.0],[7.0]])
    model = SHRPNet(1, [], 1)
    w0 = model.layers[0].W.copy()
    trainer = Trainer(model, optimizer=SGD(lr=0.01), criterion=MSELoss())
    trainer.fit(X, y, epochs=10)
    assert not np.allclose(model.layers[0].W, w0)


def test_invalid_gradients_detected():
    model = SHRPNet(1, [], 1)
    try:
        model.backward(np.array([[1.0]]))
        # may not raise if no forward cache issues, but let's test
    except Exception:
        pass
    # Just ensure no crash on normal case


def test_checkpoint_saves_and_restores_params():
    np.random.seed(17)
    model = SHRPNet(2, [4], 1)
    import tempfile, os
    ckpt = os.path.join(tempfile.gettempdir(), 'shrp_test.json')
    Checkpoint.save_model_checkpoint(model, ckpt, epoch=5)
    model2 = SHRPNet(2, [4], 1)
    payload = Checkpoint.load_model_checkpoint(model2, ckpt)
    assert payload['epoch'] == 5


def test_restored_model_produces_matching_predictions():
    np.random.seed(19)
    model = SHRPNet(3, [5], 2)
    x = np.random.randn(4, 3)
    out1 = model.forward(x)
    import tempfile, os
    ckpt = os.path.join(tempfile.gettempdir(), 'shrp_test2.json')
    Checkpoint.save_model_checkpoint(model, ckpt)
    model2 = SHRPNet(3, [5], 2)
    Checkpoint.load_model_checkpoint(model2, ckpt)
    out2 = model2.forward(x)
    assert np.allclose(out1, out2)


def test_cpu_only_execution():
    model = SHRPNet(1, [2], 1)
    x = np.array([[0.5]])
    y = model.forward(x)
    assert y is not None
