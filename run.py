import pygame
from pygame.locals import K_SPACE, KEYDOWN, QUIT

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
        self.background: pygame.Surface
        self.background_norm: pygame.Surface
        self.background_flash: pygame.Surface
        self.clock = pygame.time.Clock()
        self.fruit = None
        self.pause = Pause(True)
        self.level = 0
        self.lives = 5
        self.score = 0
        self.text_group = TextGroup()
        self.life_sprites = LifeSprites(self.lives)
        self.flash_background = False
        self.flash_time = 0.2
        self.flash_timer = 0
        self.fruit_captured = []
        self.fruit_node = None
        self.maze_data = MazeData()

    def set_background(self):
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)
        self.background_norm = self.maze_sprites.construct_background(
            self.background_norm, self.level % 5
        )
        self.background_flash = self.maze_sprites.construct_background(
            self.background_flash, 5
        )
        self.flash_background = False
        self.background = self.background_norm

    def start_game(self):
        self.maze_data.load_maze(self.level)
        self.maze_sprites = MazeSprites(
            self.maze_data.path + self.maze_data.obj.name + ".txt",
            self.maze_data.path + self.maze_data.obj.name + "_rotation.txt",
        )
        self.set_background()
        self.nodes = NodeGroup(self.maze_data.path +
                               self.maze_data.obj.name + ".txt")
        self.maze_data.obj.set_portal_pairs(self.nodes)
        self.maze_data.obj.connect_home_nodes(self.nodes)
        self.pacman = Pacman(
            self.nodes.get_node_from_tiles(*self.maze_data.obj.pacman_start)
        )
        self.pellets = PelletGroup(
            self.maze_data.path + self.maze_data.obj.name + ".txt")
        self.ghosts = GhostGroup(self.nodes.get_start_temp_node(), self.pacman)

        self.ghosts.pinky.set_start_node(
            self.nodes.get_node_from_tiles(
                *self.maze_data.obj.add_offset(2, 3))
        )
        self.ghosts.inky.set_start_node(
            self.nodes.get_node_from_tiles(
                *self.maze_data.obj.add_offset(0, 3))
        )
        self.ghosts.clyde.set_start_node(
            self.nodes.get_node_from_tiles(
                *self.maze_data.obj.add_offset(4, 3))
        )
        self.ghosts.set_spawn_node(
            self.nodes.get_node_from_tiles(
                *self.maze_data.obj.add_offset(2, 3))
        )
        self.ghosts.blinky.set_start_node(
            self.nodes.get_node_from_tiles(
                *self.maze_data.obj.add_offset(2, 0))
        )

        self.nodes.deny_home_access(self.pacman)
        self.nodes.deny_home_access_list(self.ghosts)
        self.ghosts.inky.start_node.deny_access(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.start_node.deny_access(LEFT, self.ghosts.clyde)
        self.maze_data.obj.deny_ghost_access(self.ghosts, self.nodes)

    def update(self):
        dt = self.clock.tick(30) / 1000.0
        self.text_group.update(dt)
        self.pellets.update(dt)
        if not self.pause.paused:
            self.ghosts.update(dt)
            if self.fruit is not None:
                self.fruit.update(dt)
            self.check_pellet_events()
            self.check_ghost_events()
            self.check_fruit_events()

        if self.pacman.alive:
            if not self.pause.paused:
                self.pacman.update(dt)
        else:
            self.pacman.update(dt)

        if self.flash_background:
            self.flash_timer += dt
            if self.flash_timer >= self.flash_time:
                self.flash_timer = 0
                if self.background == self.background_norm:
                    self.background = self.background_flash
                else:
                    self.background = self.background_norm

        after_pause_method = self.pause.update(dt)
        if after_pause_method is not None:
            after_pause_method()
        self.check_events()
        self.render()
        # Check for button clicks
        mouse_pos = pygame.mouse.get_pos()
        start_button, exit_button = self.create_buttons()
        if pygame.mouse.get_pressed()[0]:
            self.handle_button_click(mouse_pos, start_button, exit_button)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if self.pacman.alive:
                        self.pause.set_pause(player_paused=True)
                        if not self.pause.paused:
                            self.text_group.hide_text()
                            self.show_entities()
                        else:
                            self.text_group.show_text(PAUSETXT)
                            # self.hideEntities()

    def check_pellet_events(self):
        pellet = self.pacman.eat_pellets(self.pellets.pellet_list)
        if pellet:
            self.pellets.num_eaten += 1
            self.update_score(pellet.points)
            if self.pellets.num_eaten == 30:
                self.ghosts.inky.start_node.allow_access(
                    RIGHT, self.ghosts.inky)
            if self.pellets.num_eaten == 70:
                self.ghosts.clyde.start_node.allow_access(
                    LEFT, self.ghosts.clyde)
            self.pellets.pellet_list.remove(pellet)
            if pellet.name == POWERPELLET:
                self.ghosts.start_freight()
            if self.pellets.is_empty():
                self.flash_background = True
                self.hide_entities()
                self.pause.set_pause(pause_time=3, func=self.next_level)

    def check_ghost_events(self):
        for ghost in self.ghosts:
            if self.pacman.collide_ghost(ghost):
                if ghost.mode.current is FREIGHT:
                    self.pacman.visible = False
                    ghost.visible = False
                    self.update_score(ghost.points)
                    self.text_group.add_text(
                        str(ghost.points),
                        WHITE,
                        ghost.position.x,
                        ghost.position.y,
                        8,
                        time=1,
                    )
                    self.ghosts.update_points()
                    self.pause.set_pause(pause_time=1, func=self.show_entities)
                    ghost.start_spawn()
                    self.nodes.allow_home_access(ghost)
                elif ghost.mode.current is not SPAWN:
                    if self.pacman.alive:
                        self.lives -= 1
                        self.life_sprites.remove_image()
                        self.pacman.die()
                        self.ghosts.hide()
                        if self.lives <= 0:
                            self.text_group.show_text(GAMEOVERTXT)
                            self.pause.set_pause(
                                pause_time=3, func=self.restart_game)
                        else:
                            self.pause.set_pause(
                                pause_time=3, func=self.reset_level)

    def check_fruit_events(self):
        if self.pellets.num_eaten == 50 or self.pellets.num_eaten == 140:
            if self.fruit is None:
                self.fruit = Fruit(
                    self.nodes.get_node_from_tiles(9, 20), self.level)
                print(self.fruit)
        if self.fruit is not None:
            if self.pacman.collide_check(self.fruit):
                self.update_score(self.fruit.points)
                self.text_group.add_text(
                    str(self.fruit.points),
                    WHITE,
                    self.fruit.position.x,
                    self.fruit.position.y,
                    8,
                    time=1,
                )
                fruit_captured = False
                for fruit in self.fruit_captured:
                    if fruit.get_offset() == self.fruit.image.get_offset():
                        fruit_captured = True
                        break
                if not fruit_captured:
                    self.fruit_captured.append(self.fruit.image)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None

    def show_entities(self):
        self.pacman.visible = True
        self.ghosts.show()

    def hide_entities(self):
        self.pacman.visible = False
        self.ghosts.hide()

    def next_level(self):
        self.show_entities()
        self.level += 1
        self.pause.paused = True
        self.start_game()
        self.text_group.update_level(self.level)

    def restart_game(self):
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.start_game()
        self.score = 0
        self.text_group.update_score(self.score)
        self.text_group.update_level(self.level)
        self.text_group.show_text(READYTXT)
        self.life_sprites.reset_lives(self.lives)
        self.fruit_captured = []

    def reset_level(self):
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.text_group.show_text(READYTXT)

    def update_score(self, points):
        self.score += points
        self.text_group.update_score(self.score)

    # Menu buttons
    def create_buttons(self):
        start_button_rect = pygame.Rect(SCREENWIDTH - 250, 200, 200, 50)
        exit_button_rect = pygame.Rect(SCREENWIDTH - 250, 270, 200, 50)

        start_button = pygame.draw.rect(self.screen, GREEN, start_button_rect)
        exit_button = pygame.draw.rect(self.screen, RED, exit_button_rect)

        FONTFAMILY = "font/PressStart2P-Regular.ttf"
        font = pygame.font.Font(FONTFAMILY, 36)
        start_text = font.render("START", True, WHITE)
        exit_text = font.render("EXIT", True, WHITE)

        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)

        self.screen.blit(start_text, start_text_rect)
        self.screen.blit(exit_text, exit_text_rect)

        return start_button, exit_button

    def handle_button_click(self, pos, start_button, exit_button):
        if start_button.collidepoint(pos):
            self.handle_space_key()
        elif exit_button.collidepoint(pos):
            pygame.quit()
            exit()

    def handle_space_key(self):
        # Xử lý sự kiện tương tự khi nhấn phím cách (Space)
        if self.pacman.alive:
            self.pause.set_pause(player_paused=True)
            if not self.pause.paused:
                self.text_group.hide_text()
                self.show_entities()
            else:
                self.text_group.show_text(PAUSETXT)

    def render(self):
        self.screen.blit(self.background, (0, 0))
        # self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.text_group.render(self.screen)

        for i in range(len(self.life_sprites.images)):
            x = self.life_sprites.images[i].get_width() * i
            y = SCREENHEIGHT - self.life_sprites.images[i].get_height()
            self.screen.blit(self.life_sprites.images[i], (x, y))

        for i in range(len(self.fruit_captured)):
            x = SCREENWIDTH - self.fruit_captured[i].get_width() * (i + 1)
            y = SCREENHEIGHT - self.fruit_captured[i].get_height()
            self.screen.blit(self.fruit_captured[i], (x, y))
        start_button, exit_button = self.create_buttons()
        pygame.display.update()


if __name__ == "__main__":
    game = GameController()
    game.start_game()
    while True:
        game.update()
