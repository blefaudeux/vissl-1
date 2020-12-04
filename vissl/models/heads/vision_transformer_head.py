# (c) Facebook, Inc. and its affiliates. Confidential and proprietary.

"""
Code modified from https://github.com/google-research/vision_transformer
and https://www.internalfb.com/D24714842, as per https://arxiv.org/abs/2010.11929
"""

# from typing import List
import copy
from collections import OrderedDict

import torch.nn as nn
from vissl.models.heads import register_model_head
from vissl.models.model_helpers import lecun_normal_init
from vissl.utils.hydra_config import AttrDict


@register_model_head("vision_transformer_head")
class VisionTransformerHead(nn.Module):
    """
    Code modified from https://github.com/google-research/vision_transformer
    and https://www.internalfb.com/D24714842, as per https://arxiv.org/abs/2010.11929

    Authors use a 2-layer MLP for pretraining and a single linear layer for
    fine-tuning. Thus a pre-training head would be called with something like
    ["vision_transformer_head", {"in_plane": D, "hidden_dim": D,
    "num_classes": K}], where D = hidden dimensionality and K = number of
    classes. A fine-tuning head would be called ["vision_transformer_head",
    {"in_plane", D, "num_classes": K].

    """
    def __init__(
            self,
            model_config: AttrDict,
            in_plane,
            num_classes,
            hidden_dim=None,
    ):
        super().__init__()
        if hidden_dim is None:
            layers = [("head", nn.Linear(in_plane, num_classes))]
        else:
            layers = [
                ("pre_logits", nn.Linear(in_plane, hidden_dim)),
                ("act", nn.Tanh()),
                ("head", nn.Linear(hidden_dim, num_classes)),
            ]
        self.layers = nn.Sequential(OrderedDict(layers))
        self.init_weights()

    def init_weights(self):
        if hasattr(self.layers, "pre_logits"):
            lecun_normal_init(
                self.layers.pre_logits.weight, fan_in=self.layers.pre_logits.in_features
            )
            nn.init.zeros_(self.layers.pre_logits.bias)
        nn.init.zeros_(self.layers.head.weight)
        nn.init.zeros_(self.layers.head.bias)

    @classmethod
    def from_config(cls, config):
        config = copy.deepcopy(config)
        config.pop("unique_id")
        return cls(**config)

    def forward(self, x):
        return self.layers(x)

