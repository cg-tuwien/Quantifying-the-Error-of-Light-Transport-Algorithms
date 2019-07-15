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
import subprocess
import concurrent.futures
from collections import namedtuple
from pathlib import Path


WorkItem = namedtuple('WorkItem', 'command out_name')

def printer(work_items):
    for work_item in work_items:
        print(work_item.command)
        
def executeOnSystem(work_item):
    Path(work_item.out_name).parent.mkdir(parents=True, exist_ok=True)
    dateTimeString = time.strftime('%Y-%m-%d %H:%M:%S')
    stdout = open(f"{work_item.out_name}.command.txt", "a")
    stdout.write(f"=========== {dateTimeString} ===========")
    stdout.write(work_item.command)
    stdout.close()
    
    output = subprocess.run(work_item.command, shell=True, check=False, text=True, capture_output=True)
    stdout = open(f"{work_item.out_name}.stdout.txt", "a")
    stdout.write(f"=========== {dateTimeString} ===========")
    stdout.write(output.stdout)
    stdout.close()
    
    stderr = open(f"{work_item.out_name}.stderr.txt", "a")
    stderr.write(f"=========== {dateTimeString} ===========")
    stderr.write(output.stderr)
    stderr.close()
    if len(output.stderr) > 0:
        print(f"\033[0;31;40m while executing \033[1;35;40m {work_item.command}\033[0;31;40m: \033[1;31;40m {output.stderr.rstrip()}  \033[0;37;40m",  flush=True)
    return work_item.out_name

def sequential(work_items):
    print("sequential executer",  flush=True);
    print("_"*100)
    i = 0
    printed = 0
    for work_item in work_items:
        executeOnSystem(work_item)
                                                                                                                                               
        i += 1
        percentage = math.floor(100 * i / len(work_items))
        
        print("#" * (percentage - printed),  flush=True, end = '')
        printed = percentage
    print()

class Parallel:
    def __init__(self, n_workers):
        self.n_workers = n_workers
    
    def __call__(self, work_items):
        print(f"parallel executor {self.n_workers} workers",  flush=True);
        print("_"*100)
        i = 0
        printed = 0
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.n_workers) as executor:
            for out_name in executor.map(executeOnSystem, work_items):
                i += 1
                percentage = math.floor(100 * i / len(work_items))
                print("#" * (percentage - printed),  flush=True, end = '')
                printed = percentage

        print()
        print("done")
