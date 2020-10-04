from heap import Heap


class Node:
    __slots__ = ['key', 'value', 'visited']

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.visited = False

    def __repr__(self):
        return f'Node {self.key}'


class Graph:
    __slots__ = ['nodes', 'edges', 'checkpoints', 'manhattan']

    def __init__(self):
        self.nodes = []
        self.edges = {}
        self.checkpoints = {}
        self.manhattan = {}

    def add_node(self, node):
        self.nodes.append(node)

    def get_node(self, key):
        for node in self.nodes:
            if node.key == key:
                return node
        raise Exception()

    def add_edge(self, source, destination, weight, checkpoints):
        if source not in self.nodes or destination not in self.nodes:
            raise Exception()

        if source not in self.edges:
            self.edges[source] = {}
            self.checkpoints[source] = {}
        if destination not in self.edges:
            self.edges[destination] = {}
            self.checkpoints[destination] = {}

        self.edges[source][destination] = weight
        self.edges[destination][source] = weight

        self.checkpoints[source][destination] = checkpoints
        self.checkpoints[destination][source] = checkpoints

    def add_manhattan_distance(self, source, destination, distance):
        if source not in self.nodes or destination not in self.nodes:
            raise Exception()

        if source not in self.manhattan:
            self.manhattan[source] = {}
        if destination not in self.manhattan:
            self.manhattan[destination] = {}

        self.manhattan[source][destination] = distance
        self.manhattan[destination][source] = distance

    def get_adjacents(self, node):
        if node not in self.nodes:
            raise Exception()

        return self.edges[node].keys()

    def get_weight(self, source, destination):
        if source not in self.edges:
            raise Exception()

        if destination not in self.edges[source]:
            raise Exception()

        return self.edges[source][destination]

    def get_checkpoints(self, source, destination):
        if source not in self.edges:
            raise Exception()

        if destination not in self.edges[source]:
            raise Exception()

        return self.checkpoints[source][destination]

    def get_manhattan_distance(self, source, destination):
        if source not in self.manhattan:
            raise Exception()

        if destination not in self.manhattan[source]:
            raise Exception()

        return self.manhattan[source][destination]

    def bfs(self, start):
        open_list = [(start, [], 0)]
        closed_list = []
        shortest_path = None
        shortest_distance = None

        while open_list:
            node, path, distance = open_list.pop(0)
            path.append(node)
            closed_list.append(node)

            if node.value == '$':
                if shortest_distance is None or distance < shortest_distance:
                    shortest_distance = distance
                    shortest_path = path

            for adj in self.get_adjacents(node):
                if adj not in closed_list:
                    open_list.append(
                        (adj, path[:], distance+self.get_weight(node, adj)))

        return shortest_path, shortest_distance


    def dfs(self, start):
        open_list = [(start, [], 0)]
        closed_list = []
        shortest_path = None
        shortest_distance = None

        while open_list:
            node, path, distance = open_list.pop()
            path.append(node)
            closed_list.append(node)

            if node.value == '$':
                if shortest_distance is None or distance < shortest_distance:
                    shortest_distance = distance
                    shortest_path = path

            for adj in self.get_adjacents(node):
                if adj not in path:
                    open_list.append(
                        (adj, path[:], distance+self.get_weight(node, adj)))

        return shortest_path, shortest_distance


    def dls(self, start, max_depth):
        open_list = [(start, [], 0)]
        closed_list = []
        shortest_path = None
        shortest_distance = None

        while open_list:
            node, path, distance = open_list.pop()
            if distance > max_depth:
                continue
            path.append(node)
            closed_list.append(node)

            if node.value == '$':
                return path, distance

            for adj in self.get_adjacents(node):
                if adj not in path:
                    open_list.append(
                        (adj, path[:], distance+self.get_weight(node, adj)))

        return None


    def ids(self, start):
        for depth in range(1, 1000000):
            result = self.dls(start, depth)
            if result is not None:
                return result

        return None

    def a_star(self, start, goal):
        open_list = Heap()
        open_list.push((start, (), 0), 0)
        closed_list = []

        while True:
            entry = open_list.pop()
            if entry is None:
                break
            node, path, distance = entry
            path = (*path, node)
            closed_list.append(node)
            
            if node.value == '$':
                return path, distance

            for adj in self.get_adjacents(node):
                if adj not in closed_list:
                    adj_dist = distance+self.get_weight(node, adj)
                    heuristic = adj_dist+self.get_manhattan_distance(adj, goal)
                    open_list.push((adj, path, adj_dist), heuristic)

        return None


    def count_checkpoints(self, path):
        checkpoints = 0
        for i, node in enumerate(path):
            if node.value == '#':
                checkpoints += 1
            if i < len(path)-1:
                checkpoints += self.get_checkpoints(node, path[i+1])
        return checkpoints
