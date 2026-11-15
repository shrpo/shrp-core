from __future__ import annotations

from typing import Dict

import numpy as np


class MultiTaskModel:
    def __init__(self, backbone, heads):
        self.backbone = backbone
        self.heads = heads

    def forward(self, x):
        features = self.backbone.forward(x) if hasattr(self.backbone, 'forward') else self.backbone(x)
        if hasattr(self.heads, 'items'):
            return {name: (head.forward(features) if hasattr(head, 'forward') else head(features)) for name, head in self.heads.items()}
        return features
