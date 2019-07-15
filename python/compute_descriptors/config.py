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

import re # regexp
import warnings
import imageio
import numpy as np
import image_handling
from pathlib import Path

base_path = "/home/madam/tmp/shortRenderings"

#scenes = {"torus", "kitchen", "sponza", "bottle", "door", "bathroom"}
#integrators = {"pt", "bdpt", "memlt", "pssmlt"}

scenes = {"torus"}
integrators = {"pt", "memlt"}
file_ending = ".exr"
n = 20

imread_fun = imageio.imread # should return linear hdr float, 0 is black, 1 is white
def imwrite_fun(path, image):   # eats linear hdr float
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    image = image_handling.gamma_corrected(image)
    image = image * 255
    image = np.minimum(image, 255)
    imageio.imwrite(path, image.astype(np.uint8))
    

def sample_budget_extractor(path):
    search = re.search('_sampleBudget_(\d+)', path, re.IGNORECASE)
    if search:
        return int(search.group(1))
    
    warnings.warn(f"Sample budget not found in {path}")
    return 1;

def time_budget_extractor(path):
    search = re.search('_timeBudget_(\.?\d+\.?\d*)', path, re.IGNORECASE)
    if search:
        return float(search.group(1))
    
    warnings.warn(f"Time budget not found in {path}")
    return 1;
