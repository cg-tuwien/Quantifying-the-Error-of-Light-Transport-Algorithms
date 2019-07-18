#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 15:52:53 2019

@author: madam
"""
import matplotlib.pyplot as plt
import numpy as np

def vis(scene, descriptors, config):
    fig, ax = plt.subplots()
    
    i = 0
    for d in descriptors:
        n = d.n()
        config.imwrite_fun(f"{config.out_path}/{scene}_N{n}/mean_{d.integrator.upper()}.png", d.meanImage())
        config.imwrite_fun(f"{config.out_path}/{scene}_N{n}/SDpp_{d.integrator.upper()}.png", d.sdPpImage(config))
        config.imwrite_fun(f"{config.out_path}/{scene}_N{n}/exampleShortRendering_{d.integrator.upper()}.png",
                           d.short_rendering_example)
        
        ensembleMean = d.ensembleMean()
        maxFreq = len(ensembleMean) - 1
        tail_yes = np.concatenate((d.lowerTail(config), np.flip(d.upperTail(config))))
        body_yes = np.concatenate((d.lowerBody(config), np.flip(d.upperBody(config))))
        head_yes = np.concatenate((d.lowerHead(config), np.flip(d.upperHead(config))))
        xes = np.concatenate((np.arange(0, maxFreq + 1), np.arange(maxFreq, -1, -1)))
        ax.fill(xes, tail_yes, alpha=0.2, facecolor=config.colours[i])
        ax.fill(xes, body_yes, alpha=0.2, facecolor=config.colours[i])
        ax.fill(xes, head_yes, alpha=0.4, facecolor=config.colours[i])
        
        ax.plot(np.arange(0, maxFreq + 1), ensembleMean, color=config.colours[i], label=d.label())
        i += 1
    
    ax.set(xlabel='frequency', ylabel='error', yscale='log', xlim=(0, maxFreq))
    ax.legend(title=f"{scene}, N={n}")
    
    fig.savefig(f"{config.out_path}/{scene}_N{n}/ese.png")
    fig.savefig(f"{config.out_path}/{scene}_N{n}/ese.svg")
    plt.close(fig)