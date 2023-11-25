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
        self.fruit: Fruit | None = None
        self.pause = Pause(True)
        self.level = 0
        self.lives = 5
        self.score = 0
        self.textgroup = TextGroup()
        self.life_sprites = LifeSprites(self.lives)
        self.flash_background = False
        self.flash_time = 0.2
        self.flash_timer = 0
        self.fruit_captured: list[pygame.Surface] = []
        self.mazedata = MazeData()
        # self.current_algorithm = ALGORITHMS[0]
        # self.have_ghosts = False

    def set_background(self):
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)
        self.background_norm = self.maze_sprites.construct_background(self.background_norm, self.level % 5)
        self.background_flash = self.maze_sprites.construct_background(self.background_flash, 5)
        self.flash_background = False
        self.background = self.background_norm

    def start_game(self):
        self.mazedata.load_maze(self.level)
        self.maze_sprites = MazeSprites(
            self.mazedata.maze_path + self.mazedata.obj.name + ".txt",
            self.mazedata.maze_path + self.mazedata.obj.name + "_rotation.txt",
        )
        self.set_background()

        self.nodes = NodeGroup(self.mazedata.maze_path + self.mazedata.obj.name + ".txt")
        self.mazedata.obj.set_portal_pairs(self.nodes)
        self.mazedata.obj.connect_home_nodes(self.nodes)

        self.pacman = Pacman(self.nodes.get_node_from_tiles(*self.mazedata.obj.pacman_start))
        # self.pellets = PelletGroup(self.mazedata.maze_path + self.mazedata.obj.name + ".txt", self.nodes)
        self.pellets = PelletGroup(self.mazedata.maze_path + self.mazedata.obj.name + ".txt")
        self.ghosts = GhostGroup(self.nodes.get_start_temp_node(), self.pacman)

        self.ghosts.pinky.set_start_node(self.nodes.get_node_from_tiles(*self.mazedata.obj.add_offset(2, 3)))
        self.ghosts.inky.set_start_node(self.nodes.get_node_from_tiles(*self.mazedata.obj.add_offset(0, 3)))
        self.ghosts.clyde.set_start_node(self.nodes.get_node_from_tiles(*self.mazedata.obj.add_offset(4, 3)))
        self.ghosts.set_spawn_mode(self.nodes.get_node_from_tiles(*self.mazedata.obj.add_offset(2, 3)))
        self.ghosts.blinky.set_start_node(self.nodes.get_node_from_tiles(*self.mazedata.obj.add_offset(2, 0)))

        self.nodes.deny_home_access(self.pacman)
        self.nodes.deny_home_access_list(self.ghosts)
        self.ghosts.inky.start_node.deny_access(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.start_node.deny_access(LEFT, self.ghosts.clyde)
        self.mazedata.obj.deny_ghost_access(self.ghosts, self.nodes)

    def update(self):
        dt = self.clock.tick(30) / 1000.0
        self.textgroup.update(dt)
        self.pellets.update(dt)
        if not self.pause.paused:
            self.ghosts.update(dt)
            # if self.have_ghosts:
            # self.ghosts.update(dt)
            if self.fruit is not None:
                self.fruit.update(dt)
            self.check_pellet_events()
            self.check_ghost_events()
            self.check_fruit_events()

        if self.pacman.alive:
            if not self.pause.paused:
                # self.pacman.update(dt, self.pellets.pellet_list, self.current_algorithm)
                self.pacman.update(dt)
        else:
            # self.pacman.update(dt, self.pellets.power_pellets, self.current_algorithm)
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

        # mouse_pos = pygame.mouse.get_pos()
        # start_button, exit_button, algorithm_button, ghost_button = self.create_buttons()
        # if pygame.mouse.get_pressed()[0]:
        #     self.handle_button_click(mouse_pos, start_button, exit_button, algorithm_button, ghost_button)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN and event.key == K_SPACE:
                if self.pacman.alive:
                    self.pause.set_pause(player_paused=True)
                    if not self.pause.paused:
                        self.textgroup.hide_text()
                        self.show_entities()
                    else:
                        self.textgroup.show_text(PAUSETXT)
                        # self.hideEntities()

    def check_pellet_events(self):
        pellet = self.pacman.eat_pellets(self.pellets.pellet_list)
        if pellet:
            self.pellets.num_eaten += 1
            self.update_score(pellet.points)
            if self.pellets.num_eaten == 30:
                self.ghosts.inky.start_node.allow_access(RIGHT, self.ghosts.inky)
            if self.pellets.num_eaten == 70:
                self.ghosts.clyde.start_node.allow_access(LEFT, self.ghosts.clyde)
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
                    self.textgroup.add_text(
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
                            self.textgroup.show_text(GAMEOVERTXT)
                            self.pause.set_pause(pause_time=3, func=self.restart_game)
                        else:
                            self.pause.set_pause(pause_time=3, func=self.reset_level)

    def check_fruit_events(self):
        if self.pellets.num_eaten == 50 or self.pellets.num_eaten == 140:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.get_node_from_tiles(9, 20), self.level)
                print(self.fruit)
        if self.fruit is not None:
            if self.pacman.collide_check(self.fruit):
                self.update_score(self.fruit.points)
                self.textgroup.add_text(
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
        self.textgroup.update_level(self.level)

    def restart_game(self):
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.start_game()
        self.score = 0
        self.textgroup.update_score(self.score)
        self.textgroup.update_level(self.level)
        self.textgroup.show_text(READYTXT)
        self.life_sprites.reset_lives(self.lives)
        self.fruit_captured = []

    def reset_level(self):
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.textgroup.show_text(READYTXT)

    def update_score(self, points):
        self.score += points
        self.textgroup.update_score(self.score)

    # def create_buttons(self):
    #     font = pygame.font.Font(FONT_FAMILY, 36)

    #     start_button_rect = pygame.Rect(SCREENWIDTH - 250, 200, 200, 50)
    #     start_button = pygame.draw.rect(self.screen, GREEN, start_button_rect)
    #     start_text = font.render("START GAME", True, WHITE)
    #     start_text_rect = start_text.get_rect(center=start_button_rect.center)

    #     exit_button_rect = pygame.Rect(SCREENWIDTH - 250, 270, 200, 50)
    #     exit_button = pygame.draw.rect(self.screen, RED, exit_button_rect)
    #     exit_text = font.render("EXIT", True, WHITE)
    #     exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)

    #     algorithm_button_rect = pygame.Rect(SCREENWIDTH - 250, 340, 200, 50)
    #     algorithm_button = pygame.draw.rect(self.screen, BLUE, algorithm_button_rect)
    #     algorithm_text = font.render(self.current_algorithm, True, WHITE)
    #     algorithm_text_rect = algorithm_text.get_rect(center=algorithm_button_rect.center)

    #     ghost_button_rect = pygame.Rect(SCREENWIDTH - 250, 410, 200, 50)
    #     ghost_button = pygame.draw.rect(self.screen, BLUE, ghost_button_rect)
    #     ghost_text = font.render("Ghost", True, WHITE)
    #     ghost_text_rect = ghost_text.get_rect(center=ghost_button_rect.center)

    #     ghost_status_text = font.render(str(self.have_ghosts), True, WHITE)
    #     ghost_status_rect = ghost_status_text.get_rect(
    #         center=(ghost_button_rect.centerx, ghost_button_rect.centery + 30)
    #     )

    #     self.screen.blit(algorithm_text, algorithm_text_rect)
    #     self.screen.blit(start_text, start_text_rect)
    #     self.screen.blit(exit_text, exit_text_rect)
    #     self.screen.blit(ghost_text, ghost_text_rect)
    #     self.screen.blit(ghost_status_text, ghost_status_rect)
    #     return start_button, exit_button, algorithm_button, ghost_button

    # def handle_button_click(
    #     self,
    #     pos: tuple[int, int],
    #     start_button: pygame.Rect,
    #     exit_button: pygame.Rect,
    #     algorithm_button: pygame.Rect,
    #     ghost_button: pygame.Rect,
    # ):
    #     if start_button.collidepoint(pos):
    #         self.handle_space_key()
    #     elif exit_button.collidepoint(pos):
    #         pygame.quit()
    #         exit()
    #     elif algorithm_button.collidepoint(pos):
    #         self.change_algorithm()
    #     elif ghost_button.collidepoint(pos):
    #         self.have_ghosts = not self.have_ghosts

    # def handle_space_key(self):
    #     # Xử lý sự kiện tương tự khi nhấn phím cách (Space)
    #     if self.pacman.alive:
    #         self.pause.set_pause(player_paused=True)
    #         if not self.pause.paused:
    #             self.textgroup.hide_text()
    #             self.show_entities()
    #         else:
    #             self.textgroup.show_text(PAUSETXT)

    # def change_algorithm(self):
    #     current_index = ALGORITHMS.index(self.current_algorithm)
    #     next_index = (current_index + 1) % len(ALGORITHMS)
    #     self.current_algorithm = ALGORITHMS[next_index]

    def render(self):
        self.screen.blit(self.background, (0, 0))
        # self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.textgroup.render(self.screen)

        for i in range(len(self.life_sprites.images)):
            x = self.life_sprites.images[i].get_width() * i
            y = SCREENHEIGHT - self.life_sprites.images[i].get_height()
            self.screen.blit(self.life_sprites.images[i], (x, y))

        for i in range(len(self.fruit_captured)):
            x = SCREENWIDTH - self.fruit_captured[i].get_width() * (i + 1)
            y = SCREENHEIGHT - self.fruit_captured[i].get_height()
            self.screen.blit(self.fruit_captured[i], (x, y))

        # start_button, exit_button, algorithm_button, ghost_button = self.create_buttons()
        pygame.display.update()


if __name__ == "__main__":
    game = GameController()
    game.start_game()
    while True:
        game.update()
