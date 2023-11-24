from __future__ import annotations

import numpy as np
import pygame

from constants import *
from vector import Vector2


class Node(object):
    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.neighbors: dict[int, Node] = {
            UP: None, DOWN: None, LEFT: None, RIGHT: None, PORTAL: None}
        self.access = {
            UP: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
            DOWN: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
            LEFT: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
            RIGHT: [PACMAN, BLINKY, PINKY, INKY, CLYDE, FRUIT],
        }

    def deny_access(self, direction, entity):
        if entity.name in self.access[direction]:
            self.access[direction].remove(entity.name)

    def allow_access(self, direction, entity):
        if entity.name not in self.access[direction]:
            self.access[direction].append(entity.name)

    def render(self, screen):
        for node in self.neighbors.values():
            if node is not None:
                line_start = self.position.as_tuple()
                line_end = node.position.as_tuple()
                pygame.draw.line(screen, WHITE, line_start, line_end, 4)
                pygame.draw.circle(screen, RED, self.position.as_int(), 12)


class NodeGroup(object):
    def __init__(self, level):
        self.level = level
        self.nodes_lookup_table: dict[tuple[int, int], Node] = {}
        self.node_symbols = ["+", "P", "n"]
        self.path_symbols = [".", "-", "|", "p"]
        data = self.read_maze_file(level)
        self.create_node_table(data)
        self.connect_horizontally(data)
        self.connect_vertically(data)
        self.home_key: tuple[int, int]

    def read_maze_file(self, textfile):
        return np.loadtxt(textfile, dtype="<U1")

    def create_node_table(self, data, x_offset=0, y_offset=0):
        for row in list(range(data.shape[0])):
            for col in list(range(data.shape[1])):
                if data[row][col] in self.node_symbols:
                    x, y = self.construct_key(col + x_offset, row + y_offset)
                    self.nodes_lookup_table[(x, y)] = Node(x, y)

    def construct_key(self, x, y):
        return x * TILEWIDTH, y * TILEHEIGHT

    def connect_horizontally(self, data, x_offset=0, y_offset=0):
        for row in list(range(data.shape[0])):
            key = None
            for col in list(range(data.shape[1])):
                if data[row][col] in self.node_symbols:
                    if key is None:
                        key = self.construct_key(
                            col + x_offset, row + y_offset)
                    else:
                        other_key = self.construct_key(
                            col + x_offset, row + y_offset)
                        self.nodes_lookup_table[key].neighbors[RIGHT] = self.nodes_lookup_table[other_key]
                        self.nodes_lookup_table[other_key].neighbors[LEFT] = self.nodes_lookup_table[key]
                        key = other_key
                elif data[row][col] not in self.path_symbols:
                    key = None

    def connect_vertically(self, data, x_offset=0, y_offset=0):
        data_transposed = data.transpose()
        for col in list(range(data_transposed.shape[0])):
            key = None
            for row in list(range(data_transposed.shape[1])):
                if data_transposed[col][row] in self.node_symbols:
                    if key is None:
                        key = self.construct_key(
                            col + x_offset, row + y_offset)
                    else:
                        other_key = self.construct_key(
                            col + x_offset, row + y_offset)
                        self.nodes_lookup_table[key].neighbors[DOWN] = self.nodes_lookup_table[other_key]
                        self.nodes_lookup_table[other_key].neighbors[UP] = self.nodes_lookup_table[key]
                        key = other_key
                elif data_transposed[col][row] not in self.path_symbols:
                    key = None

    def get_start_temp_node(self):
        nodes = list(self.nodes_lookup_table.values())
        return nodes[0]

    def set_portal_pair(self, pair1, pair2):
        key1 = self.construct_key(*pair1)
        key2 = self.construct_key(*pair2)
        if key1 in self.nodes_lookup_table.keys() and key2 in self.nodes_lookup_table.keys():
            self.nodes_lookup_table[key1].neighbors[PORTAL] = self.nodes_lookup_table[key2]
            self.nodes_lookup_table[key2].neighbors[PORTAL] = self.nodes_lookup_table[key1]

    def create_home_nodes(self, x_offset, y_offset):
        home_data = np.array(
            [
                ["X", "X", "+", "X", "X"],
                ["X", "X", ".", "X", "X"],
                ["+", "X", ".", "X", "+"],
                ["+", ".", "+", ".", "+"],
                ["+", "X", "X", "X", "+"],
            ]
        )

        self.create_node_table(home_data, x_offset, y_offset)
        self.connect_horizontally(home_data, x_offset, y_offset)
        self.connect_vertically(home_data, x_offset, y_offset)
        self.home_key = self.construct_key(x_offset + 2, y_offset)
        return self.home_key

    def connect_home_nodes(self, home_key, other_key, direction):
        key = self.construct_key(*other_key)
        self.nodes_lookup_table[home_key].neighbors[direction] = self.nodes_lookup_table[key]
        self.nodes_lookup_table[key].neighbors[direction * -
                                               1] = self.nodes_lookup_table[home_key]

    def get_nodes_from_pixels(self, x_pixel, y_pixel):
        if (x_pixel, y_pixel) in self.nodes_lookup_table.keys():
            return self.nodes_lookup_table[(x_pixel, y_pixel)]
        return None

    def get_node_from_tiles(self, col, row) -> Node:
        x, y = self.construct_key(col, row)
        if (x, y) in self.nodes_lookup_table.keys():
            return self.nodes_lookup_table[(x, y)]
        return 

    def deny_access(self, col, row, direction, entity):
        node = self.get_node_from_tiles(col, row)
        if node is not None:
            node.deny_access(direction, entity)

    def allow_access(self, col, row, direction, entity):
        node = self.get_node_from_tiles(col, row)
        if node is not None:
            node.allow_access(direction, entity)

    def deny_access_list(self, col, row, direction, entities):
        for entity in entities:
            self.deny_access(col, row, direction, entity)

    def allow_access_list(self, col, row, direction, entities):
        for entity in entities:
            self.allow_access(col, row, direction, entity)

    def deny_home_access(self, entity):
        self.nodes_lookup_table[self.home_key].deny_access(DOWN, entity)

    def allow_home_access(self, entity):
        self.nodes_lookup_table[self.home_key].allow_access(DOWN, entity)

    def deny_home_access_list(self, entities):
        for entity in entities:
            self.deny_home_access(entity)

    def allow_home_access_list(self, entities):
        for entity in entities:
            self.allow_home_access(entity)

    def render(self, screen):
        for node in self.nodes_lookup_table.values():
            node.render(screen)
