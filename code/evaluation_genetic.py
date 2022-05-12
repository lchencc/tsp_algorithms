import os
import csv
import glob
from LS1 import Genetic
from main import read_data
import pandas as pd
import time

fpath = "../DATA/"
files = glob.glob(fpath + '*.tsp')

# Set hyper-parameter
select_method = 'r'  # 'r' for rank selection; 'p' for proportional selection
init_method = 'n'  # 'n' for nearest neighbor; 'r' for random
mutation_method = 'local_search'

with open(f'tracking_file_select{select_method}_init{init_method}_{mutation_method}.csv', 'w', newline='') as output_file:
    fieldnames = ['Iteration', 'Instance', 'Solution', 'Initial_Solution', 'System_time', 'Cpu_time']
    csv_writer = csv.DictWriter(output_file, delimiter=',', fieldnames=fieldnames)
    csv_writer.writeheader()

    for i in range(1):
        for file in files:
            res = read_data(file)
            myGenetic = Genetic(res['XY'], seed=10, mutation_method=mutation_method)

            # Run algorithm and record execution time, cpu time and system time in seconds
            start_cpu_time = time.process_time()
            start_system_time = time.time()
            shortest_path, initial_shortest_path = myGenetic.find_path(select=select_method, init=init_method)
            cpu_time = time.process_time() - start_cpu_time
            system_time = time.time() - start_system_time

            # write result in csv
            filename = os.path.basename(file).replace('.tsp', '')
            print(f'now is doing iteration {i} for {filename}')
            result_dict = {'Iteration': i,
                           'Instance': filename,
                           'Solution': f'{shortest_path:.2f}',
                           'Initial_Solution': f'{initial_shortest_path:.2f}',
                           'System_time': f'{system_time:.2f}',
                           'Cpu_time': f'{cpu_time:.2f}'
                           }
            csv_writer.writerow(result_dict)


