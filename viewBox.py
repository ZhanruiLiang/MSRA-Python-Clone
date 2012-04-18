import config
from vec2d import Vec2d

class ViewBox:
    MinScale = 0.05
    MaxScale = 20
    def __init__(self, size):
        self.originSize = size
        self.size = map(float, size)
        self.center = Vec2d(size[0]/2, size[1]/2)
        self.scale = 1.0

    def move(self, dp):
        self.center += dp

    def zoom(self, center, ds):
        center = self.posScreen2world(center)

        scale = self.scale
        self.scale += ds
        self.scale = max(min(self.scale, self.MaxScale), self.MinScale)
        dp = self.center - center
        self.center = center + scale/self.scale * dp
        self.size = tuple(x*self.scale for x in self.originSize)

    def inside(self, pos, r):
        # x1 in [cx - w/2, cx + w/2], x2 in [pos.x - r, pos.x + r]
        # so does y
        c = self.center
        w, h = self.size
        return max(c.x - w/2, pos.x - r) <= min(c.x + w/2, pos.x + r) and max(c.y - h/2, pos.y - r) <= max(c.y + h/2, pos.y + r)

    def posScreen2world(self, p):
        w, h = self.size
        lx, ly = self.center - (w/2, h/2)
        return Vec2d(lx + p[0] / self.scale, ly + p[1] / self.scale)

    def posWorld2screen(self, p):
        # convert a point in the world coordinate to screen coordinate
        w, h = self.size
        w0, h0 = self.originSize
        pTopleft = self.center - (w/2, h/2)
        return Vec2d((p.x - pTopleft.x)*w/w0, (p.y - pTopleft.y)*h/h0)

    def lenWorld2screen(self, l):
        return l * self.scale

