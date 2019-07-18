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

import concurrent.futures
import math

import config
import descriptor_comp
import descriptor_vis

    
def compute_for_scene(scene):
    descriptors = []
    for i in config.integrators:
        descriptors.append(descriptor_comp.comp(scene, i, config))
    
    return (scene, descriptors)

def compute_for_config(config):
    i = 0
    printed = 0
    ## single threaded (well, numpy is doing some parallelisation under the hood)
#    for s in config.scenes:
#        (scene, descriptors) = compute_for_scene(s)
#        descriptor_vis.vis(scene, descriptors, config)
#        i += 1
#        percentage = math.floor(100 * i / len(config.scenes))
#        print("#" * (percentage - printed),  flush=True, end = '')
#        printed = percentage
    ## multi threaded
    with concurrent.futures.ProcessPoolExecutor(max_workers=config.n_workers) as executor:
        for (scene, descriptors) in executor.map(compute_for_scene, config.scenes):
            descriptor_vis.vis(scene, descriptors, config)
            i += 1
            percentage = math.floor(100 * i / len(config.scenes))
            print("#" * (percentage - printed),  flush=True, end = '')
            printed = percentage
    print()
    print("done")
    
config.max_n = 4000
compute_for_config(config)
config.out_path = f"{config.base_path}/python/relErr"
config.error_fun = config.constants.ERROR_FUN_RELATIVE