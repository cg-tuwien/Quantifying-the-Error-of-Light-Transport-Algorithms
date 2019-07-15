# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import matplotlib
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap

import config
import madam_cm

madam_cm.cm_linSeg(0.4)

test_cmp = LinearSegmentedColormap.from_list('madam', madam_cm.cm_data, N=256)
normaliser = matplotlib.colors.Normalize(vmin=0, vmax=2**16, clip=True)
mapper = cm.ScalarMappable(norm=normaliser, cmap=test_cmp)
Icolours = mapper.to_rgba(Is)
config.imwrite_fun("test.png", Icolours)