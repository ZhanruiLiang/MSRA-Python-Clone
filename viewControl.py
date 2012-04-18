from button import Button
from pygame import Rect

class ViewControl:
    def __init__(self, shippo):
        self.shippo = shippo
        self.size = shippo.W, shippo.H

        # init buttons
        thick = 40
        w, h = self.size
        visible = 0
        self.buttons = []
        self.buttons.append(Button(Rect((0, 0), (w, thick)), 'up', visible))
        self.buttons.append(Button(Rect((w - thick, 0), (thick, h)), 'right', visible))
        self.buttons.append(Button(Rect((0, h - thick), (w, thick)), 'down', visible))
        self.buttons.append(Button(Rect((0, 0), (thick, h)), 'left', visible))

        self.buttons.append(Button(Rect((0, 0), (w, h)), 'scroll', 0))

        for button in self.buttons:
            self.shippo.otherSprites.append(button)

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

    def mover(self, ds):
        def callback(event):
            self.shippo.viewBox.move(ds)
        return callback

    def handle(self, event):
        for button in self.buttons:
            button.handle(event)

    def step(self):
        for button in self.buttons:
            button.step()
            
