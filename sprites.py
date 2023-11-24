import numpy as np
import pygame

from animation import Animator
from constants import *

BASE_TILEWIDTH = 16
BASE_TILEHEIGHT = 16
DEATH = 5

FILEPATH = "spritesheets/"
FILENAME = "spritesheet.png"


class Spritesheet(object):
    def __init__(self):
        self.sheet = pygame.image.load(FILEPATH + FILENAME).convert()
        transcolor = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(transcolor)
        width = int(self.sheet.get_width() / BASE_TILEWIDTH * TILEWIDTH)
        height = int(self.sheet.get_height() / BASE_TILEHEIGHT * TILEHEIGHT)
        self.sheet = pygame.transform.scale(self.sheet, (width, height))

    def get_image(self, x, y, width, height):
        x *= TILEWIDTH
        y *= TILEHEIGHT
        self.sheet.set_clip(pygame.Rect(x, y, width, height))
        return self.sheet.subsurface(self.sheet.get_clip())


class PacmanSprites(Spritesheet):
    def __init__(self, entity):
        Spritesheet.__init__(self)
        self.entity = entity
        self.entity.image = self.get_start_image()
        self.animations = {}
        self.define_animations()
        self.stop_image = (8, 0)

    def define_animations(self):
        self.animations[LEFT] = Animator(((8, 0), (0, 0), (0, 2), (0, 0)))
        self.animations[RIGHT] = Animator(((10, 0), (2, 0), (2, 2), (2, 0)))
        self.animations[UP] = Animator(((10, 2), (6, 0), (6, 2), (6, 0)))
        self.animations[DOWN] = Animator(((8, 2), (4, 0), (4, 2), (4, 0)))
        self.animations[DEATH] = Animator(
            (
                (0, 12),
                (2, 12),
                (4, 12),
                (6, 12),
                (8, 12),
                (10, 12),
                (12, 12),
                (14, 12),
                (16, 12),
                (18, 12),
                (20, 12),
            ),
            speed=6,
            loop=False,
        )

    def update(self, dt):
        if self.entity.alive == True:
            if self.entity.direction == LEFT:
                self.entity.image = self.get_image(
                    *self.animations[LEFT].update(dt))
                self.stop_image = (8, 0)
            elif self.entity.direction == RIGHT:
                self.entity.image = self.get_image(
                    *self.animations[RIGHT].update(dt))
                self.stop_image = (10, 0)
            elif self.entity.direction == DOWN:
                self.entity.image = self.get_image(
                    *self.animations[DOWN].update(dt))
                self.stop_image = (8, 2)
            elif self.entity.direction == UP:
                self.entity.image = self.get_image(
                    *self.animations[UP].update(dt))
                self.stop_image = (10, 2)
            elif self.entity.direction == STOP:
                self.entity.image = self.get_image(*self.stop_image)
        else:
            self.entity.image = self.get_image(
                *self.animations[DEATH].update(dt))

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()

    def get_start_image(self):
        return self.get_image(8, 0)

    def get_image(self, x, y):
        return Spritesheet.get_image(self, x, y, 2 * TILEWIDTH, 2 * TILEHEIGHT)


class GhostSprites(Spritesheet):
    def __init__(self, entity):
        Spritesheet.__init__(self)
        self.x = {BLINKY: 0, PINKY: 2, INKY: 4, CLYDE: 6}
        self.entity = entity
        self.entity.image = self.get_start_image()

    def update(self, dt):
        x = self.x[self.entity.name]
        if self.entity.mode.current in [SCATTER, CHASE]:
            if self.entity.direction == LEFT:
                self.entity.image = self.get_image(x, 8)
            elif self.entity.direction == RIGHT:
                self.entity.image = self.get_image(x, 10)
            elif self.entity.direction == DOWN:
                self.entity.image = self.get_image(x, 6)
            elif self.entity.direction == UP:
                self.entity.image = self.get_image(x, 4)
        elif self.entity.mode.current == FREIGHT:
            self.entity.image = self.get_image(10, 4)
        elif self.entity.mode.current == SPAWN:
            if self.entity.direction == LEFT:
                self.entity.image = self.get_image(8, 8)
            elif self.entity.direction == RIGHT:
                self.entity.image = self.get_image(8, 10)
            elif self.entity.direction == DOWN:
                self.entity.image = self.get_image(8, 6)
            elif self.entity.direction == UP:
                self.entity.image = self.get_image(8, 4)

    def get_start_image(self):
        return self.get_image(self.x[self.entity.name], 4)

    def get_image(self, x, y):
        return Spritesheet.get_image(self, x, y, 2 * TILEWIDTH, 2 * TILEHEIGHT)


class FruitSprites(Spritesheet):
    def __init__(self, entity, level):
        Spritesheet.__init__(self)
        self.entity = entity
        self.fruits = {
            0: (16, 8),
            1: (18, 8),
            2: (20, 8),
            3: (16, 10),
            4: (18, 10),
            5: (20, 10),
        }
        self.entity.image = self.get_start_image(level % len(self.fruits))

    def get_start_image(self, key):
        return self.get_image(*self.fruits[key])

    def get_image(self, x, y):
        return Spritesheet.get_image(self, x, y, 2 * TILEWIDTH, 2 * TILEHEIGHT)


class LifeSprites(Spritesheet):
    def __init__(self, num_lives):
        Spritesheet.__init__(self)
        self.reset_lives(num_lives)

    def remove_image(self):
        if len(self.images) > 0:
            self.images.pop(0)

    def reset_lives(self, num_lives):
        self.images = []
        for i in range(num_lives):
            self.images.append(self.get_image(0, 0))

    def get_image(self, x, y):
        return Spritesheet.get_image(self, x, y, 2 * TILEWIDTH, 2 * TILEHEIGHT)


class MazeSprites(Spritesheet):
    def __init__(self, mazefile, rotfile):
        Spritesheet.__init__(self)
        self.data = self.read_maze_file(mazefile)
        self.rot_data = self.read_maze_file(rotfile)

    def get_image(self, x, y):
        return Spritesheet.get_image(self, x, y, TILEWIDTH, TILEHEIGHT)

    def read_maze_file(self, maze_file):
        return np.loadtxt(maze_file, dtype="<U1")

    def construct_background(self, background, y):
        for row in list(range(self.data.shape[0])):
            for col in list(range(self.data.shape[1])):
                if self.data[row][col].isdigit():
                    x = int(self.data[row][col]) + 12
                    sprite = self.get_image(x, y)
                    rot_val = int(self.rot_data[row][col])
                    sprite = self.rotate(sprite, rot_val)
                    background.blit(
                        sprite, (col * TILEWIDTH, row * TILEHEIGHT))
                elif self.data[row][col] == "=":
                    sprite = self.get_image(10, 8)
                    background.blit(
                        sprite, (col * TILEWIDTH, row * TILEHEIGHT))
        return background

    def rotate(self, sprite, value):
        return pygame.transform.rotate(sprite, value * 90)
