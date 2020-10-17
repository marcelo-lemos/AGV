import argparse
from dataclasses import dataclass
from enum import Enum
import sys

from graph import Graph, Node


@dataclass
class Point:
    x: int
    y: int

    def __add__(self, other):
        new_x = self.x + other.x
        new_y = self.y + other.y
        return Point(new_x, new_y)


DIRECTIONS = {
    'north': Point(0, 1),
    'south': Point(0, -1),
    'east': Point(1, 0),
    'west': Point(-1, 0)
}


def point_is_valid(grid, point):
    rows = len(grid)
    cols = len(grid[0])
    if point.x < 0 or point.x > rows - 1:
        return False
    if point.y < 0 or point.y > cols - 1:
        return False
    return True


def get_adjacents(grid, point):
    adjacents = []
    for direction in DIRECTIONS.values():
        adj = point + direction
        if point_is_valid(grid, adj) and grid[adj.x][adj.y] != '*':
            adjacents.append(point + direction)
    return adjacents


def load_grid(filename):
    with open(filename) as f:
        content = f.read().splitlines()

    meta = content.pop(0).split()
    map_ = content

    return meta, map_


def get_points_of_interest(grid):
    entry_points = []
    checkpoints = []
    goal = None
    for x, row in enumerate(grid):
        for y, cell in enumerate(row):
            if cell != '*':
                if x == 0 or y == 0 or x == (len(grid)-1) or y == (len(grid[0])-1):
                    entry_points.append(Point(x, y))
            if cell == '#':
                checkpoints.append(Point(x, y))
            if cell == '$':
                goal = Point(x, y)
    return entry_points, checkpoints, goal


def manhattan_distance(start, goal):
    dx = abs(goal.x - start.x)
    dy = abs(goal.y - start.y)
    return dx + dy


def generate_edges(grid, start, max_checkpoint_dist, graph, poi):
    open_list = [(start, 0, 0)]
    closed_list = []

    start_node = graph.get_node(start)

    while open_list:
        point, distance, checkpoints = open_list.pop(0)
        if distance > max_checkpoint_dist + 1:
            break
        closed_list.append(point)

        if distance != max_checkpoint_dist +1:
            if point != start and point in poi:
                node = graph.get_node(point)
                graph.add_edge(start_node, node, distance, checkpoints)
        else:
            if grid[point.x][point.y] == '#':
                node = graph.get_node(point)
                graph.add_edge(start_node, node, distance, checkpoints)

        if point != start and grid[point.x][point.y] == '#':
            checkpoints += 1

        for adj in get_adjacents(grid, point):
            if adj not in closed_list:
                open_list.append((adj, distance+1, checkpoints))


def generate_manhattan_distance(graph, goal, poi):
    goal_node = graph.get_node(goal)
    for point in poi:
        distance = manhattan_distance(point, goal)
        node = graph.get_node(point)
        graph.add_manhattan_distance(node, goal_node, distance)


def generate_graph(grid, checkpoint_distance):
    g = Graph()
    start_node = Node(Point(-1,-1), '.')
    g.add_node(start_node)

    entry_points, checkpoints, goal = get_points_of_interest(grid)

    goal_node = Node(goal, '$')
    g.add_node(goal_node)

    for point in entry_points:
        node = Node(point, grid[point.x][point.y])
        g.add_node(node)
        g.add_edge(start_node, node, 1, 0)

    for point in checkpoints:
        if point not in entry_points:
            node = Node(point, grid[point.x][point.y])
            g.add_node(node)

    # List of entry points and checkpoints
    entry_checkpoints = entry_points[:]
    for point in checkpoints:
        if point not in entry_checkpoints:
            entry_checkpoints.append(point)

    # All points of interest
    poi = entry_checkpoints[:]
    poi.append(goal)

    for point in entry_checkpoints:
        generate_edges(grid, point, int(checkpoint_distance), g, poi)
    
    g.add_manhattan_distance(start_node, goal_node, sys.maxsize)
    generate_manhattan_distance(g, goal, poi)

    return g, start_node, goal_node


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--algorithm', required=True)
    parser.add_argument('-i', '--input', required=True)
    cmd_args = parser.parse_args()

    meta, grid = load_grid(cmd_args.input)
    height, width, checkpoint_distance = meta

    graph, start, goal = generate_graph(grid, checkpoint_distance)
    
    if cmd_args.algorithm == 'bfs':
        path, dist = graph.bfs(start)
        checkpoints = graph.count_checkpoints(path)
        entry_point = path[1].key
        print(f'{dist} {checkpoints} [{entry_point.x} , {entry_point.y}]')
    elif cmd_args.algorithm == 'dfs':
        path, dist = graph.dfs(start)
        checkpoints = graph.count_checkpoints(path)
        entry_point = path[1].key
        print(f'{dist} {checkpoints} [{entry_point.x} , {entry_point.y}]')
    elif cmd_args.algorithm == 'ids':
        path, dist = graph.ids(start)
        checkpoints = graph.count_checkpoints(path)
        entry_point = path[1].key
        print(f'{dist} {checkpoints} [{entry_point.x} , {entry_point.y}]')
    elif cmd_args.algorithm == 'a_star':
        path, dist = graph.a_star(start, goal)
        checkpoints = graph.count_checkpoints(path)
        entry_point = path[1].key
        print(f'{dist} {checkpoints} [{entry_point.x} , {entry_point.y}]')
    else:
        print(f'Unknown algorithm: {cmd_args.algorithm}')