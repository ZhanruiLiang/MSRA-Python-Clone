class GameEvent:
    def __lt__(self, e):
        return self.time < e.time

class ShipDamage(GameEvent):
    def __init__(self, time, ship, damage):
        self.time = time
        self.ship = ship
        self.damage = damage

class ShipRecover(GameEvent):
    def __init__(self, time, ship, val):
        self.time = time
        self.ship = ship
        self.val = val

class ShipAttack(GameEvent):
    def __init__(self, time, ship):
        self.time = time
        self.ship = ship

class ObjHit(GameEvent):
    def __init__(self, time, obj1, obj2):
        self.time = time
        self.obj1 = obj1
        self.obj2 = obj2
    def __repr__(self):
        return 'ObjHit(%s, %s)' % (self.obj1, self.obj2)
