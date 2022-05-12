import numpy as np
import random
import time
import math

class SimulatedAnealing:
    def __init__(self, dat, seed=0, tempMax = 100, tempMin = 1, iterMax =60000, cooling = 'linear'):
        self.tempMax = tempMax
        self.tempMin = tempMin
        self.iterMax =iterMax
        self.cooling = cooling
        self.state = [[s[1],s[2],s[0]] for s in dat['XY']]
        
        n = len(self.state)
        self.dismat = np.zeros((n+1,n+1))
        for i in range(n):
            for j in range(n):
                self.dismat[self.state[i][-1],self.state[j][-1]] = self.getDistance_naive(self.state[i],self.state[j])
        self.state = self.greedy_initial(self.state)
        self.state = np.asarray(self.state)
        
        if seed is None:
            self.seed = seed
        else:
            self.seed = seed
        np.random.seed(self.seed)
        random.seed(self.seed)
    
    def MST(self,x):
        #find a mst
        n = len(x)
        visited = [(x[0][0],x[0][1])]
        best_predcessor = [0]
        unvisited = [(x[i][0],x[i][1]) for i in range(1,len(x))]
        while len(visited)!=len(x):
            best_ind = None
            best_distance = 1e9
            best_parent = None
            for i in range(len(visited)):
                for j in range(len(unvisited)):
                    try:
                        dis=math.log(self.getDistance(visited[i],unvisited[j])+1e-9)
                    except Exception:
                        print(i,j)
                        print(visited)
                        print(unvisited)
                        print(x)
                        print(len(x),len(visited),len(unvisited))
                        print(visited[i],unvisited[j])
                        print(self.getDistance(visited[i],unvisited[j]))
                        exit()
                    if dis<=best_distance:
                        best_distance = dis
                        best_ind = j
                        best_parent = i
            visited.append(unvisited.pop(best_ind))
            best_predcessor.append(best_parent)
        path = [visited[0]]
        while len(path)<n:
            state = 0
            for i in range(1,n):
                if visited[best_predcessor[i]]==path[-1] and visited[i] not in path:
                    path.append(visited[i])
                    state = 1
                elif visited[best_predcessor[i]]==path[0] and visited[i] not in path:
                    path.insert(0,visited[i])
                    state = 1
            if state==0:
                min_dis = 1e9
                next_to_append = None
                dis = 0
                for i in range(1,n):
                    if visited[i] not in path:
                        try:
                            dis = math.log(min(self.getDistance(visited[i],path[0]),self.getDistance(visited[i],path[-1]))+1e-4)
                            if dis==0:
                                print("dis is 0",dis)
                        except Exception:
                            print(i)
                            print(visited)
                            print(path)
                            print(visited[i],path[0])
                            print(visited[i],path[-1])
                            exit()
                        if dis<min_dis:
                            min_dis=dis
                            next_to_append = i 
                if dis==0:
                    print(next_to_append)
                    print(dis)
                    print(path)
                    print(visited)
                try:
                    if self.getDistance(visited[next_to_append],path[0])>=self.getDistance(visited[next_to_append],path[-1]):
                        path.insert(-1,visited[next_to_append])
                    else:
                        path.insert(0,visited[next_to_append])
                except Exception:
                    print(dis)
                    exit()
        return path
    
    
    def greedy_initial(self, x):
        path = [x[0]]
        n = len(x)
        unvisited = [x[i] for i in range(1,n)]
        while len(path)<n:
            best_next = None
            best_dis = 1e9
            for i in range(len(unvisited)):
                dis = min(self.getDistance(unvisited[i],path[0]),self.getDistance(unvisited[i],path[-1]))
                if dis<best_dis:
                    best_dis=dis
                    best_next = i 
            if self.getDistance(unvisited[best_next],path[0])<self.getDistance(unvisited[best_next],path[-1]):
                path.insert(0,unvisited[best_next])
                unvisited.pop(best_next)
            else:
                path.insert(-1,unvisited[best_next])
                unvisited.pop(best_next)
        return path
    
    
    def getDistance_naive(self, x1, x2):
        return np.sqrt((x1[0] - x2[0]) ** 2 + (x1[1] - x2[1]) ** 2)

    def getDistance(self, x1, x2):
        return self.dismat[int(x1[-1]),int(x2[-1])]
    
    #get distance of given tour
    def cost(self, tour): 
        cost = 0
        for i in range(len(tour)-1):
            cost += self.getDistance(tour[i],tour[i+1])
        cost += self.getDistance(tour[0],tour[-1])
          
        return cost
            
    #perform n-opt, default to 2 opt
    def nopt(self, currentState, t, tmax, method=2):
       #swap two neighbors along the path
        index = random.sample(range(len(currentState)), 2)
        xi = min(index)
        xj = max(index)
        if t<min(5,tmax//20):
            xj = min(xi+np.random.randint(5),len(currentState)-1)

        neighbor = currentState.copy()
        if xj<len(neighbor)-1:
            middle = neighbor[xi:xj+1].copy()
            neighbor[xi:xj+1] = middle[::-1]
            return neighbor
        else:
            middle = neighbor[xi:].copy()
            neighbor[xi:] = middle[::-1]
            return neighbor
        '''
        if method == 4:
            index = random.sample(range(len(currentState)), 4)
            xi,xj,xk,xm = index[0],index[1],index[2],index[3]
            neighbor = currentState.copy()
            temp = neighbor[xi].copy()
            neighbor[xi] = neighbor[xj]
            neighbor[xj] = neighbor[xk]
            neighbor[xk] = neighbor[xm]
            neighbor[xm] = temp
            return neighbor
        '''
    #Simulated Anealing
    def SA(self,current_tour,current_cost, cutoff=600):
        step =  1
        best_tour = current_tour
        best_cost = current_cost
        t=self.tempMax
        trace = []
        start_time = time.time()
        while step < self.iterMax and t >= self.tempMin:
            
            # get neighborhood by apply nopt
            current_neighbor = self.nopt(current_tour, t, self.tempMax)
            
            # neighbor cost
            neighbor_cost = self.cost(current_neighbor)
    
            # updata best cost
            if neighbor_cost < best_cost:
                best_tour = current_neighbor
                best_cost = neighbor_cost
                trace.append([round(time.time() - start_time, 2), int(best_cost)])
                if len(trace)>2 and trace[-1][0]-trace[-2][0]>1:
                    break
    
            # weather or not we should accept current neighbor
            if current_cost-neighbor_cost > np.log(np.random.random())*t:
                current_tour = current_neighbor
                current_cost = neighbor_cost
            
            if time.time()-start_time>cutoff:
                break
            
            #self.cooling
            if self.cooling == 'linear':
                t = self.tempMin + (self.tempMax - self.tempMin) * ((self.iterMax - step)/self.iterMax)
            elif self.cooling == 'quadratic additive':
                t= self.tempMin + (self.tempMax - self.tempMin) * ((self.tempMin - step)/self.tempMin)**2
            
            elif self.cooling == 'exponential':
                t=self.tempMax * 0.8**step
            else:
                t = self.tempMax / 0.1 * np.log(step + 1)
            step += 1
            
        return trace,best_tour,round(best_cost)
    
    def find_path(self, cutoff=600):
        initial_state = np.copy(self.state)
        current_cost = self.cost(initial_state)
        trace,best_state,best_cost = self.SA(initial_state,current_cost, cutoff=cutoff)
        best_state_ret = [int(i[2]) for i in best_state]
        return trace, best_state_ret,best_cost
