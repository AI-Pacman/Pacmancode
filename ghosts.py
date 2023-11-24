from constants import *
from entity import Entity
from modes import ModeController
from pacman import Pacman
from sprites import GhostSprites
from vector import Vector2
from nodes import Node


class Ghost(Entity):
    def __init__(self, node, pacman, blinky):
        Entity.__init__(self, node)
        self.name = GHOST
        self.points = 200
        self.goal = Vector2()
        self.direction_method = self.goal_direction
        self.pacman: Pacman = pacman
        self.mode = ModeController(self)
        self.blinky: Ghost = blinky
        self.home_node: Node = node

    def reset(self):
        Entity.reset(self)
        self.points = 200
        self.direction_method = self.goal_direction

    def update(self, dt):
        self.sprites.update(dt)  # type: ignore
        self.mode.update(dt)
        if self.mode.current is SCATTER:
            self.scatter()
        elif self.mode.current is CHASE:
            self.chase()
        Entity.update(self, dt)

    def scatter(self):
        self.goal = Vector2()

    def chase(self):
        self.goal = self.pacman.position

    def spawn(self):
        self.goal = self.spawn_node.position

    def set_spawn_node(self, node):
        self.spawn_node = node

    def start_spawn(self):
        self.mode.set_spawn_mode()
        if self.mode.current == SPAWN:
            self.set_speed(150)
            self.direction_method = self.goal_direction
            self.spawn()

    def start_freight(self):
        self.mode.set_freight_mode()
        if self.mode.current == FREIGHT:
            self.set_speed(50)
            self.direction_method = self.random_direction

    def normal_mode(self):
        self.set_speed(100)
        self.direction_method = self.goal_direction
        self.home_node.deny_access(DOWN, self)


class Blinky(Ghost):
    def __init__(self, node, pacman, blinky):
        Ghost.__init__(self, node, pacman, blinky)
        self.name = BLINKY
        self.color = RED
        self.sprites = GhostSprites(self)


class Pinky(Ghost):
    def __init__(self, node, pacman, blinky):
        Ghost.__init__(self, node, pacman, blinky)
        self.name = PINKY
        self.color = PINK
        self.sprites = GhostSprites(self)

    def scatter(self):
        self.goal = Vector2(TILEWIDTH * NCOLS, 0)

    def chase(self):
        self.goal = (
            self.pacman.position
            + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 4
        )


class Inky(Ghost):
    def __init__(self, node, pacman, blinky):
        Ghost.__init__(self, node, pacman, blinky)
        self.name = INKY
        self.color = TEAL
        self.sprites = GhostSprites(self)
        self.blinky = blinky

    def scatter(self):
        self.goal = Vector2(TILEWIDTH * NCOLS, TILEHEIGHT * NROWS)

    def chase(self):
        vec1 = (
            self.pacman.position
            + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 2
        )
        vec2 = (vec1 - self.blinky.position) * 2
        self.goal = self.blinky.position + vec2


class Clyde(Ghost):
    def __init__(self, node, pacman, blinky):
        Ghost.__init__(self, node, pacman, blinky)
        self.name = CLYDE
        self.color = ORANGE
        self.sprites = GhostSprites(self)

    def scatter(self):
        self.goal = Vector2(0, TILEHEIGHT * NROWS)

    def chase(self):
        d = self.pacman.position - self.position
        ds = d.magnitude_squared()
        if ds <= (TILEWIDTH * 8) ** 2:
            self.scatter()
        else:
            self.goal = (
                self.pacman.position
                + self.pacman.directions[self.pacman.direction] * TILEWIDTH * 4
            )


class GhostGroup(object):
    def __init__(self, node, pacman):
        self.blinky = Blinky(node, pacman, None)
        self.pinky = Pinky(node, pacman, None)
        self.inky = Inky(node, pacman, self.blinky)
        self.clyde = Clyde(node, pacman, None)
        self.ghosts:list[Ghost] = [self.blinky, self.pinky, self.inky, self.clyde]

    def __iter__(self):
        return iter(self.ghosts)

    def update(self, dt):
        for ghost in self:
            ghost.update(dt)

    def start_freight(self):
        for ghost in self:
            ghost.start_freight()
        self.reset_points()

    def set_spawn_node(self, node):
        for ghost in self:
            ghost.set_spawn_node(node)

    def update_points(self):
        for ghost in self:
            ghost.points *= 2

    def reset_points(self):
        for ghost in self:
            ghost.points = 200

    def hide(self):
        for ghost in self:
            ghost.visible = False

    def show(self):
        for ghost in self:
            ghost.visible = True

    def reset(self):
        for ghost in self:
            ghost.reset()

    def render(self, screen):
        for ghost in self:
            ghost.render(screen)
