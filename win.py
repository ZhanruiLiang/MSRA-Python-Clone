from button import PyeventHandler, Button
from pygame import Rect, Color, Surface
from pygame.sprite import Sprite
from pygame.locals import *
import pygame
import config

class WinScreen(Sprite, PyeventHandler):
    def __init__(self, winner):
        self.winner = winner
        self.draw()
        self.finished = 0

    def draw(self):
        W, H = config.W, config.H
        self.image = pygame.image.load('win.png').convert_alpha()
        w, h = self.image.get_rect().size
        self.rect = Rect(((W - w)/2, (H - h)/2), (w, h))

        font = pygame.font.SysFont('monospace', 24, bold=True)
        text1 = font.render('AI %s win.' %(self.winner.name), 1, Color("white"))
        text2 = font.render('Press Enter or q to exit.', 1, Color("white"))
        self.image.blit(text1, (50, 50))
        self.image.blit(text2, (50, 100))

    def update(self):
        pass

    def handle(self, event):
        if event.type == KEYDOWN:
            if event.key in (K_RETURN, K_q):
                self.finished = 1

    def step(self):
        pass
