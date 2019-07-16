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

import os
import warnings
from pathlib import Path

class FileList:
    def __init__(self, scene, integrator, sample_budget, time_budget, paths):
        self.scene = scene
        self.integrator = integrator
        self.sample_budget = sample_budget
        self.time_budget = time_budget
        self.paths = paths

def files_for(scene, integrator, config):
    scene_path = Path(config.short_renderings_path).joinpath(scene)
    integrator_paths = set()
    for f in os.scandir(scene_path):
        if f.is_dir() and f.name[0:len(integrator)] == integrator:
            integrator_paths.add(f.path)
    
    if len(integrator_paths) == 0:
        raise Exception(f"Data for {integrator} not found for scene {scene}!")
    
    if len(integrator_paths) > 1:
        warnings.warn(f"More than one directory found for {integrator} for scene {scene}. Using the first")
    
    integrator_path = integrator_paths.pop()
    paths = set()
    sample_budget = None
    time_budget = 0
    time_budget_n = 0
    for f in os.scandir(integrator_path):
        if f.is_file() and f.name[-len(config.file_ending):] == config.file_ending:
            if sample_budget is None:
                sample_budget = config.sample_budget_extractor(f.path)
            
            if sample_budget != config.sample_budget_extractor(f.path):
                raise Exception(f"Sample budget should be the same in all images ({f.path})")
            
            time_budget += config.time_budget_extractor(f.path)
            time_budget_n += 1
            
            paths.add(f.path)
        if len(paths) >= config.max_n:
            break;
    if time_budget_n != 0:
        time_budget /= time_budget_n
    
    return FileList(scene, integrator, sample_budget, time_budget, paths)
    
