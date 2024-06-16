class Game:
    def __init__(self, chars, towers, proj):
        self.char_group = chars
        self.tower_group = towers
        self.proj_group = proj
        self.p1went = True
        self.p2went = True
        self.p1received = False
        self.p2received = False
        self.ready = False
    def restart(self):
        self.p1went = False
        self.p2went = False
    def restart_recv(self):
        self.p1received = False
        self.p2received = False
    def update(self):
        self.char_group.update()
        self.tower_group.update()
        self.proj_group.update()
