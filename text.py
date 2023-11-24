import pygame

from constants import *
from vector import Vector2

FONT_FAMILY = "font/PressStart2P-Regular.ttf"

class Text(object):
    def __init__(self, text, color, x, y, size, time=None, id=None, visible=True):
        self.id = id
        self.text = text
        self.color = color
        self.size = size
        self.visible = visible
        self.position = Vector2(x, y)
        self.timer = 0
        self.lifespan = time
        self.label = None
        self.destroy = False
        self.setup_font(FONT_FAMILY)
        self.create_label()

    def setup_font(self, font_path):
        self.font = pygame.font.Font(font_path, self.size)

    def create_label(self):
        self.label = self.font.render(self.text, 1, self.color)

    def set_text(self, new_text):
        self.text = str(new_text)
        self.create_label()

    def update(self, dt):
        if self.lifespan is not None:
            self.timer += dt
            if self.timer >= self.lifespan:
                self.timer = 0
                self.lifespan = None
                self.destroy = True

    def render(self, screen):
        if self.visible:
            x, y = self.position.as_tuple()
            screen.blit(self.label, (x, y))


class TextGroup(object):
    def __init__(self):
        self.next_id = 10
        self.all_text:dict[int, Text] = {}
        self.setup_text()
        self.show_text(READYTXT)

    def add_text(self, text, color, x, y, size, time=None, id=None):
        self.next_id += 1
        self.all_text[self.next_id] = Text(text, color, x, y, size, time=time, id=id)
        return self.next_id

    def remove_text(self, id):
        self.all_text.pop(id)

    def setup_text(self):
        size = TILEHEIGHT
        self.all_text[SCORETXT] = Text("0".zfill(8), WHITE, 0, TILEHEIGHT, size)
        self.all_text[LEVELTXT] = Text(
            str(1).zfill(3), WHITE, 23 * TILEWIDTH, TILEHEIGHT, size
        )
        self.all_text[READYTXT] = Text(
            "READY!", YELLOW, 11.25 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False
        )
        self.all_text[PAUSETXT] = Text(
            "PAUSED!", YELLOW, 10.625 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False
        )
        self.all_text[GAMEOVERTXT] = Text(
            "GAMEOVER!", YELLOW, 10 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False
        )
        self.add_text("SCORE", WHITE, 0, 0, size)
        self.add_text("LEVEL", WHITE, 23 * TILEWIDTH, 0, size)

    def update(self, dt):
        for tkey in list(self.all_text.keys()):
            self.all_text[tkey].update(dt)
            if self.all_text[tkey].destroy:
                self.remove_text(tkey)

    def show_text(self, id):
        self.hide_text()
        self.all_text[id].visible = True

    def hide_text(self):
        self.all_text[READYTXT].visible = False
        self.all_text[PAUSETXT].visible = False
        self.all_text[GAMEOVERTXT].visible = False

    def update_score(self, score):
        self.update_text(SCORETXT, str(score).zfill(8))

    def update_level(self, level):
        self.update_text(LEVELTXT, str(level + 1).zfill(3))

    def update_text(self, id, value):
        if id in self.all_text.keys():
            self.all_text[id].set_text(value)

    def render(self, screen):
        for text_key in list(self.all_text.keys()):
            self.all_text[text_key].render(screen)
