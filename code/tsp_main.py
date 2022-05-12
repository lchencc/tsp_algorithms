
import os
import argparse

# 1. Import Algorithms ----

from bnb import BnB
from approx import Approx
from LS1 import Genetic
from LS2 import SimulatedAnealing

# 2. Commond Arguments ----

params = argparse.ArgumentParser()
params.add_argument("-inst", dest = "fpath")
params.add_argument("-alg", dest = "algorithm")
params.add_argument("-time", dest = "cutoff", type = int)
params.add_argument("-seed", dest = "seed", type = int)
options = params.parse_args()

# 3. Define read/write file functions ----

def read_data(fname):
    """
    Given a file path, read and clean the data
    
    params:
    fname = str, file path
    
    returns:
    res = dict, a dictionary of data information
    """
    
    # read lines
    lines = []
    with open(fname) as f:
        lines = f.readlines()
    
    # clean data
    res, dat = {}, []
    found = False
    for line in lines:
        if not found:
            if "NODE_COORD_SECTION" in line:
                found = True
            else:
                vals = line.strip().split(": ")
                res[vals[0]] = vals[1]
        elif "EOF" in line:
            break
        else:
            vals = line.strip().split()
            dat.append([int(vals[0]), float(vals[1]), float(vals[2])])
        
    res["XY"] = dat
    
    return res

def write_data(dat,
               options,
               trace,
               best_path,
               best_cost):
    """
    Given the inputs, output the sol and trace
    
    params:
    dat: dict, original data
    options: list, paramters
    trace: list
    best_path: list
    best_cost: list
    path = str, output path
    """

    city = dat["NAME"]
    if "berlin" in city:
        city = "Berlin"
    fpath = options.fpath
    algorithm = options.algorithm
    cutoff = options.cutoff
    seed = options.seed
    
    fpath = "../output"
    os.makedirs(fpath, exist_ok = True)
    
    if seed is None:
        sol_name = "{}_{}_{}.sol".format(city, algorithm, cutoff)
        trace_name = "{}_{}_{}.trace".format(city, algorithm, cutoff)
    else:
        sol_name = "{}_{}_{}_{}.sol".format(city, algorithm, cutoff, seed)
        trace_name = "{}_{}_{}_{}.trace".format(city, algorithm, cutoff, seed)        
    
    sol_name = fpath + "/" + sol_name
    trace_name = fpath + "/" + trace_name
    
    with open(sol_name, "w") as f:
        f.write(str(best_cost) + "\n")
        f.write(", ".join([str(x) for x in best_path]))
    
    with open(trace_name, "w") as f:
        for tc in trace:
            f.write("{:.2f}, {}\n".format(tc[0], tc[1]))

# 4. Generate output ----
if options.algorithm == "Approx":
    dat = read_data(options.fpath)
    tsp = Approx(dat)
    trace, best_path, best_cost = tsp.find_path(cutoff = options.cutoff)
    write_data(dat, options, trace, best_path, best_cost)
        
elif options.algorithm == "BnB":
    dat = read_data(options.fpath)
    bnb = BnB(dat['XY'], options.cutoff)
    trace, best_path, best_cost = bnb.find_path()
    write_data(dat, options, trace, best_path, best_cost)
        
elif options.algorithm == "LS1":
    dat = read_data(options.fpath)
    genetic = Genetic(dat['XY'], seed = options.seed)
    trace, best_path, best_cost = genetic.find_path(cutoff = options.cutoff)
    write_data(dat, options, trace, best_path, best_cost)
        
elif options.algorithm == "LS2":
    dat = read_data(options.fpath)
    tsp = SimulatedAnealing(dat, seed = options.seed)
    trace, best_path, best_cost = tsp.find_path(cutoff = options.cutoff)
    write_data(dat, options, trace, best_path, best_cost)
