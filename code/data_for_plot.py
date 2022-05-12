#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：cse6140 
@File    ：data_for_plot.py
@Author  ：Jiawei
@Date    ：11/27/21 12:28 PM

Generate trace file for plot drawing
'''

import time
import os


run_times = 100

# Run local search1
for _ in range(run_times):
    seed = int(time.time())
    alg = 'LS1'
    os.system(f'python3 main.py -inst ../output/plot_data -alg {alg} -time 600 -seed {seed}')
    print(f'finished iteration {_} for {alg}')

# Run local search2
for _ in range(run_times):
    seed = int(time.time())
    alg = 'LS2'
    os.system(f'python3 main.py -inst ../output/plot_data -alg {alg} -time 600 -seed {seed}')
    print(f'finished iteration {_} for {alg}')