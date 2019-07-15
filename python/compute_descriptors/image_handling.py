#
# Copyright (c) 2019, <copyright holder> <email>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY <copyright holder> <email> ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <copyright holder> <email> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import math
import numpy as np

import matplotlib
import matplotlib.cm

import madam_cm
import constants


def rgb_to_lum(rgb_image):
    return np.sum(rgb_image * constants.luminance_factors, 2)

def gamma_corrected(i):
    return i ** constants.gamma_correction

def colour_mapped(mono, low, high):
    if mono.ndim > 2:
        raise Exception("colour_map is only applicable for mono matrices")
      
    normaliser = matplotlib.colors.Normalize(vmin=low, vmax=high, clip=True)
    mapper = matplotlib.cm.ScalarMappable(norm=normaliser, cmap=madam_cm.cm_linSeg)
    return mapper.to_rgba(mono);

class OnlineAvgAndVar:
    def __init__(self, width, height, depth):
        self.mean = np.zeros((height, width, depth))
        self.M2 = np.zeros((height, width, depth))
        self.count = 0
    
    # adapted from wikipedia: https://en.wikipedia.org/w/index.php?title=Algorithms_for_calculating_variance&oldid=898576581#Welford's_online_algorithm
    # for a new value newValue, compute the new count, new mean, the new M2.
    # mean accumulates the mean of the entire dataset
    # M2 aggregates the squared distance from the mean
    # count aggregates the number of samples seen so far
    def update(self, newValue):
        if newValue.shape != self.mean.shape:
            raise Exception("shapes must match")
        self.count += 1 
        delta = newValue - self.mean
        self.mean += delta / self.count
        delta2 = newValue - self.mean
        self.M2 += delta * delta2

    # retrieve the mean, variance and sample variance from an aggregate
    def finalize(self):
        if self.count < 2:
            raise Exception("minimum nuber of samples is 2")
        else:
            return (self.mean, self.M2/(self.count - 1))

def cutOutSquare(data):
    height, width = data.shape
    size = min(width, height)
    rowStart = int(height / 2 - size / 2)
    rowEnd = int(height / 2 + size / 2)
    colStart = int(width / 2 - size / 2)
    colEnd = int(width / 2 + size / 2)
    return data[rowStart : rowEnd, colStart : colEnd]

class RadialAverage:
    def __init__(self):
        pass

    def __call__(self, data):
        data = cutOutSquare(data)
        size = data.shape[0]
        coords = self.__transform_radial_coords(self.__radial_coords(size))
        coords[0] += size / 2 # check
        coords[1] += size / 2 # check
        
        # draw samples / check
        # simple sampling
        # bilinear sampling
        # average over rows
        
        return coords
    
    def __radial_coords(self, size):
        n_radial_samples = size / 2 * 2 * math.pi
        return np.meshgrid(np.r_[0 : size/2 : 1] + 0.5 - (size % 2) / 2,
                           np.r_[0 : 2 * math.pi : 2 * math.pi / n_radial_samples])
        
    def __transform_radial_coords(self, coords):
        sini = np.sin(coords[1])
        cosini = np.cos(coords[1])
        radi = coords[0]
        return [radi * sini, radi * cosini]
        


