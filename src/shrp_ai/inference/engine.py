from __future__ import annotations


class InferenceEngine:
    def __init__(self, model, device: str = "cpu"):
        self.model = model
        self.device = device

    def predict(self, x):
        if hasattr(self.model, 'forward'):
            return self.model.forward(x)
        elif callable(self.model):
            return self.model(x)
        return x

    def predict_numpy(self, x):
        out = self.predict(x)
        import numpy as np
        if hasattr(out, 'numpy'):
            try:
                return out.numpy()
            except Exception:
                pass
        return np.array(out)
