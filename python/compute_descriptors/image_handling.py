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

def powerSpectrum(image):
    s = np.fft.fft2(image, axes=(0, 1))
    s = np.fft.fftshift(s)
    s = np.absolute(s)
    s = s * s
    return s

def cutOutSquare(data):
    height = data.shape[0]
    width = data.shape[1]
    size = min(width, height)
    rowStart = int(height / 2 - size / 2)
    rowEnd = int(height / 2 + size / 2)
    colStart = int(width / 2 - size / 2)
    colEnd = int(width / 2 + size / 2)
    return data[rowStart : rowEnd, colStart : colEnd, :]

def polar_transform(data):
    data = cutOutSquare(data)
    size = data.shape[0]
    coords = __transform_radial_coords(__radial_coords(size))
    coords[0] += size / 2 + 0.5
    coords[1] += size / 2 + 0.5
    
    # draw samples / check
    polar = __sample(data, coords)
    return polar

def radial_average(data):
    polar = polar_transform(data)
    # average over rows
    radialAverage = np.mean(polar, axis=0);
    
    return radialAverage

def __sample(image, coords):
    height, width, depth = image.shape
    ## simple nn sampling
    #return image[coords[0].astype(int), coords[1].astype(int), :];
    ## bilinear sampling
    tlF = [(coords[0] - 0.5), (coords[1] - 0.5)]
    trF = [(coords[0] + 0.5), (coords[1] - 0.5)]
    blF = [(coords[0] - 0.5), (coords[1] + 0.5)]
    brF = [(coords[0] + 0.5), (coords[1] + 0.5)]
    
    tlI = [tlF[0].astype(int), tlF[1].astype(int)]
    trI = [trF[0].astype(int), trF[1].astype(int)]
    blI = [blF[0].astype(int), blF[1].astype(int)]
    brI = [brF[0].astype(int), brF[1].astype(int)]
    
    tlP = (tlI[0] - tlF[0] + 1) * (tlI[1] - tlF[1] + 1)
    trP = (trF[0] - trI[0])     * (trI[1] - trF[1] + 1)
    blP = (blI[0] - blF[0] + 1) * (blF[1] - blI[1])
    brP = (brF[0] - brI[0])     * (brF[1] - brI[1])
    
#        pCheck = tlP + trP + blP + brP - 1;
#        pCheck *= pCheck;
#        pCheck = np.sum(pCheck);
#        pCheck /= (width * height);
#        assert pCheck < 0.0000001
    
    np.clip(tlI[0], 0, width - 1, out=tlI[0])
    np.clip(tlI[1], 0, height - 1, out=tlI[1])
    np.clip(trI[0], 0, width - 1, out=trI[0])
    np.clip(trI[1], 0, height - 1, out=trI[1])
    np.clip(blI[0], 0, width - 1, out=blI[0])
    np.clip(blI[1], 0, height - 1, out=blI[1])
    np.clip(brI[0], 0, width - 1, out=brI[0])
    np.clip(brI[1], 0, height - 1, out=brI[1])
    
    return image[tlI[0].astype(int), tlI[1].astype(int)] * tlP[:, :, np.newaxis] \
           + image[trI[0].astype(int), trI[1].astype(int)] * trP[:, :, np.newaxis] \
           + image[blI[0].astype(int), blI[1].astype(int)] * blP[:, :, np.newaxis]  \
           + image[brI[0].astype(int), brI[1].astype(int)] * brP[:, :, np.newaxis]

def __radial_coords(size):
    n_radial_samples = size * 4 #/ 2 * 2 * math.pi
    dAngle = 2 * math.pi / n_radial_samples
    # if data is 16x16, then fft2 puts dc term on +8+8, so this is the centre
    # if data is 17x17, then fft2 puts dc term on +8+8
    maxRadius = int((size - 1) / 2);
    return np.meshgrid(np.r_[0 : maxRadius + 1 : 1],
                       np.r_[0 : 2 * math.pi : dAngle])
    
def __transform_radial_coords(coords):
    sini = np.sin(coords[1])
    cosini = np.cos(coords[1])
    radi = coords[0]
    return [radi * sini, radi * cosini]
