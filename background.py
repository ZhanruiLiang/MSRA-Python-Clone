
class Background(GameObj):
    def __init__(self, textureFile):
        super(Background, self).__init__()
        texture = pygame.image.load(textureFile).convert_alpha()
        size = texture.get_size()
        ssize = config.screenW, config.screenH
        ssize = ssize[0] + size[0], ssize[1] + size[1]
        image = pygame.Surface(ssize).convert_alpha()
        for x in xrange(0, ssize[0], size[0]):
            for y in xrange(0, ssize[1], size[1]):
                image.blit(texture, (x, y))
        self.image = image
        self.ssize = ssize
        self.tsize = size
        self.rect = pygame.Rect((0, 0), ssize)
        self._pos = (0, 0)

    def update(self, viewport):
        x, y = self._pos
        w0, h0 = self.tsize
        x0, y0 = viewport.topleft
        x = x0 - (x0 - x) % w0
        y = y0 - (y0 - y) % h0
        self._pos = x, y
        self.rect.topleft = x - x0, y - y0
