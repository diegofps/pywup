from pywup.services.system import error

class StateMachine:

    def __init__(self):

        self.states = {}


    def add(self, name, callback):

        if name in self.states:
            error("Another state is already using this name:", name)
        
        self.states[name] = callback


    def move_to(self, name):

        if not name in self.states:
            error("Unknown state:", name)
        self.current = self.states[name]


    def run(self, start):

        self.alive = True
        self.move_to(start)

        while self.alive:
            self.current(self)

