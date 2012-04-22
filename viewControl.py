from button import Button
from pygame import Rect
import pygame
from pygame.locals import *

class ViewControl:
    def __init__(self, shippo):
        self.shippo = shippo
        self.size = shippo.W, shippo.H

        # init view control buttons
        thick = 40
        w, h = self.size
        visible = 0
        self.buttons = []
        self.buttons.append(Button(Rect((0, 0), (w, thick)), 'up', visible))
        self.buttons.append(Button(Rect((w - 3*thick, 0), (3*thick, h)), 'right', visible))
        self.buttons.append(Button(Rect((0, h - thick), (w, thick)), 'down', visible))
        self.buttons.append(Button(Rect((0, 0), (thick, h)), 'left', visible))

        self.buttons.append(Button(Rect((0, 0), (w, h)), 'scroll', 0))

        for button in self.buttons:
            self.shippo.UISprites.append(button)

        # bind event
        self.speed = speed = 10 # scroll speed
        self.buttons[0].bind(Button.Over, self.mover((0, -speed)))
        self.buttons[1].bind(Button.Over, self.mover((speed, 0)))
        self.buttons[2].bind(Button.Over, self.mover((0, speed)))
        self.buttons[3].bind(Button.Over, self.mover((-speed, 0)))
        def scroll(event):
            ds = 0.05
            if event.button == 4: 
                # scroll up, zoom in
                ds = ds
            elif event.button == 5:
                ds = -ds
            self.shippo.viewBox.zoom(event.pos, ds)
        self.buttons[4].bind(Button.Scroll, scroll)
        # self.buttons[4].bind(Button.Press, lambda event:self.shippo.viewBox.zoom(event.pos, 0))

        hidedash = Button(Rect(self.shippo.dashBoard.rect), 'hidedash', 0)
        self.buttons.append(hidedash)
        hidedash.bind(Button.Over, self.hide_dash)
        def start_show(event):
            self.showingDash = 1
            self.shippo.dashBoard.hided = 0
        hidedash.bind(Button.Out, start_show)
        self.showingDash = 0

        # bind events for every ship
        def shower(obj):
            def show_detail(event):
                shippo.detailBoard.update_target(obj)
            return show_detail

        for ship in self.shippo.ships:
            ship.button.bind(Button.Over, shower(ship))
            ship.button.bind(Button.Out, shower(None))

        for res in self.shippo.resources:
            res.button.bind(Button.Over, shower(res))
            res.button.bind(Button.Out, shower(None))

        self.vim_bindings = {K_h: self.mover((-speed, 0)), K_j: self.mover((0, speed)), K_k: self.mover((0, -speed)), K_l: self.mover((speed, 0))}

    def hide_dash(self, event):
        dash = self.shippo.dashBoard
        x0 = self.shippo.W - 4
        speed = 20
        if abs(dash.rect.left - x0) < speed:
            dash.rect.left = x0
            dash.hided = 1
        else:
            dash.rect.left += speed

    def show_dash(self):
        dash = self.shippo.dashBoard
        speed = 40
        x0 = self.shippo.BoardPos[0]
        if abs(dash.rect.left - x0) < speed:
            dash.rect.left = x0
            self.showingDash = 0
        else:
            dash.rect.left -= speed

    def mover(self, ds):
        def callback(event):
            self.shippo.viewBox.target = None
            self.shippo.viewBox.move(ds)
        return callback

    def handle(self, event):
        for button in self.buttons:
            button.handle(event)
        if event.type == pygame.KEYDOWN:
            if (event.mod & pygame.KMOD_ALT) and event.key in map(ord, '0123456789'):
                id = event.key - pygame.K_0
                for ship in self.shippo.ships:
                    if ship.id == id:
                        self.shippo.viewBox.follow(ship)
                        self.shippo.detailBoard.update_target(ship)
                        break
            elif (event.mod & pygame.KMOD_ALT) and event.key == ord('`'):
                self.shippo.viewBox.follow(None)
            if event.key == K_LALT:
                show = sum(1 for ship in self.shippo.ships if ship._show_debug)
                for ship in self.shippo.ships:
                    ship._show_debug = not show

    def step(self):
        for button in self.buttons:
            button.step()
        pressed = pygame.key.get_pressed()
        for key in self.vim_bindings:
            if pressed[key]:
                self.vim_bindings[key](None)
        self.shippo.viewBox.step()
        if self.showingDash:
            self.show_dash()
