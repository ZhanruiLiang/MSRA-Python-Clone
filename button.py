import pygame
from pygame import Rect
from pygame.sprite import Sprite

pygame.font.init()
font = pygame.font.SysFont('monospace', 16)
Transparent = (0, 0, 0, 0)

class PyeventHandler:
    def handle(self):
        pass
    def step(sefl):
        pass

class Button(Sprite, PyeventHandler):
    Press, Over, Release, Out, Scroll = 0, 1, 2, 3, 5
    AcceptEventTypes = [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]
    BgColor = (0, 0, 0, 0x55)

    def __init__(self, rect, caption, visible=0):
        self.rect = rect
        self.visible = visible
        self.enable = True
        self.callbacks = {}
        self.caption = caption

        self.image = pygame.Surface(self.rect.size).convert_alpha()
        self.image.fill(self.BgColor)
        self.image.blit(font.render(caption, 1, (0xff, 0xff, 0xff, 0xff), self.BgColor), 
            (self.rect.size[0]/2-font.size(caption)[0]/2,
                self.rect.size[1]/2-font.size(caption)[1]/2))

        self._mouseOver = 0

    def bind(self, eventType, callback):
        """ 
The `eventType` can be one of 
(Button.Press, Button,Over, Button.Release, Button.Out, Button.Scroll).
The `callback` is a function with prototype callback(event).
"""
        calllist = self.callbacks.get(eventType, [])
        calllist.append(callback)
        self.callbacks[eventType] = calllist

    def handle(self, event):
        pet = event.type # Pygame Event Type
        if pet not in self.AcceptEventTypes:
            return False 
        if not self.rect.collidepoint(event.pos):
            if self._mouseOver == 1 and pet == pygame.MOUSEMOTION:
                self._mouseOver = 0
                for callback in self.callbacks.get(self.Out, []):
                    callback(event)
            return False
        # event.pos in rect
        et = None
        if pet == pygame.MOUSEBUTTONDOWN:
            if event.button < 4:
                et = self.Press
            else:
                et = self.Scroll
        elif pet == pygame.MOUSEBUTTONUP:
            if event.button < 4:
                et = self.Release
        elif pet == pygame.MOUSEMOTION:
            et = self.Over
            self._mouseOver = 1
        self._event = event

        if et is None: return False
        for callback in self.callbacks.get(et, []):
            callback(event)
        return True

    def step(self):
        if self._mouseOver:
            for callback in self.callbacks.get(self.Over, []):
                callback(self._event)

    def __repr__(self):
        return 'Button(%s, %s)'%(self.rect, self.caption)
