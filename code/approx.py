
import time
import math

class Approx:
    
    def __init__(self, dat):
        """
        NEAREST NEIGHBOR Algorithm
        find the closest vertex not yet visited and add it in the tour
        
        params:
        dat = dict, inputs
        """
        
        self.coordinates = dat["XY"]
        
        self.n = len(self.coordinates)
        self.points = [s[0] for s in self.coordinates]
        self.X = [s[1] for s in self.coordinates]
        self.Y = [s[2] for s in self.coordinates]
        
        self.cost_matrix = [[0] * self.n for _ in range(self.n)]
        

    def calc_cost(self, p1, p2):
        """
        Calculate the distance of two points, p1 and p2
        
        params:
        p1, p2 = [x, y], [x, y]
        
        returns:
        distance = float
        """
        
        distance = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        
        return distance
    
    def calc_cost_matrix(self):
        """
        Calculate the distance matrix
        """
        
        for i in range(self.n):
            for j in range(self.n):
                p1, p2 = [self.X[i], self.Y[i]], [self.X[j], self.Y[j]]
                self.cost_matrix[i][j] = self.calc_cost(p1, p2)
    
    def search(self, start = 0):
        """
        Search the best cost and best path based on the start index
        
        params:
        start = int, start index
        
        returns:
        path = list, travel path
        cost = float, total cost
        """
        
        # set initial values
        cur, path, cost = start, [start], 0
        
        # record visited places
        visited = set()
        visited.add(start)
        
        # find the closest vertex not yet visited
        while len(visited) < self.n:
            cost_vector = self.cost_matrix[cur]
            index_list = [i for i in range(len(cost_vector)) if i not in visited]
            cost_list = [cost_vector[i] for i in index_list]
            
            min_cost = min(cost_list)
            min_index = index_list[cost_list.index(min_cost)]
            
            path.append(min_index)
            visited.add(min_index)
            cost += min_cost
            
            cur = min_index
        
        # connecting the end point to the start point
        cost += self.cost_matrix[min_index][start]
        
        path = [self.points[i] for i in path]
        cost = round(cost)
        
        return path, cost
    
    def find_path(self, cutoff = 600):
        """
        Loop through all start cities to find the best path

        params:
        cutoff = maximum running time
        
        returns:
        trace = list, running time and cost
        best_path = best running path
        best_cost = best cost
        """
        
        start_time = time.time()
        
        # get the cost matrix
        self.calc_cost_matrix()
        
        # initial values
        trace = []
        best_path, best_cost = None, float("inf")
        
        # find the best path and cost
        for i in range(self.n):
            path, cost = self.search(i)
            if cost < best_cost:
                cur_time = time.time() - start_time
                trace.append([round(cur_time, 2), cost])
                best_cost = cost
                best_path = path
            if time.time() - start_time > cutoff:
                break
        
        return trace, best_path, best_cost
    