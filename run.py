import pygame
from pygame.locals import *

from constants import *
from fruit import Fruit
from ghosts import GhostGroup
from mazedata import MazeData
from nodes import NodeGroup
from pacman import Pacman
from pauser import Pause
from pellets import PelletGroup
from sprites import LifeSprites, MazeSprites
from text import TextGroup


class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.background_norm = None
        self.background_flash = None
        self.clock = pygame.time.Clock()
        self.fruit = None
        self.pause = Pause(True)
        self.level = 0
        self.lives = 5
        self.score = 0
        self.textgroup = TextGroup()
        self.lifesprites = LifeSprites(self.lives)
        self.flashBG = False
        self.flashTime = 0.2
        self.flashTimer = 0
        self.fruitCaptured = []
        self.fruitNode = None
        self.mazedata = MazeData()
        self.current_algorithm = "Alogorithms"  
        self.haveghosts = False
       

    def setBackground(self):
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)
        self.background_norm = self.mazesprites.constructBackground(
            self.background_norm, self.level % 5
        )
        self.background_flash = self.mazesprites.constructBackground(
            self.background_flash, 5
        )
        self.flashBG = False
        self.background = self.background_norm

    def startGame(self):
        self.mazedata.loadMaze(self.level)
        self.mazesprites = MazeSprites(
            self.mazedata.path + self.mazedata.obj.name + ".txt",
            self.mazedata.path + self.mazedata.obj.name + "_rotation.txt",
        )
        self.setBackground()
        self.nodes = NodeGroup(self.mazedata.path + self.mazedata.obj.name + ".txt")
        self.mazedata.obj.setPortalPairs(self.nodes)
        self.mazedata.obj.connectHomeNodes(self.nodes)
        self.pacman = Pacman(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.pacmanStart)
        )
        self.pellets = PelletGroup(self.mazedata.path + self.mazedata.obj.name + ".txt", self.nodes)
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)

        self.ghosts.pinky.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3))
         )
        self.ghosts.inky.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(0, 3))
        )
        self.ghosts.clyde.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(4, 3))
        )
        self.ghosts.setSpawnNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3))
        )
        self.ghosts.blinky.setStartNode(
            self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 0))
        )

        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.mazedata.obj.denyGhostsAccess(self.ghosts, self.nodes)

    def update(self):
        dt = self.clock.tick(30) / 1000.0
        self.textgroup.update(dt)
        self.pellets.update(dt)
        if not self.pause.paused:
            if self.haveghosts:
                self.ghosts.update(dt)
            if self.fruit is not None:
                self.fruit.update(dt)
            self.checkPelletEvents()
            self.checkGhostEvents()
            self.checkFruitEvents()

        if self.pacman.alive:
            if not self.pause.paused:
                self.pacman.update(dt,self.pellets.pelletList, self.current_algorithm) # add pellet code 
        else:
            self.pacman.update(dt,self.pellets.powerpellets, self.current_algorithm)  # add pellet code

        if self.flashBG:
            self.flashTimer += dt
            if self.flashTimer >= self.flashTime:
                self.flashTimer = 0
                if self.background == self.background_norm:
                    self.background = self.background_flash
                else:
                    self.background = self.background_norm

        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()
        self.checkEvents()
        self.render()
        # Check for button clicks
        mouse_pos = pygame.mouse.get_pos()
        start_button, exit_button, algorithm_button, ghost_button = self.create_buttons()
        if pygame.mouse.get_pressed()[0]:
            self.handle_button_click(mouse_pos, start_button, exit_button, algorithm_button, ghost_button)

        
        
    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if self.pacman.alive:
                        self.pause.setPause(playerPaused=True)
                        if not self.pause.paused:
                            self.textgroup.hideText()
                            self.showEntities()
                        else:
                            self.textgroup.showText(PAUSETXT)
                            # self.hideEntities()

    def checkPelletEvents(self):
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            self.updateScore(pellet.points)
            if self.pellets.numEaten == 30:
                self.ghosts.inky.startNode.allowAccess(RIGHT, self.ghosts.inky)
            if self.pellets.numEaten == 70:
                self.ghosts.clyde.startNode.allowAccess(LEFT, self.ghosts.clyde)
            self.pellets.pelletList.remove(pellet)
            if pellet.name == POWERPELLET:
                self.ghosts.startFreight()
            if self.pellets.isEmpty():
                self.flashBG = True
                self.hideEntities()
                self.pause.setPause(pauseTime=3, func=self.nextLevel)

    def checkGhostEvents(self):
        for ghost in self.ghosts:
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.pacman.visible = False
                    ghost.visible = False
                    self.updateScore(ghost.points)
                    self.textgroup.addText(
                        str(ghost.points),
                        WHITE,
                        ghost.position.x,
                        ghost.position.y,
                        8,
                        time=1,
                    )
                    self.ghosts.updatePoints()
                    self.pause.setPause(pauseTime=1, func=self.showEntities)
                    ghost.startSpawn()
                    self.nodes.allowHomeAccess(ghost)
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        self.lives -= 1
                        self.lifesprites.removeImage()
                        self.pacman.die()
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.textgroup.showText(GAMEOVERTXT)
                            self.pause.setPause(pauseTime=3, func=self.restartGame)
                        else:
                            self.pause.setPause(pauseTime=3, func=self.resetLevel)

    def checkFruitEvents(self):
        if self.pellets.numEaten == 50 or self.pellets.numEaten == 140:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.getNodeFromTiles(9, 20), self.level)
                print(self.fruit)
        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                self.updateScore(self.fruit.points)
                self.textgroup.addText(
                    str(self.fruit.points),
                    WHITE,
                    self.fruit.position.x,
                    self.fruit.position.y,
                    8,
                    time=1,
                )
                fruitCaptured = False
                for fruit in self.fruitCaptured:
                    if fruit.get_offset() == self.fruit.image.get_offset():
                        fruitCaptured = True
                        break
                if not fruitCaptured:
                    self.fruitCaptured.append(self.fruit.image)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None

    def showEntities(self):
        self.pacman.visible = True
        self.ghosts.show()

    def hideEntities(self):
        self.pacman.visible = False
        self.ghosts.hide()

    def nextLevel(self):
        self.showEntities()
        self.level += 1
        self.pause.paused = True
        self.startGame()
        self.textgroup.updateLevel(self.level)

    def restartGame(self):
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.startGame()
        self.score = 0
        self.textgroup.updateScore(self.score)
        self.textgroup.updateLevel(self.level)
        self.textgroup.showText(READYTXT)
        self.lifesprites.resetLives(self.lives)
        self.fruitCaptured = []

    def resetLevel(self):
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.textgroup.showText(READYTXT)

    def updateScore(self, points):
        self.score += points
        self.textgroup.updateScore(self.score)
    # creat buttons
    def create_buttons(self):
        start_button_rect = pygame.Rect(SCREENWIDTH - 250, 200, 200, 50)
        exit_button_rect = pygame.Rect(SCREENWIDTH - 250, 270, 200, 50)
        
        
        start_button = pygame.draw.rect(self.screen, GREEN, start_button_rect)
        exit_button = pygame.draw.rect(self.screen, RED, exit_button_rect)

        font = pygame.font.Font(None, 36)
        start_text = font.render("Start Game", True, WHITE)
        exit_text = font.render("Exit", True, WHITE)

        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)

        algorithm_button_rect = pygame.Rect(SCREENWIDTH - 250, 340, 200, 50)
        algorithm_button = pygame.draw.rect(self.screen, BLUE, algorithm_button_rect)
        algorithm_text = font.render(self.current_algorithm, True, WHITE)
        algorithm_text_rect = algorithm_text.get_rect(center=algorithm_button_rect.center)
        
        ghost_button_rect = pygame.Rect(SCREENWIDTH - 250, 410, 200, 50)
        ghost_button = pygame.draw.rect(self.screen, BLUE, ghost_button_rect)
        ghost_text = font.render("Ghost", True, WHITE)
        ghost_text_rect = ghost_text.get_rect(center=ghost_button_rect.center)
        # Check the status of self.haveghost to determine the text behind the "Ghost" button
      
        ghost_status_text = font.render(str(self.haveghosts), True, WHITE)

        ghost_status_rect = ghost_status_text.get_rect(center=(ghost_button_rect.centerx, ghost_button_rect.centery + 30))
        
        self.screen.blit(algorithm_text, algorithm_text_rect)
        self.screen.blit(start_text, start_text_rect)
        self.screen.blit(exit_text, exit_text_rect)
        self.screen.blit(ghost_text, ghost_text_rect)
        self.screen.blit(ghost_status_text, ghost_status_rect)
        return start_button, exit_button, algorithm_button, ghost_button

    def handle_button_click(self, pos, start_button, exit_button, algorithm_button, ghost_button):
        if start_button.collidepoint(pos):
            self.handle_space_key()
        elif exit_button.collidepoint(pos):
            pygame.quit()
            exit()
        elif algorithm_button.collidepoint(pos):
            # Handle Algorithm button click
            self.change_algorithm()
        elif ghost_button.collidepoint(pos):
           if self.haveghosts:
               self.haveghosts = False 
           else:
               self.haveghosts = True
        
    def handle_space_key(self):
        # Xử lý sự kiện tương tự khi nhấn phím cách (Space)
        if self.pacman.alive:
            self.pause.setPause(playerPaused=True)
            if not self.pause.paused:
                self.textgroup.hideText()
                self.showEntities()
            else:
                self.textgroup.showText(PAUSETXT)
    
    def change_algorithm(self):
        if self.current_algorithm == "Alogorithms":
            self.current_algorithm = "DFS" 
        elif self.current_algorithm == "DFS":
            self.current_algorithm = "DFS_D"
        elif self.current_algorithm == "DFS_D":
            self.current_algorithm = "ID_DFS"
        elif self.current_algorithm == "ID_DFS":
            self.current_algorithm = "BFS"
        elif self.current_algorithm == "BFS":
            self.current_algorithm = "Greedy"
        elif self.current_algorithm == "Greedy":
            self.current_algorithm = "DFS"
        else:
            # Default to DFS if the current algorithm is not recognized
            self.current_algorithm = "DFS"
    

    # end code button            
    def render(self):
        self.screen.blit(self.background, (0, 0))
        # self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.textgroup.render(self.screen)

        for i in range(len(self.lifesprites.images)):
            x = self.lifesprites.images[i].get_width() * i
            y = SCREENHEIGHT - self.lifesprites.images[i].get_height()
            self.screen.blit(self.lifesprites.images[i], (x, y))

        for i in range(len(self.fruitCaptured)):
            x = SCREENWIDTH - self.fruitCaptured[i].get_width() * (i + 1)
            y = SCREENHEIGHT - self.fruitCaptured[i].get_height()
            self.screen.blit(self.fruitCaptured[i], (x, y))
        start_button, exit_button, algorithm_button, ghost_button  = self.create_buttons()
        pygame.display.update()


if __name__ == "__main__":
    game = GameController()
    game.startGame()
    while True:
        game.update()
