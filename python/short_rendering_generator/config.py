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

import executors

out_directory = "/home/madam/tmp"
#out_directory = "/home/acelarek/tmp"

#scenes = {"torus", "kitchen", "sponza", "bottle", "door", "bathroom"}
#integrators = {"pt", "bdpt", "memlt", "pssmlt"}

scenes = {"torus", "kitchen", "sponza", "bottle", "door", "bathroom",
          "boxRoughn1O256Light25",   "boxRoughn1O256Light100", "boxRoughn1O256Light400",
          "boxRoughn1O2048Light100",                            "boxRoughn1O32Light100"}
integrators = {"pt", "memlt", "pssmlt"}
#integrators = {"pssmlt"}

modelPath = "/home/madam/Documents/work/tuw/models"
#modelPath = "/home/acelarek/Documents/mitsuba_models"
scene_files = {'torus':      f"{modelPath}/torus/rectLight.xml",
               'kitchen':    f"{modelPath}/kitchen/kitchen.xml",
               'sponza':     f"{modelPath}/sponza/sponza.xml",
               'bottle':     f"{modelPath}/bottle/bottle.xml",
               'door':       f"{modelPath}/door/objLight.xml",
               'bathroom':   f"{modelPath}/bathroom/bathroom.xml",
               'boxLight25':    f'{modelPath}/aaltoBox/aaltoBox.xml -D lightSize=0.25 -D lightRadiance="1280 1280 1280"',
               'boxLight100':   f'{modelPath}/aaltoBox/aaltoBox.xml -D lightSize=1 -D lightRadiance="80 80 80"',
               'boxLight400':   f'{modelPath}/aaltoBox/aaltoBox.xml -D lightSize=4 -D lightRadiance="5 5 5"',
               'boxRoughn1O256Light25':    f'{modelPath}/aaltoBox/aaltoBox.xml -D glassRoughness=0.00390625 -D lightSize=0.25 -D lightRadiance="1280 1280 1280"',
               'boxRoughn1O256Light100':   f'{modelPath}/aaltoBox/aaltoBox.xml -D glassRoughness=0.00390625 -D lightSize=1 -D lightRadiance="80 80 80"',
               'boxRoughn1O256Light400':   f'{modelPath}/aaltoBox/aaltoBox.xml -D glassRoughness=0.00390625 -D lightSize=4 -D lightRadiance="5 5 5"',
               'boxRoughn1O2048Light100':   f'{modelPath}/aaltoBox/aaltoBox.xml -D glassRoughness=0.00048828125 -D lightSize=1 -D lightRadiance="80 80 80"',
               'boxRoughn1O32Light100':   f'{modelPath}/aaltoBox/aaltoBox.xml -D glassRoughness=0.03125 -D lightSize=1 -D lightRadiance="80 80 80"',
               }

integrator_files = {'pt':        f"{modelPath}/algos_uniTime/pt.xml",
                    'bdpt':      f"{modelPath}/algos_uniTime/bdpt.xml",
                    'memlt':     f"{modelPath}/algos_uniTime/memlt.xml",
                    'pssmlt':    f"{modelPath}/algos_uniTime/pssmlt.xml",
                    'pt4':       f'{modelPath}/algos_uniTime/pt.xml -D samplerType="ldsampler"',
                    'pt16':      f'{modelPath}/algos_uniTime/pt.xml -D samplerType="ldsampler"',
                    'pt64':     f'{modelPath}/algos_uniTime/pt.xml -D samplerType="ldsampler"',
                    'pt256':     f'{modelPath}/algos_uniTime/pt.xml -D samplerType="ldsampler"',
                    }

n_renderings = 4000
n_time_measurements = 20
n_course_budget_measurements = 1
n_precise_budget_measurements = 4
target_render_budget_sec = 10;

render_command_executor = executors.Parallel(16)

def render_command_builder(scene, algorithm, budget, seed, out_file):
    return f"mitsuba -p 1 -o {out_file} {scene_files[scene]} -D integrator={integrator_files[algorithm]} -S {seed} -D sampleCount={budget}";
