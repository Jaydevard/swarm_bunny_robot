class State:
    def run(self):
        assert 0, "run not implemented"
    def next(self, input):
        assert 0, "next not implemented"

class StateMachine:
    def __init__(self, initialState):
        self.currentState = initialState
        self.currentState.run()
    def runAll(self, inputs):
        for i in inputs:
            print(i)
            self.currentState = self.currentState.next(i)
            self.currentState.run()

class RobotAction:
    pass

class Idle(State):
    pass
#Are IDLE and ROAMING essentailly the same?
class Roaming(State):
    pass

class Formation(State):
    pass

class Charging(State):
    pass

class Waiting(State):
    pass