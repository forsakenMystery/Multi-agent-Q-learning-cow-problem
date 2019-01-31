class BaseAgent:
    def __init__(self, name, state, ally_state, cow_state):
        self.state = state
        self.ally_state_prime = self.state_prime = self.cow_state_prime = 0
        self.cow_state = cow_state
        self.ally_state = ally_state
        self.name = name

    def message_passing(self, ally_position):
        self.ally_state_prime = ally_position
