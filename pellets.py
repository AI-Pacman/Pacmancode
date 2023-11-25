import numpy as np
import pygame

from constants import *
from vector import Vector2


class Pellet(object):
    # def __init__(self, row: int, column: int, node=None):
    def __init__(self, row: int, column: int):
        self.name = PELLET
        self.position = Vector2(column * TILEWIDTH, row * TILEHEIGHT)
        self.color = WHITE
        self.radius = int(2 * TILEWIDTH / 16)
        self.collide_radius = 2 * TILEWIDTH / 16
        self.points = 10
        self.visible = True
        # self.node: Node | None = node

    def render(self, screen):
        if self.visible:
            adjust = Vector2(TILEWIDTH, TILEHEIGHT) / 2
            p = self.position + adjust
            pygame.draw.circle(screen, self.color, p.as_int(), self.radius)


class PowerPellet(Pellet):
    # def __init__(self, row: int, column: int, node=None):
    def __init__(self, row: int, column: int):
        # super().__init__(row, column, node)
        super().__init__(row, column)
        self.name = POWERPELLET
        self.radius = int(8 * TILEWIDTH / 16)
        self.points = 50
        self.flash_time = 0.2
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.flash_time:
            self.visible = not self.visible
            self.timer = 0


class PelletGroup(object):
    # def __init__(self, pellet_file, node_group: NodeGroup):
    def __init__(self, pellet_file):
        self.pellet_list: list[Pellet] = []
        self.power_pellets: list[PowerPellet] = []
        # self.create_pellet_list(pellet_file, node_group)
        self.create_pellet_list(pellet_file)
        self.num_eaten = 0

    def update(self, dt):
        for powerpellet in self.power_pellets:
            powerpellet.update(dt)

    # def create_pellet_list(self, pellet_file, node_group: NodeGroup):
    def create_pellet_list(self, pellet_file):
        data = self.read_pellet_file(pellet_file)
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                if data[row][col] in [".", "+"]:
                    # pellet = Pellet(row, col, None)
                    # pellet.node = node_group.get_node_from_tiles(col, row)
                    # self.pellet_list.append(pellet)
                    self.pellet_list.append(Pellet(row, col))
                elif data[row][col] in ["P", "p"]:
                    pp = PowerPellet(row, col)
                    # pp.node = node_group.get_node_from_tiles(col, row)
                    self.pellet_list.append(pp)
                    self.power_pellets.append(pp)

    def read_pellet_file(self, textfile):
        return np.loadtxt(textfile, dtype="<U1")

    def is_empty(self):
        if len(self.pellet_list) == 0:
            return True
        return False

    def render(self, screen):
        for pellet in self.pellet_list:
            pellet.render(screen)
