#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
from typing import Any, Dict

import numpy as np
import torchvision.transforms as pth_transforms
from classy_vision.dataset.transforms import register_transform
from classy_vision.dataset.transforms.classy_transform import ClassyTransform


@register_transform("ImgPilToMultiCrop")
class ImgPilToMultiCrop(ClassyTransform):
    """
    Convert a PIL image to Multi-resolution Crops
    Input
    - PIL Image
    Returns
    - list containing crops
    This transform was proposed in SwAV - https://arxiv.org/abs/2006.09882
    """

    def __init__(self, total_nmb_crops, nmb_crops, size_crops, crop_scales):
        """
        Returns total_nmb_crops square crops of an image. Each crop is a random crop
        extracted according to the parameters specified in size_crops and crop_scales.
        For ease of use, one can specify `nmb_crops` which removes the need to repeat
        parameters.

        Inputs:
        - total_nmb_crops (int): Total number of crops to extract
        - nmb_crops (List or Tuple of ints): Specifies the number of `type' of crops.
        - size_crops (List or Tuple of ints): Specifies the height (height = width)
                                              of each patch
        - crop_scales (List or Tuple containing [float, float]): Scale of the crop

        Example usage:
        - (total_nmb_crops=2, nmb_crops=[1, 1],
           size_crops=[224, 96], crop_scales=[(0.14, 1.), (0.05, 0.14)])
           Extracts 2 crops total of size 224x224 and 96x96
        - (total_nmb_crops=2, nmb_crops=[1, 2],
           size_crops=[224, 96], crop_scales=[(0.14, 1.), (0.05, 0.14)])
           Extracts 3 crops total: 1 of size 224x224 and 2 of size 96x96
        """

        assert np.sum(nmb_crops) == total_nmb_crops
        assert len(size_crops) == len(nmb_crops)
        assert len(size_crops) == len(crop_scales)

        trans = []
        for i, sc in enumerate(size_crops):
            trans.extend(
                [
                    pth_transforms.Compose(
                        [pth_transforms.RandomResizedCrop(sc, scale=crop_scales[i])]
                    )
                ]
                * nmb_crops[i]
            )

        self.transforms = trans

    def __call__(self, image):
        return list(map(lambda trans: trans(image), self.transforms))

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "ImgPilToMultiCrop":
        return cls(**config)
