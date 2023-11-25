from __future__ import annotations

from constants import *
from nodes import NodeGroup


class MazeBase(object):
    def __init__(self):
        self.name: str
        self.portal_pairs: dict[int, tuple[tuple[int, int], tuple[int, int]]] = {}
        self.home_offset = (0, 0)
        self.ghost_node_deny: dict[int, tuple[tuple[int, int], ...]] = {UP: (), DOWN: (), LEFT: (), RIGHT: ()}
        self.home_node_connect_left: tuple[int, int]
        self.home_node_connect_right: tuple[int, int]
        self.pacman_start: tuple[int, int]
        self.fruit_start: tuple[int, int]

    def set_portal_pairs(self, nodes: NodeGroup):
        for pair in list(self.portal_pairs.values()):
            nodes.set_portal_pair(*pair)

    def connect_home_nodes(self, nodes: NodeGroup):
        key = nodes.create_home_nodes(*self.home_offset)
        nodes.connect_home_nodes(key, self.home_node_connect_left, LEFT)
        nodes.connect_home_nodes(key, self.home_node_connect_right, RIGHT)

    def add_offset(self, x: int, y: int):
        return x + self.home_offset[0], y + self.home_offset[1]

    def deny_ghost_access(self, ghosts, nodes: NodeGroup):
        nodes.deny_access_list(*(self.add_offset(2, 3) + (LEFT, ghosts)))
        nodes.deny_access_list(*(self.add_offset(2, 3) + (RIGHT, ghosts)))

        for direction in list(self.ghost_node_deny.keys()):
            for values in self.ghost_node_deny[direction]:
                nodes.deny_access_list(*(values + (direction, ghosts)))


class Maze1(MazeBase):
    def __init__(self):
        super().__init__()
        self.name = "maze1"
        self.portal_pairs = {0: ((0, 17), (27, 17))}
        self.home_offset = (11.5, 14)
        self.home_node_connect_left = (12, 14)
        self.home_node_connect_right = (15, 14)
        self.pacman_start = (15, 26)
        self.fruit_start = (9, 20)
        self.ghost_node_deny = {
            UP: ((12, 14), (15, 14), (12, 26), (15, 26)),
            LEFT: (self.add_offset(2, 3),),
            RIGHT: (self.add_offset(2, 3),),
        }


class Maze2(MazeBase):
    def __init__(self):
        super().__init__()
        self.name = "maze2"
        self.portal_pairs = {0: ((0, 4), (27, 4)), 1: ((0, 26), (27, 26))}
        self.home_offset = (11.5, 14)
        self.home_node_connect_left = (9, 14)
        self.home_node_connect_right = (18, 14)
        self.pacman_start = (16, 26)
        self.fruit_start = (11, 20)
        self.ghost_node_deny = {
            UP: ((9, 14), (18, 14), (11, 23), (16, 23)),
            LEFT: (self.add_offset(2, 3),),
            RIGHT: (self.add_offset(2, 3),),
        }


class MazeData(object):
    def __init__(self):
        self.obj: MazeBase
        self.maze_dict: dict[int, MazeBase.__base__] = {0: Maze1, 1: Maze2}
        self.maze_path = "mazes/"

    def load_maze(self, level: int):
        self.obj = self.maze_dict[level % len(self.maze_dict)]()
