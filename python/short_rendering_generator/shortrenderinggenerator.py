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
import time
import executors
import config
import json
from pathlib import Path

import subprocess

class ShortRenderingGenerator:
    '''
    The Vehicle object contains lots of vehicles
    :param scenes: set of scene names
    :param `integrators`: set of integrator names
    :param `out_directory`: top output directory
    :param `render_command_builder`: factory for rendering command. it receives the scene name, the integrator name and the output path and returns a rendering command string
    :ivar arg: This is where we store arg
    '''
    
    def __init__(self, config):
        self.config = config
        self.cache_directory = Path(self.config.out_directory).joinpath('cache')
        
        cache_path = self.cache_directory.joinpath('render_budgets.cache')
        if cache_path.exists():
            f = open(cache_path, 'r')
            self.render_budgets = json.load(f)
        else:
            self.render_budgets = dict()
        
        cache_path = self.cache_directory.joinpath('render_times.cache')
        if cache_path.exists():
            f = open(cache_path, 'r')
            self.render_times = json.load(f)
        else:
            self.render_times = dict()
            
    def generate(self):
        work_items = set()
        for scene in self.config.scenes:
            for integrator in self.config.integrators:
                budget = self.render_budget_for(scene, integrator)
                assert self.config.n_renderings < 100000                    # less than 100 000 renderings should be a safe guess to have a different seed for each,
                                                                            # even if the seed base happens to be the same in two consecutive runs
                seedBase = (math.floor(time.time()) * 100000) % (2**31);    # new seed base every second, should be good enough, so that no two runs have the same seed base
                for i in range(0, self.config.n_renderings):
                    render_time = self.estimate_render_time_for(scene, integrator, budget, self.config.n_time_measurements)
                    seed = seedBase + i
                    out_name = f"{self.config.out_directory}/shortRenderings/{scene}/{integrator}_sampleBudget_{budget}_timeBudget_{render_time}/{i:05d}_seed{seed}"
                    out_part_name = f"{self.config.out_directory}/shortRenderings/{scene}/{integrator}_sampleBudget_{budget}_timeBudget_{render_time}/{i:05d}_seed"
                    check_command = f'ls -l {out_part_name}*  | grep "\.exr" | wc -l'
                    check_result = subprocess.run(check_command, shell=True, check=False, text=True, capture_output=True)
                    if int(check_result.stdout.strip()) >= 1:
                        continue
                    command = self.config.render_command_builder(scene, integrator, budget, seed, f"{out_name}.exr");
                    work_items.add(executors.WorkItem(command, out_name))
        
        print(f"Generating short renderings",  flush=True);
        self.config.render_command_executor(work_items)
        
    
    def render_budget_for(self, scene, integrator):
        if str((scene, integrator)) in self.render_budgets:
            return self.render_budgets[str((scene, integrator))]
        budget = 1
        budget_too_large = budget
        
        #approx, with 1/10th of the measurements
        while (self.estimate_render_time_for(scene, integrator, budget_too_large, math.ceil(self.config.n_course_budget_measurements)) < self.config.target_render_budget_sec * 1.3):
            if (self.estimate_render_time_for(scene, integrator, budget_too_large, math.ceil(self.config.n_course_budget_measurements)) < self.config.target_render_budget_sec / 1.3):
                budget = budget_too_large
            budget_too_large *= 2
        
        #precisely
        while (self.estimate_render_time_for(scene, integrator, budget, self.config.n_precise_budget_measurements) < self.config.target_render_budget_sec):
            new_budget = math.ceil((budget + budget_too_large) / 2)
            if (new_budget == budget_too_large):
                budget = new_budget
                break
            if (new_budget == budget):
                break;
            if (self.estimate_render_time_for(scene, integrator, new_budget, self.config.n_precise_budget_measurements) > self.config.target_render_budget_sec):
                budget_too_large = new_budget
            else:
                budget = new_budget
        
        self.render_budgets[str((scene, integrator))] = budget
        self.save_cache()
        return self.render_budgets[str((scene, integrator))];
    

    def estimate_render_time_for(self, scene, integrator, budget, n_measurements):
        if str((scene, integrator, budget, n_measurements)) in self.render_times:
            return self.render_times[str((scene, integrator, budget, n_measurements))]
        
        work_items = set()
        for i in range(0, n_measurements):
            seed = i
            out_name = f"{self.config.out_directory}/timeTest/{scene}/{integrator}/sampleBudget_{budget}/{i:05d}_seed{seed}"
            command = self.config.render_command_builder(scene, integrator, budget, seed, f"{out_name}.exr");
            work_items.add(executors.WorkItem(command, out_name))
        
        print(f"Measuring time for ({scene} / {integrator} / budget: {budget})",  flush=True);
        begin = time.time()
        executors.sequential(work_items)
        end = time.time()
        avg_rendering_time = (end - begin) / n_measurements
        print(f"Time for {scene} / {integrator}, budget {budget} is {avg_rendering_time} (N={n_measurements})",  flush=True);
        self.render_times[str((scene, integrator, budget, n_measurements))] = avg_rendering_time;
        self.save_cache()
        return avg_rendering_time
        
    def save_cache(self):
        self.cache_directory.mkdir(parents=True, exist_ok=True)
        f = open(self.cache_directory.joinpath('render_budgets.cache'), 'w')
        json.dump(self.render_budgets, f, indent=2, sort_keys=True)
        f.close
        
        f = open(self.cache_directory.joinpath('render_times.cache'), 'w')
        json.dump(self.render_times, f, indent=2, sort_keys=True)
        f.close



