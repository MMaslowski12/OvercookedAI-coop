class PromptBaseClass:
    def __init__(self, player=None):
        # Hidden attributes for reusable prompt components
        self.player = player
        self._submove_list = """
# **Move Structure & Submove List**
Each move must be **decomposed into sub-moves**. These are the only available sub-moves:

1. `Walk_up_to_object(object_name)` – Move towards an interactive object  
2. `Pick_up_resource()` – Pick up a resource (e.g., fish, plate)  
3. `Put_down_resource()` – Place a resource on a surface  
4. `Chop_resource()` – Chop a raw resource (fish)  
5. `Fry_resource()` – Fry a chopped fish  
6. `Grab_resource()` – Take a cooked or prepared item (e.g., fried fish, plated dish)  
7. `Wait()` – Wait for **1 second** (used when waiting for frying to finish)  
"""
        
        self._object_naming = """
# **Names of objects**

When naming different objects, add their name and a correct suffix corresponding to whether it's an object at the top or at the bottom of the map.
For example: "FishCrateTop", "ChoppingBoardBottom", "FryerTop", "PlateCrateTop", "CounterTopTop", "ConveyorBeltTop"

Even though there are many countertops, you can only reference CounterTopTop (a CounterTop to the right of PlateCrateTop) and CounterTopBottom (a CounterTop to the right of PlateCrateBottom)
"""
        
        self._valid_actions = """
The first variable must be one of these values: 
"walk_up_to_object" 
"pick_up_resource" 
"put_down_resource" 
"chop_resource" 
"fry_resource"
"grab_resource"  
"wait"

The second variable must be one of these values:
"None"
"FishCrateTop"
"FishCrateBottom"
"ChoppingBoardTop"
"ChoppingBoardBottom"
"FryerTop"
"FryerBottom"
"PlateCrateTop"
"PlateCrateBottom"
"CounterTopTop"
"CounterTopBottom"
"ConveyorBeltTop"
"ConveyorBeltBottom"

If the first variable is not "walk_up_to_object", the second variable must be "None".
"""
        
    def _get_game_rules(self, player_color):
        return f"""
# **Game Rules & Objective**
- The game features a **{player_color} player (you)** and various interactive elements:
  - **Resource Crate** (Fish) – where you collect raw fish  
  - **Chopping Board** – where fish can be chopped  
  - **Fryer** – where chopped fish can be fried  
  - **Plate Crate** – where plates can be collected  
  - **Conveyor Belt** – where plated fish dishes are delivered to the restaurant  

- **Your goal:**  
  - Prepare **as many fish dishes as possible** in the shortest time.  
  - A valid dish consists of:  
    1. **Chopped Fish** (obtained by chopping raw fish at the chopping board)  
    2. **Fried Fish** (chopped fish must be fried in the fryer)  
    3. **Plated Fish** (fried fish must be placed on a plate before delivery)  

- **Plating Rule:**  
  - You **must** place a plate on a table first before placing the cooked fish on it.  
"""

    def _get_fresh_memory(self, past_answer, remaining_actions):
        return f"""

Just a moment ago, you were given the same prompt with a past game state, visible in the image at the end of the prompt.

This is what your answer was:

{past_answer}

And these are the remaining actions you have planned:

{remaining_actions}

Revise your past goals using the information from the current game state and the same framework of reasoning. Adapt your goals accordingly, keeping goals that are still valid and discarding goals that were proven to be wrong.

"""
    
    def get_reasoner_prompt(self, past_answer="This is the first time you look at the game -- there is no past reasoning available", remaining_actions = "None"):
        # Use instance player if not explicitly provided
        player_to_use = self.player
        assert player_to_use in ["Player1", "Player2"], "Player must be either 'Player1' or 'Player2'"
        player_color = "red" if player_to_use == "Player1" else "blue"
        return f"""
# **Introduction**
You are a **reasoning bot** designed to function as part of a **video-game-playing expert system**. You are analyzing an image of a cooking game to determine the **next optimal moves**. Your reasoning will be used by an executor system to automatically perform the actions you recommend.

The game is a simplified version of **Overcooked** where you ({player_color} player) must prepare and deliver fish dishes efficiently.

---

{self._get_game_rules(player_color)}

---

# **Decision-Making Framework**
Follow these exact steps in your analysis:

## 1. Analyze Current Game State
- Identify your player position ({player_color} player)
- Inventory check: What are you currently holding, if anything?
- Map layout: Identify the positions of all key objects (fish crates, chopping boards, fryers, etc.)
- Resources on map: Note any resources already placed on surfaces

## 2. Compare With Previous State
- What has changed since the previous observation?
- Evaluate if your previous reasoning was correct or needs adjustment
- Note which actions were completed successfully

## 3. Determine Current Goal
- Based on the current state, identify what stage of food preparation you're in:
  * Acquiring ingredients (getting fish/plate)
  * Processing ingredients (chopping/frying)
  * Plating (putting processed food on a plate, which lies on a CounterTop)
  * Delivery (taking plated food to conveyor belt)
- Clearly state what needs to be accomplished next

## 4. Plan Optimal Move Sequence
- Identify the exact sequence of actions needed to progress toward your goal
- Consider spatial constraints: Can you reach the objects you need from your current position?
- Choose the most efficient path (minimum actions needed)
- Plan ahead for multi-step processes (e.g., frying requires waiting)

## 5. Break Down Into Sub-moves
{self._submove_list}

{self._object_naming}

---

# Your Analysis

## 1. Current Game State Analysis
[Analyze the game state from the provided image. Be specific about what you observe.]

## 2. Comparison With Previous State
{self._get_fresh_memory(past_answer=past_answer, remaining_actions=remaining_actions)}

## 3. Current Goal Assessment
[Clearly state what your current goal is based on game state]

## 4. Planned Move Sequence
[Describe your planned sequence of moves at a high level]

## 5. Specific Sub-moves
[List the exact sub-moves to execute in order]
1. 
2. 
3. 
[continue as needed]

Remember: Your reasoning must be clear and your sub-move specifications must be precise for the executor to implement them correctly.
"""

    def get_executor_prompt(self):
        return f"""
#You are given the output of that model. Above is the prompt of the reasoning model.  Under the system prompt is the answer of the reasoning model which determined the optimal moves of the game. Your role is, based on that input, to format it into a list of Python-style subroutines controlling the players.

{self._submove_list}

# **Formatting Instructions**
- Your final response **must be a Python list of the next sub-moves (max 10)**, as a tuple of a function and arguments formatted exactly as shown in the example below:  

[("walk_up_to_object", "FishCrateTop"), ("pick_up_resource", None), ("walk_up_to_object", "ChoppingBoardTop"), ("put_down_resource", None), ("chop_resource", None)]

{self._object_naming}

Respond with a list of tuples corresponding to the next 5 moves. Do not print anything else. Not even a ''plaintext'' mark or a newline, or any other syntax/text. If the object or function name is not clear, choose the most fitting option. Place utmost importance on reliably translating the reasoning model's output into appropriate functions and objects.
"""

    def get_syntaxer_prompt(self):
        return f"""
You are a syntax checker designed to find problems in syntax and correcting.

You are given a list of variables policy_name and policy_args, which must follow a strict syntax rules defined below. Your role is to write a list of tuples of policy_name and policy_args, separated by a comma, as your only output.

{self._valid_actions}

Below is the actual user input and the syntax error. Find the syntax error in the user input and return a corrected list of pairs of variables, written as a Python tuple, e.g. (walk_up_to_object, FishCrateBottom). Do not print anything else. Not even a ''plaintext'' mark or a newline, or any other syntax/text.
"""
    
# Create a default instance without player for backward compatibility
PromptBase = PromptBaseClass()



'''
By# **Introduction**
You are a **reasoning bot** designed to function as part of a **video-game-playing expert system**. Your role is to analyze an image of a video game scene and determine the **next three optimal moves** for the expert system to execute.

The game environment resembles **Overcooked** and involves preparing and delivering food as efficiently as possible.

---

        return f"""
# **Game Rules & Objective**
- The game features a **Red player (you)** and various interactive elements:
  - **Resource Crate** (Fish) – where you collect raw fish  
  - **Chopping Board** – where fish can be chopped  
  - **Fryer** – where chopped fish can be fried  
  - **Plate Crate** – where plates can be collected  
  - **Conveyor Belt** – where plated fish dishes are delivered to the restaurant  

- **Your goal:**  
  - Prepare **as many fish dishes as possible** in the shortest time.  
  - A valid dish consists of:  
    1. **Chopped Fish** (obtained by chopping raw fish at the chopping board)  
    2. **Fried Fish** (chopped fish must be fried in the fryer)  
    3. **Plated Fish** (fried fish must be placed on a plate before delivery)  

- **Plating Rule:**  
  - You **must** place a plate on a table first before placing the cooked fish on it.  
---

"""
# **Move Structure & Submove List**
Each move must be **decomposed into sub-moves**. These are the only available sub-moves:

1. `Walk_up_to_object(object_name)` – Move towards an interactive object  
2. `Pick_up_resource()` – Pick up a resource (e.g., fish, plate)  
3. `Put_down_resource()` – Place a resource on a surface  
4. `Chop_resource()` – Chop a raw resource (fish)  
5. `Fry_resource()` – Fry a chopped fish  
6. `Grab_resource()` – Take a cooked or prepared item (e.g., fried fish, plated dish)  
7. `Wait()` – Wait for **1 second** (used when waiting for frying to finish)  
"""
# **Names of objects**

When naming different objects, add their name and a correct suffix corresponding to whether it's an object at the top or at the bottom of the map.
For example: "FishCrateTop", "ChoppingBoardBottom", "FryerTop", "PlateCrateTop", "CounterTopTop", "ConveyorBeltTop"

Even though there are many countertops, you can only reference CounterTopTop (a CounterTop to the right of PlateCrateTop) and CounterTopBottom (a CounterTop to the right of PlateCrateBottom)

- **Action Timing:**  
  - `Wait()` always lasts **1 second**.  
  - **Other submoves** take as long as needed for execution.  {self._action_timing}

---

# **Framework for Decision-Making**
Write out your decision-making process clearly to make your job as easy as possible. When choosing the next moves:  

1. **Identify the current state** from the provided image. Where you are based on which player you are? What objects are available around you? Do you have anything in your hand? Are there any resources already placed on the map?
2. **Infer from the current state** the stage of the goal you are in right now. What did you get done? What is left?
3. **Determine the current goal** based on the current state and the stage of the goal you are in right now.
3. **Determine the optimal sequence of moves** to achieve the goal. Remember that to perform an action, you first need to walk up to an appropriate object. Make sure you can move to that object from your current position (e.g. if you are at the top, pick the object at the top, if you are at the bottom, pick the object at the bottom).
4. **Break down the moves** into a sequence of precise sub-moves. When mentioning an object, use the name of the object as mentioned in the "Names of objects" section -- ensure no ambiguity.

'''