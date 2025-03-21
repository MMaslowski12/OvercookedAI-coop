from .utils import parse_commands

class ExpertSystem:
    '''
    Expert Agent for Overcooked

    Moves:

    `Walk_up_to_object(object_name)` – Move towards an interactive object 
    `Pick_up_resource()` – Pick up a resource (e.g., fish, plate)  
    `Put_down_resource()` – Place a resource on a surface  
    `Chop_resource()` – Chop a raw resource (fish)  
    `Fry_resource()` – Fry a chopped fish  
    `Grab_resource()` – Take a cooked or prepared item (e.g., fried fish, plated dish)  
    `Wait()` – Wait for **1 second** (used when waiting for frying to finish) 
    '''

    def __init__(self, player):
        '''
        FishCrate is x, y = (7, 1), (7, 8), CBoard is (8, 1) (8,8), Fryers (9, 1), (9, 8), PlateCrate (11, 1) (11, 8), CounterTop is (12, 1) (12, 8), CBelt is (17, 2), (17, 9)
        '''
        self.player = player
        self.names2coordinates = {
            None: None,
            "FishCrateTop": (352, 156),
            "FishCrateBottom": (352, 380),
            "ChoppingBoardTop": (384, 156),
            "ChoppingBoardBottom": (384, 380),
            "FryerTop": (416, 156),
            "FryerBottom": (416, 380),
            "PlateCrateTop": (480, 156),
            "PlateCrateBottom": (480, 380),
            "CounterTopTop": (512, 156),
            "CounterTopBottom": (512, 380),
            "ConveyorBeltTop": (672, 188),
            "ConveyorBeltBottom": (672, 412),
        }
        
    def grammar_function(self, policy_string):
        #Try parsing, if not working then give the regulsr
        #If it does check individual grammar checks
        try:
            error, parsed_string = parse_commands(policy_string)
            if error:
                return error, parsed_string
        
            policy = parsed_string
            for policy_name, policy_args in policy:
                error, error_message = self._individual_grammar_function(policy_name, policy_args)
                if error:
                    return error, error_message
            
            return 0, policy
        
        except Exception as e:
            return 1, f"Error parsing policy: {e}"
    def _individual_grammar_function(self, policy_name, policy_args):
        if not hasattr(self, policy_name):
            return 1, f"{policy_name} is not an appropriate policy name"
        
        if policy_args is None and policy_name == "walk_up_to_object":
            return 1, f"policy_name {policy_name} must have a policy argument"
        
        if policy_args is not None and policy_args not in self.names2coordinates.keys():
            return 1, f"policy_args {policy_args} is not a valid policy argument"
        
        return 0, None

    def __call__(self, name, args):
        if self._individual_grammar_function(name, args)[0] != 0:
            raise ValueError(self._individual_grammar_function(name, args)[1])
        
        func = getattr(self, name)
        return func(args)

    def walk_up_to_object(self, *args):
        #TODO later: better pathfinding: what algorithm (A*?), what input, what map representation
        # Get player's current position
        player_x, player_y = self.player.rect.center

        # Get target object position
        object_name = args[0]
        target_x, target_y = self.names2coordinates[object_name]
        
        # Calculate distance to object
        distance_x = target_x - player_x
        distance_y = target_y - player_y
        
        actions = [False, False, False, False, False]
        
        actions[0] = distance_y < 0
        actions[1] = distance_y > 0
        actions[2] = distance_x < 0
        actions[3] = distance_x > 0

        close_enough = (distance_x**2 + distance_y**2) < self.player.HAND_LENGTH
        
        return actions, close_enough

    def pick_up_resource(self, *args):
        # Placeholder for picking up a resource
        return [False, False, False, False, True], True

    def put_down_resource(self, *args):
        # Placeholder for putting down a resource
        return [False, False, False, False, True], True

    def chop_resource(self, *args):
        # Placeholder for chopping a resource
        if self.player.hands is not None and self.player.hands.chopped: #If your hands have something thats already chopped, you're done
            return [False, False, False, False, False], True
        
        else: #Else, continue doing something until it is possible to do something
            action_possible = self.player.action_possible() is not None
            return [False, False, False, False, True], not action_possible

    def fry_resource(self, *args):
        # Placeholder for frying a resource
        if self.player.hands is not None:
            return [False, False, False, False, False], True
        
        else:
            return [False, False, False, False, True], self.player.action_possible()

    def grab_resource(self, *args):
        return [False, False, False, False, True], True

    def wait(self, *args):
        return [False, False, False, False, False], True

