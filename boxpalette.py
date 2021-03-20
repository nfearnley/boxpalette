boxen = (
    "┌─┐ ╭┬╮ ╲ ╱  ╷ ",
    "│ │ ├┼┤  ╳  ╶┼╴",
    "└─┘ ╰┴╯ ╱ ╲  ╵ "
)

boxnames = {
    "─": "Horizontal",
    "│": "Vertical",
    "┌": "Down and Right",
    "┐": "Down and Left",
    "└": "Up and Right",
    "┘": "Up and Left",
    "├": "Vertical and Right",
    "┤": "Vertical and Left",
    "┬": "Down and Horizontal",
    "┴": "Up and Horizontal",
    "┼": "Vertical and Horizontal",
    "╭": "Arc Down and Right",
    "╮": "Arc Down and Left",
    "╯": "Arc Up and Left",
    "╰": "Arc Up and Right",
    "╱": "Diagonal Upper Right to Lower Left",
    "╲": "Diagonal Upper Left to Lower Right",
    "╳": "Diagonal Cross",
    "╴": "Left",
    "╵": "Up",
    "╶": "Right",
    "╷": "Down"
}


import nygame
from nygame import DigiText as T
import pygame
import math
from tkinter import Tk

BOXEN_X = 48
BOXEN_Y = 10

def copy2clipboard(s):
    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(s)
    r.update()
    r.destroy()

# This should be happening automatically by nygame, but I guess it isn't.
def scale_mouse(pos, scale):
    x, y = pos
    return math.floor(x / scale), math.floor(y / scale)


class Boxen:
    BOX_W = 7
    BOX_H = 16
    BOX_SIZE = (BOX_W, BOX_H)
    def __init__(self, pos):
        self.pos = pos
        self.select = None
        with open("boxen.png") as f:
            self.boxen_texture = pygame.image.load(f)
        with open("selector.png") as f:
            self.selector_texture = pygame.image.load(f)

    @property
    def select(self):
        return self._select

    @select.setter
    def select(self, pos):
        if pos is None:
            self._select = None
            return
        x, y = pos
        if x < 0 or y < 0:
            pos = None
        self._select = pos

    @property
    def screen_select(self):
        """Screen coordinates of selection"""
        if self.local_select is None:
            return None
        x, y = self.local_select
        boxen_x, boxen_y = self.pos
        x += boxen_x
        y += boxen_y
        return x, y
    
    @screen_select.setter
    def screen_select(self, screen_pos):
        if screen_pos is None:
            self.select = None
            return
        x, y = screen_pos
        boxen_x, boxen_y = self.pos
        x = math.floor((x-boxen_x)/self.BOX_W)
        y = math.floor((y-boxen_y)/self.BOX_H)
        self.select = x, y
    
    @property
    def local_select(self):
        """Local coordinates of selection"""
        if self.select is None:
            return None
        x, y = self.select
        x = (x * self.BOX_W)
        y = (y * self.BOX_H)
        return x, y

    @local_select.setter
    def local_select(self, local_pos):
        if local_pos is None:
            self.select = None
            return
        x, y = local_pos
        x = math.floor(x/self.BOX_W)
        y = math.floor(y/self.BOX_H)
        self.select = x, y

    def render_to(self, surface):
        surface.blit(self.boxen_texture, self.pos)
        if self.select:
            surface.blit(self.selector_texture, self.screen_select)
            if self.box_surface:
                surface.blit(self.box_surface, (20,27))
            if self.boxname:
                T(self.boxname).render_to(surface, (10, 80))

    @property
    def box_surface(self):
        if self.local_select is None:
            return None
        if self.box_char is None:
            return None
        return self.boxen_texture.subsurface(pygame.Rect(self.local_select, self.BOX_SIZE))

    @property
    def box_char(self):
        if self.select is None:
            return None
        x, y = self.select
        if x < 0 or y < 0:
            return None
        try:
            box_char = boxen[y][x]
        except IndexError:
            return None
        if box_char == " ":
            return None
        return box_char

    @property
    def boxname(self):
        if self.box_char is None:
            return ""
        return boxnames.get(self.box_char, "")

class BoxPalette(nygame.Game):
    def __init__(self):
        super().__init__(scale=2, size=(200,100), bgcolor="#1e1e1e")
        T.font = "Arial"
        T.color = "grey"
        T.size = 14
        self.boxen = Boxen((48, 10))
        self.select = None
        self.flash = 0
        self.flash_surface = pygame.Surface(self.size)
        self.flash_surface.fill("yellow")

    def loop(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.boxen.screen_select = scale_mouse(event.pos, 4)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.boxen.screen_select = scale_mouse(event.pos, 4)
                if self.boxen.box_char:
                    copy2clipboard(self.boxen.box_char)
                    self.flash = 6

        self.boxen.render_to(self.surface)
        if self.flash:
            self.flash_surface.set_alpha(self.flash * 10)
            self.surface.blit(self.flash_surface, (0, 0))
            self.flash -= 1

if __name__ == "__main__":
    BoxPalette().run()

