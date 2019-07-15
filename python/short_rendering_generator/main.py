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

import re
import config
import warnings
from shortrenderinggenerator import ShortRenderingGenerator

#def renderBudgetFromIntegrator(scene, integrator):
    #search = re.search('\d+', integrator)
    #if search:
        #return int(search.group(0))
    
    #warnings.warn(f" budget not found in {integrator}")
    #return 1;

#config.scenes = {"torus", "sponza"}
#config.integrators = {"pt4", "pt16", "pt64", "pt256"}
#config.n_renderings = 1000

#tester = ShortRenderingGenerator(config)
#tester.render_budget_for = renderBudgetFromIntegrator
#rendering_budgets = {}
#for scene in config.scenes:
    #for integrator in config.integrators:
        #budget = tester.render_budget_for(scene, integrator)
        #render_time = tester.estimate_render_time_for(scene, integrator, budget, config.n_time_measurements)
        #rendering_budgets[(scene, integrator)] = (budget, render_time)

#for scene in config.scenes:
    #for integrator in config.integrators:
        #(budget, render_time) = rendering_budgets[(scene, integrator)];
        #print(f"{scene} / {integrator} / budget: {budget} = {render_time}")

#tester.generate()


#config.scenes = {"torus", "kitchen", "sponza", "bottle", "door", "bathroom"}
config.scenes = {"boxRoughn1O2048Light100", "boxRoughn1O32Light100"}
#config.integrators = {"pt", "pssmlt", "memlt"}

tester = ShortRenderingGenerator(config)
rendering_budgets = {}
for scene in config.scenes:
    for integrator in config.integrators:
        budget = tester.render_budget_for(scene, integrator)
        render_time = tester.estimate_render_time_for(scene, integrator, budget, config.n_time_measurements)
        rendering_budgets[(scene, integrator)] = (budget, render_time)

for scene in config.scenes:
    for integrator in config.integrators:
        (budget, render_time) = rendering_budgets[(scene, integrator)];
        print(f"{scene} / {integrator} / budget: {budget} = {render_time}")

tester.generate()

config.n_renderings = 16000
config.scenes = {"torus"}
config.integrators = {"pt", "pssmlt", "memlt"}
rendering_budgets = {}
for scene in config.scenes:
    for integrator in config.integrators:
        budget = tester.render_budget_for(scene, integrator)
        render_time = tester.estimate_render_time_for(scene, integrator, budget, config.n_time_measurements)
        rendering_budgets[(scene, integrator)] = (budget, render_time)

for scene in config.scenes:
    for integrator in config.integrators:
        (budget, render_time) = rendering_budgets[(scene, integrator)];
        print(f"{scene} / {integrator} / budget: {budget} = {render_time}")

tester.generate()





