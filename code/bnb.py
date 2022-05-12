import math
import time

class BnB:
    def __init__(self, dat, cutoff):
        """
        Initial processing
        """
        
        self.points = [[x[1], x[2]] for x in dat]
        self.cutoff = cutoff
        self.n = len(self.points)
        
        self.cost_matrix = [[0] * self.n for _ in range(self.n)]
        self.visited={}
        
        self.trace = []
        self.best_path = []
        self.best_cost = float("inf")
    
    def calc_cost(self, p1, p2):
        """
        Calculate the distance of two points, p1 and p2
        """
        
        distance = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        
        return distance
    
    def calc_cost_info(self):
        """
        Process coordinates information
        """
        
        # calculate cost matrix and its index
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    p1, p2 = self.points[i], self.points[j]
                    self.cost_matrix[i][j] = self.calc_cost(p1, p2)
                else:
                    self.cost_matrix[i][j] = float("inf")
        self.cost_matrix_index = [sorted(range(len(x)), key = lambda f: x[f]) for x in self.cost_matrix]
        
        # calculate mapping information
        self.mapping = {}
        for i in range(self.n):
            for j in range(i + 1, self.n):
                self.mapping[self.cost_matrix[i][j]] = [i, j]
                
        # start calculation
        self.start_time = time.time()

    
    def branch_bound(self,path):
        """
        Calculate Branch and Bound
        """
        
        # check if key exists
        subtree = path[1:-1]
        key = "".join([str(x) for x in sorted(subtree)])
        if key in self.visited:
            return self.visited[key]
        
        # initialization:
        mapping = {}
        for i in range(self.n):
            if i not in subtree:
                mapping[i] = i
        
        # connect edges along the way
        total_cost = 0
        mapping_cost = sorted(list(self.mapping.keys()))
        while mapping_cost:
            cost = mapping_cost.pop(0)
            x, y = self.mapping[cost][0], self.mapping[cost][1]
            if x not in subtree and y not in subtree and mapping[x] != mapping[y]:
                total_cost = total_cost + cost
                pivot = mapping[y]
                for idx in mapping:
                    if mapping[idx] == pivot:
                        mapping[idx] = mapping[x]

        self.visited[key] = total_cost
        
        return total_cost
        
    def dfs(self, path = [0], total_cost = 0):
        """
        DFS method to find the optimal solution
        """
        
        # return the results if path is complete
        if len(path) == self.n:
            start, end = path[0], path[-1]
            total_cost += self.cost_matrix[end][start]
            if total_cost < self.best_cost:
                time_period = round(time.time() - self.start_time, 2)
                self.trace.append([time_period, int(total_cost)])
                self.best_path = list(path)
                self.best_cost = int(total_cost)
            return
        
        # return the results if time exceeds cutoff
        if time.time() - self.start_time > self.cutoff:
            return
        
        # otherwise, backtracking on the next possible value
        for i in range(self.n):
            next_point = self.cost_matrix_index[path[-1]][i]
            if next_point not in path:
                new_cost = total_cost + self.cost_matrix[path[-1]][next_point]
                path.append(next_point)
                if self.branch_bound(path) + new_cost < self.best_cost:
                    self.dfs(path, new_cost)
                path.pop()

    def find_path(self):
        
        self.calc_cost_info()
        self.dfs()
        
        return self.trace, self.best_path, self.best_cost
