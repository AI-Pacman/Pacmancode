from __future__ import annotations

from typing import Sequence

import pygame
from pygame.locals import K_DOWN, K_LEFT, K_RIGHT, K_UP

from constants import *
from entity import Entity
from pellets import Pellet, PowerPellet

# from run import ALGORITHMS
from search import *
from sprites import PacmanSprites
from vector import Vector2

ALGORITHMS = ["ALGORITHMS", "BFS", "DFS", "IDDFS", "GREEDY", "A*"]


class Pacman(Entity):
    def __init__(self, node):
        super().__init__(node)
        self.name = PACMAN
        self.color = YELLOW
        self.direction = LEFT
        self.set_between_nodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.set_between_nodes(LEFT)
        self.alive = True
        self.image = self.sprites.get_start_image()
        self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP

    def update(self, dt, pellets: Sequence[Pellet], current_algorithm: str):
        # add code
        # Use AI search to find the direction towards the nearest pellet
        pellet_positions = [pellet.node for pellet in pellets]
        # visited_array=set()
        # flag=0
        for pellet_node in pellet_positions:
            # if flag==0:
            #     stack = [(self.node,[])]

            if current_algorithm == ALGORITHMS[1]:
                path_to_pellet = breadth_first_search(self.node, pellet_node)
            elif current_algorithm == ALGORITHMS[2]:
                path_to_pellet = depth_first_search(self.node, pellet_node)
            elif current_algorithm == ALGORITHMS[3]:
                path_to_pellet = depth_first_search_iterative_deepening(self.node, pellet_node)
            elif current_algorithm == ALGORITHMS[4]:
                path_to_pellet = greedy_search(self.node, pellet_node)
            elif current_algorithm == ALGORITHMS[5]:
                path_to_pellet = a_star_search(self.node, pellet_node)
            else:
                path_to_pellet = breadth_first_search(self.node, pellet_node)
                # raise ValueError(f"Invalid algorithm: {current_algorithm}")

            if path_to_pellet is not None:
                self.path = path_to_pellet
                # print(f"Path to pellet {pellet_node}: {path_to_pellet}")
                # Now you can use path_to_pellet to update the direction and target
                if path_to_pellet:
                    next_direction = path_to_pellet[0]
                    self.direction = next_direction
                    self.target = self.get_new_target(next_direction)
                    # self.direction = STOP

            else:
                print(f"Pellet {pellet_node} is unreachable.")
        # end add code

        self.sprites.update(dt)
        self.position += self.directions[self.direction] * self.speed * dt
        direction = self.get_valid_key()
        if self.overshot_target():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.get_new_target(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.get_new_target(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.set_position()
        else:
            if self.opposite_direction(direction):
                self.reverse_direction()

    def get_valid_key(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP

    def eat_pellets(self, pellet_list):
        for pellet in pellet_list:
            if self.collide_check(pellet):
                return pellet
        return None

    def collide_ghost(self, ghost):
        return self.collide_check(ghost)

    def collide_check(self, other: Entity):
        d = self.position - other.position
        d_squared = d.magnitude_squared()
        r_squared = (self.collide_radius + other.collide_radius) ** 2
        if d_squared <= r_squared:
            return True
        return False
