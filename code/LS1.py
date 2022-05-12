import random
import pandas as pd
import numpy as np
from sklearn.metrics import pairwise_distances
import time


class Genetic:

    def __init__(self, dat, seed=0, num_population=40, prob_m=0.8, mutation_method='normal'):
        """

        Args:
            dat: list, first column: index, second column: X coordinate, third column: Y coordinate
            num_population: int, hyper-parameter for Genetic Algorithm
            prob_m: float, hyper-parameter for Genetic Algorithm
        """
        self.coordinates = np.array(dat)[:, 1:3]
        self.dist_mat = pairwise_distances(self.coordinates)
        self.number = self.coordinates.shape[0]
        self.num_population = min(num_population, self.number)
        self.prob_m = prob_m
        if seed is None:
            self.seed = 0
        else:
            self.seed = seed
        self.trace = []
        self.start_time = time.time()
        self.mutation_method = mutation_method
        np.random.seed(self.seed)
        random.seed(self.seed)

    def get_distance(self, path):
        """
        Compute the distance of a path
        parameter:

        path: list, the sequence of visted place

        return:
        distance: float
        """
        distance = 0
        for i in range(self.number - 1):
            distance += self.dist_mat[path[i]][path[i+1]]
        distance += self.dist_mat[path[self.number-1]][path[0]]
        return distance

    def get_fitness(self, path):
        """
        Compute the fitness function of an individual, calculated as 1 / distance
        Individuals with high fitness have a greater possibility of reproduction,
        Individuals with low fitness will be given up
        """
        return 1 / self.get_distance(path)

    def random_init(self):
        """
        Randomly generate a population for genetic algorithm

        Returns:
            population: dict, {"fitness": float, "path": np-array}
        """
        max_fitness = 0
        population = []
        for i in range(self.num_population):
            path = np.random.choice(self.number, self.number, replace=False)
            fitness = self.get_fitness(path)
            if fitness > max_fitness:
                max_fitness = fitness
                self.trace.append([round(time.time() - self.start_time, 2), int(1/fitness)])
            individual = {"fitness": fitness, "path": path}
            population.append(individual)
        return population

    def nearest_neighbor_init(self):
        """
        Generate a population using nearest_neighbor method

        Returns:
            population: dict, {"fitness": float, "path": np-array}

        """
        population = []
        start_points = np.random.choice(self.number, self.num_population, replace=False)
        df = pd.DataFrame(self.dist_mat)
        max_fitness = 0
        # Find nearest-neighbor path for each start point
        for point in start_points:
            not_visited = np.ones(self.number).astype(bool)
            not_visited[point] = False
            path = [point]
            current_place = point
            for i in range(self.number-1):
                # Find next place with minimum distance
                unvisited_neighbors = df.iloc[current_place, :][not_visited]
                next_place = unvisited_neighbors.idxmin()
                path.append(next_place)
                not_visited[next_place] = False
                current_place = next_place

            fitness = self.get_fitness(path)
            if fitness > max_fitness:
                max_fitness = fitness
                self.trace.append([round(time.time() - self.start_time, 2), int(1/fitness)])
            individual = {"fitness": fitness, "path": path}
            population.append(individual)
        return population

    def local_search(self, path):
        """
        Conducting 2-opt local search from the given path
        :param path: np-array
        :return: new_path: np-array

        """
        # print("call local search")
        best_neighbor = path
        previous_fitness = self.get_fitness(path)
        previous_path = path.copy()
        best_fitness = previous_fitness
        # Search all neighbors
        iteration = 0
        while True:
            iteration += 1
            # print(f'now is doing local search {iteration}')
            for i in range(self.number):
                for j in range(i, self.number):
                    new_path = path.copy()
                    new_path[i] = previous_path[j]
                    new_path[j] = previous_path[i]
                    new_fitness = self.get_fitness(new_path)
                    if new_fitness > best_fitness:
                        best_fitness = new_fitness
                        best_neighbor = new_path
            if best_fitness == previous_fitness:
                return best_neighbor
            else:
                previous_fitness = new_fitness
                previous_path = best_neighbor

    def select_parents(self, population, method='p'):
        """
        select parents to perform crossover, select parents based on a probability dereived from normalized
        parameters:
        population: A dict {"fitness": float, "path": np-array}
        returns:
        path1, path2: 2 np-array
        """
        population_fitness = list(map(lambda individual: individual['fitness'], population))

        if method == 'p':
            # Proportional Roulette Wheel Selection
            probabilities = [i / sum(population_fitness) for i in population_fitness]
        elif method == 'l':
            # Linear Roulette Wheel Selection
            population_fitness = [10 * i + 20 for i in population_fitness]
            probabilities = [i / sum(population_fitness) for i in population_fitness]
        elif method == 'r':
            # rank based
            population_fitness = [1/(i+3) for i in range(len(population))]
            probabilities = [i / sum(population_fitness) for i in population_fitness]

        selection = np.random.choice(self.num_population, 2, p=probabilities, replace=False)
        path1 = population[selection[0]]['path']
        path2 = population[selection[1]]['path']
        return path1, path2

    def crossover(self, path1, path2):
        """
        Conduct crossover by applying Partially-mapped crossover(PMX)
        Params:
        path1, path2: np-array
        Returns:
        child_path1, child_path2: list
        """
        cut_points = np.random.choice(self.number + 1, 2, replace=False)
        cut_points = np.sort(cut_points)

        def create_child(path_a, path_b):
            my_dict = {}
            child_path = np.zeros(self.number).astype('int64')

            # Update middle part of child path
            for i in range(cut_points[0], cut_points[1]):
                child_path[i] = path_b[i]
                my_dict[child_path[i]] = path_a[i]

            # Update left part
            for i in range(0, cut_points[0]):
                if path_a[i] in my_dict.keys():
                    child_path[i] = my_dict[path_a[i]]
                    while child_path[i] in my_dict.keys():
                        child_path[i] = my_dict[child_path[i]]
                else:
                    child_path[i] = path_a[i]
                # print(child_path)

            # Update right part
            for i in range(cut_points[1], self.number):
                if path_a[i] in my_dict.keys():
                    child_path[i] = my_dict[path_a[i]]
                    while child_path[i] in my_dict.keys():
                        child_path[i] = my_dict[child_path[i]]
                else:
                    child_path[i] = path_a[i]
                # print(child_path)
            return child_path

        child_path1 = create_child(path1, path2)
        child_path2 = create_child(path2, path1)

        return child_path1, child_path2

    def mutation(self, path, prob_m):
        """
        Applying a insertion mutation

        """
        if self.mutation_method == "local_search":
            return self.local_search(path)

        is_mutation = random.choices([False, True], weights=[1 - prob_m, prob_m])
        if is_mutation:
            cut_points = random.choices(range(self.number), k=2)
            cut_points = sorted(cut_points)
            insertion_list = path[np.asarray(range(cut_points[0], cut_points[1])).astype('int64')]
            new_path = np.delete(path, range(cut_points[0], cut_points[1]))
            insertion_point = np.random.choice(new_path.size, 1)
            new_path = np.insert(new_path, obj=insertion_point, values=insertion_list)
        return new_path

    def find_path(self, select='r', init='n', cutoff=600):
        """
        Find the shortest path
        :param select: string, method for selecting parents, p stands for traditional proportional wheel method
        :param init: string, method for initialize population,
                'r': for random init
                'n': for nearest neighbor init
        :param cutoff: int, maximum runnning time in seconds
        :return shortest_distance: float
        :return initial_shortest_distance: float, the shortest distance derived from the initialized population.
        it will be used to measure the contribution of genetic algorithm

        """
        start_time = time.time()
        if init == 'r':
            population = self.random_init()
        elif init == 'n':
            population = self.nearest_neighbor_init()
        population = sorted(population, key=lambda individual: individual['fitness'], reverse=True)
        shortest_distance = 1 / population[0]['fitness']
        previous_shortest_distance = shortest_distance
        converge_times = 0
        # print('initialization finished')
        for _ in range(10000000):
            # print(f'iteration {_}')
            path1, path2 = self.select_parents(population, select)
            new_path1, new_path2 = self.crossover(path1, path2)
            new_path1 = self.mutation(new_path1, self.prob_m)
            new_path2 = self.mutation(new_path2, self.prob_m)
            population.append({'fitness': self.get_fitness(new_path1), 'path': new_path1})
            population.append({'fitness': self.get_fitness(new_path2), 'path': new_path2})
            population = sorted(population, key=lambda individual: individual['fitness'], reverse=True)
            population = population[0:self.num_population]

            best_fitness = population[0]['fitness']
            shortest_distance = 1 / best_fitness

            # Check whether upgrade the best result so far
            if shortest_distance == previous_shortest_distance:
                converge_times += 1
            else:  # new best record
                converge_times = 0
                previous_shortest_distance = shortest_distance
                self.trace.append([round(time.time() - self.start_time, 2), int(shortest_distance)])
                # print(f'new record, distance={shortest_distance}')

            # Set terminal condition
            if converge_times > 2000:
                # print("Algorithm Converged, Break")
                break
            if time.time() - self.start_time > cutoff:
                # print("Time runoff, Break")
                break

        best_path = population[0]['path']

        return self.trace, best_path, int(shortest_distance)

