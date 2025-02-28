class Expert:
    def __init__(self):
        # Initialize any internal state if needed.
        pass

    def get_decision(self, expert_state):
        """
        Given the expert_state (output by Board.get_expert_state()),
        returns a dictionary mapping each player ('player1', 'player2') to:
            - task: the high-level task being executed (one of:
                     "obtain_raw_fish", "chop_fish", "fry_fish", "plate_fish", "deliver_fish", "idle")
            - action: the discrete move command for this tick ("UP", "DOWN", "LEFT", "RIGHT", or "ACTION")
        
        This decision uses subroutine-relevant inputs:
          • Each player's current position and held item details.
          • The positions of key stations:
              - fish_crate (raw fish source)
              - chopping_station (chopping boards / CBoard objects)
              - fryer (Fryer objects)
              - plate_stack (Plate stations)
              - delivery_area (computed from map_layout)
          • The map layout (corner_coordinates, screen size) to compute the delivery area.
        """
        decisions = {}
        
        for player_label, pdata in expert_state["players"].items():
            position = pdata["position"]
            holding_type = pdata["holding"]  # e.g., "Fish", "Plate", or None
            # Retrieve the player's full state vector from get_state()
            state_vector = pdata.get("state_vector", [])
            
            # Determine the current task.
            if holding_type is None:
                task = "obtain_raw_fish"
            elif holding_type == "Plate":
                task = "deliver_fish"
            elif holding_type == "Fish":
                # Use the state vector indices to determine the fish's processing stage.
                # According to Player.get_state():
                #   index 3: raw fish (not chopped)
                #   index 4: chopped fish (not fried)
                #   index 5: fried fish
                if len(state_vector) >= 6:
                    if state_vector[3] == 1:
                        task = "chop_fish"
                    elif state_vector[4] == 1:
                        task = "fry_fish"
                    elif state_vector[5] == 1:
                        task = "plate_fish"
                    else:
                        task = "idle"
                else:
                    task = "idle"
            else:
                task = "idle"
            
            # Select the target station based on the determined task.
            target = None
            stations = expert_state["stations"]
            if task == "obtain_raw_fish":
                if stations["fish_crate"]:
                    target = self._nearest(position, stations["fish_crate"])
            elif task == "chop_fish":
                if stations["chopping_station"]:
                    target = self._nearest(position, stations["chopping_station"])
            elif task == "fry_fish":
                if stations["fryer"]:
                    target = self._nearest(position, stations["fryer"])
            elif task == "plate_fish":
                if stations["plate_stack"]:
                    target = self._nearest(position, stations["plate_stack"])
            elif task == "deliver_fish":
                # Compute the center of the delivery area region.
                da = stations["delivery_area"]
                target = ((da["top_left"][0] + da["bottom_right"][0]) / 2,
                          (da["top_left"][1] + da["bottom_right"][1]) / 2)
            
            # Compute the next move direction based on the player's current position and the target.
            if target:
                action = self._compute_direction(position, target)
            else:
                action = "ACTION"
            
            decisions[player_label] = {"task": task, "action": action}
        
        return decisions

    def _nearest(self, position, targets):
        """
        Given a current position and a list of target positions,
        returns the target that is nearest (using Manhattan distance).
        """
        best = None
        best_dist = float('inf')
        for t in targets:
            dist = abs(position[0] - t[0]) + abs(position[1] - t[1])
            if dist < best_dist:
                best_dist = dist
                best = t
        return best

    def _compute_direction(self, position, target):
        """
        Computes the next move command given the current position and target position.
        Returns one of: "UP", "DOWN", "LEFT", "RIGHT", or "ACTION" if already close enough.
        Tolerance is set to 32 pixels.
        """
        x, y = position
        tx, ty = target

        tolerance = 32
        if abs(x - tx) < tolerance and abs(y - ty) < tolerance:
            return "ACTION"

        dx = tx - x
        dy = ty - y

        # Move in the direction of the larger distance difference.
        if abs(dx) > abs(dy):
            return "RIGHT" if dx > 0 else "LEFT"
        else:
            return "DOWN" if dy > 0 else "UP"
