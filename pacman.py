import pygame
from pygame.locals import *

from constants import *
from entity import Entity
from sprites import PacmanSprites
from vector import Vector2
from AIpacmanSearch import *

class Pacman(Entity):
    def __init__(self, node):
        Entity.__init__(self, node)
        self.name = PACMAN
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        # add code 
        self.path = []  # Add this line to store the path

        # end add code
    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP

    def update(self, dt, pellets,current_algorithm):
        # add code 
        # Use AI search to find the direction towards the nearest pellet
        pellet_positions = [pellet.node for pellet in pellets]
        # visited_array=set()
        # flag=0
        for pellet_node in pellet_positions:
                # if flag==0:
                #     stack = [(self.node,[])]
                if current_algorithm == "DFS":
                    path_to_pellet = depth_first_search(self.node, pellet_node)
                elif current_algorithm == "DFS_D":
                    path_to_pellet = depth_first_search_D(self.node, pellet_node)
                elif current_algorithm == "BFS":
                    path_to_pellet= breadth_first_search(self.node, pellet_node)
                elif current_algorithm == "Greedy":
                    path_to_pellet = greedy_search(self.node, pellet_node)
                elif current_algorithm == "A_STAR":
                    path_to_pellet = A_star_search(self.node,pellet_node)
                else:
                    path_to_pellet = depth_first_search(self.node, pellet_node)
                    # raise ValueError(f"Invalid algorithm: {current_algorithm}")
                
                if path_to_pellet is not None:
                    self.path = path_to_pellet
                    # print(f"Path to pellet {pellet_node}: {path_to_pellet}")
                    # Now you can use path_to_pellet to update the direction and target
                    if path_to_pellet:
                        next_direction = path_to_pellet[0]
                        self.direction = next_direction
                        self.target = self.getNewTarget(next_direction)
                        # self.direction = STOP
                        
                else:
                    print(f"Pellet {pellet_node} is unreachable.")
        # end add code
        
        self.sprites.update(dt)
        self.position += self.directions[self.direction] * self.speed * dt
        direction = self.getValidKey()
        if self.overshotTarget():
            self.node = self.target
            if self.node.neighbors[PORTAL] is not None:
                self.node = self.node.neighbors[PORTAL]
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else:
            if self.oppositeDirection(direction):
                self.reverseDirection()

    def getValidKey(self):
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

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None

    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius) ** 2
        if dSquared <= rSquared:
            return True
        return False
