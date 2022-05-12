import os
import glob
import csv 


def read_solutions():
    """
    Given solution.csv file 
    
    params:
    
    returns:
    res = dict, map from city name to optimum solution
    """
    filename = "../DATA/solutions.csv"
    city2opt = {}
    
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader) # ignore the header
    
        for row in csvreader:
            city2opt[row[0]] = float(row[1])

    return city2opt

def get_time_and_result(datpath, city, algorithm, cutoff):
    """
    Given solution.csv file 
    
    params:
    
    returns:
    res = dict, map from city name to optimum solution
    """
    lines = []

    if algorithm not in ["LS1", "LS2"]:
        fname = datpath + "{}_{}_{}.trace".format(city, algorithm, cutoff)
        with open(fname) as f:
            lines = f.readlines()
        return float(lines[-1].split(",")[0]), float(lines[-1].split(",")[1])
    else:
        time, res = 0, 0
        fnames = glob.glob(datpath + "tmp/{}_{}_{}_*.trace".format(city, algorithm, cutoff))
        for i in range(10):
            fname = fnames[i]
            with open(fname) as f:
                lines = f.readlines()
            time += float(lines[-1].split(",")[0])
            res += float(lines[-1].split(",")[1])
        return time / 10.0, res / 10.0


def calculate_comprehensive_tables():
    """
    calculate and write comprehensive tables
    
    params:
    
    returns:

    """

    datpath = "../output/"
    output_dir = "../output/evaluation/"
    if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    temp_dir = "../output/temp/"
    if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

    # ffs = glob.glob(datpath + "*.trace")
    cities = ["Atlanta", "berlin52", "Boston", "Champaign", "Cincinnati", "Denver", 
    "NYC", "Philadelphia", "Roanoke", "SanFrancisco", "Toronto", "UKansasState", "UMissouri"]
    approaches = ["BnB", "Approx", "LS1", "LS2"]

    city2opt = read_solutions()
    for algorithm in approaches:
        ###############################
        if algorithm != "LS2":
            continue
        ###############################
        rows = []
        cutoff = 600
        for city in cities:
            time, res = get_time_and_result(datpath, city, algorithm, cutoff)
            trans = "Berlin" if city == "berlin52" else city
            opt = city2opt[trans]
            rows.append([city, time, res, (res - opt) / opt])
            #rows.append(["{:.2f}, {}, {:.2f}\n".format(time, res, (res - opt) / opt)])

        filename = output_dir + "{}_{}_comprehensive_table.csv".format(algorithm, cutoff)
        fields = ["Dataset", "Time (s)", "Sol.Qual.", "RelErr"]
        with open(filename, 'w') as csvfile: 
            csvwriter = csv.writer(csvfile) 
            csvwriter.writerow(fields)
            csvwriter.writerows(rows)


calculate_comprehensive_tables()
