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

import numpy as np
import config
import image_handling
import file_handling

def comp(scene, integrator):
    files = file_handling.files_for(scene, integrator, config)
    aggr = image_handling.OnlineAvgAndVar(512, 512, 3) 
    for f in files.paths: 
        i = config.imread_fun(f) 
        aggr.update(i)
    (mean, var) = aggr.finalize()
    
    config.imwrite_fun(f"{config.base_path}/../aggr/{scene}_mean_{integrator}.png", mean)
    config.imwrite_fun(f"{config.base_path}/../aggr/{scene}_var_{integrator}.png", var)
    config.imwrite_fun(f"{config.base_path}/../aggr/{scene}_stddev_{integrator}.png", np.sqrt(var))
    stddev_lum_cm = image_handling.colour_mapped(image_handling.rgb_to_lum(np.sqrt(var)), 0, 2);
    config.imwrite_fun(f"{config.base_path}/../aggr/{scene}_stddev_lumCm_{integrator}.png", stddev_lum_cm)

comp('torus', 'pt')
comp('torus', 'memlt')
