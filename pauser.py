class Pause(object):
    def __init__(self, paused=False):
        self.paused = paused
        self.timer = 0
        self.pause_time = None
        self.func = None

    def update(self, dt):
        if self.pause_time is not None:
            self.timer += dt
            if self.timer >= self.pause_time:
                self.timer = 0
                self.paused = False
                self.pause_time = None
                return self.func
        return None

    def set_pause(self, pause_time=None, func=None):
        self.timer = 0
        self.func = func
        self.pause_time = pause_time
        self.flip()

    def flip(self):
        self.paused = not self.paused
