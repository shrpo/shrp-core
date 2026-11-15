import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from shrp_ai.nn.models import SHRPNet
from shrp_ai.training.trainer import Trainer
from shrp_ai.training.optim import SGD
from shrp_ai.nn.loss import MSELoss


def main():
    np.random.seed(42)
    # y = 2x + 1
    X_train = np.linspace(-1, 1, 50).reshape(-1, 1)
    y_train = 2 * X_train + 1 + 0.01 * np.random.randn(*X_train.shape)
    X_val = np.linspace(-0.5, 0.5, 10).reshape(-1, 1)
    y_val = 2 * X_val + 1

    model = SHRPNet(1, [], 1)
    w0 = model.layers[0].W.copy()
    b0 = model.layers[0].b.copy()

    trainer = Trainer(model, optimizer=SGD(lr=0.01), criterion=MSELoss())
    initial_loss = trainer.evaluate(X_train, y_train)
    print(f'Initial train loss: {initial_loss}')

    history = trainer.fit(X_train, y_train, X_val, y_val, epochs=200, batch_size=16, shuffle=True)
    final_loss = trainer.evaluate(X_train, y_train)
    val_loss = trainer.evaluate(X_val, y_val)
    print(f'Final train loss: {final_loss}')
    print(f'Final val loss: {val_loss}')
    print(f'Weights: w0={w0.flatten()} -> w={model.layers[0].W.flatten()}')
    print(f'Biases: b0={b0.flatten()} -> b={model.layers[0].b.flatten()}')
    # predictions
    x_test = np.array([[0.0], [1.0], [-1.0]])
    preds = model.forward(x_test)
    print(f'Preds for [0,1,-1]: {preds.flatten()} (expect ~[1,3,-1])')


if __name__ == '__main__':
    main()
