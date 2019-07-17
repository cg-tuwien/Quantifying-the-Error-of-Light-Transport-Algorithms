#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 15:52:53 2019

@author: madam
"""

def vis(scene, descriptors, config):
    for d in descriptors:
        config.imwrite_fun(f"{config.base_path}/aggr/{scene}_mean_{d.integrator}.png", d.meanImage())
        config.imwrite_fun(f"{config.base_path}/aggr/{scene}_SDpp_{d.integrator}.png", d.sdPpImage(config))
    