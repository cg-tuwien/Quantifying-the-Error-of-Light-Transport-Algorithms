#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 14:14:34 2019

@author: madam
"""
import numpy as np
import matplotlib.cm

import madam_cm
import constants

def rgb_to_lum(rgb_image):
    return np.sum(rgb_image * constants.luminance_factors, 2)

def colour_mapped(mono, low, high):
    if mono.ndim > 2:
        raise Exception("colour_map is only applicable for mono matrices")
      
    normaliser = matplotlib.colors.Normalize(vmin=low, vmax=high, clip=True)
    mapper = matplotlib.cm.ScalarMappable(norm=normaliser, cmap=madam_cm.cm_linSeg)
    return mapper.to_rgba(mono);

def gammaCorrected(image):
    return image ** constants.gamma_correction;