class Scorer:
    def __init__(self):
        self.action_prizes = {getting resource: 50
                              putting it: 0.25*prep_coeff
                              prepping: 150
                              plate: 50
                              Putting it on a plate
                              delivering to the Menu}
        
        #SYMMETRIC VALUES FOR REMOVING STUFF
        
    def get_action_prize(self, action):
        return self.action_prizes[action]
