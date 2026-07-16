"""
Current Goal: Make it work
-- BRO. JUST USE THE FUCKING MCP
-- Change the model to best visual from LLM Arena
-- change the prompt to be more effective

- Make it fast
-- See the syntaxer ratio. Is this a problem?
-- Check where you are at
--- Draw out the entire pipeline and mark the seconds + RPM it takes
-- Minimize the bottlenecks
--- Dynamic LLM -- feed it its past reasoning
--- Detached visual -- brainstorm how to make it work. Potentially active inference?

- Make it cool 
-- Some basic code refactoring
-- Decide what you actually want to do
---How do I connect it to Active Inference?
-- Experiment with different LLMs 
-- Introduce feedback loops
-- Scale to 2 players
-- Scale to a regular level

Iteration #1: Communication
- Scale to a better OvAI level
- Human-AI communication based on that 
- Add voice mode
- Hone until perfection
- AI-AI communication, voice mode at first
Iteration #2: Better executor
- Decide on the better domain
- Connecting LLMs to VLAs?
- Active Inference generative AI?

In the Future:
- add the history of past thoughts to retain self-integrity
- Further down the road: once you change an expert system, (into, say, VLA), it will be different totally too
- Wilder idea: train the whole model on RL?
- Better memory (see below)
"""


"""
Architecture:

-Memory system:
-- Fresh memory: 
straight up what it had before
Goal: understand the current state better.
continuity in reasoning, diagnosing mistakes

-- "Note-to-self"
Goal: understand the environment better
resolving ambiguities, preventing the same mistake from happening again

-- Let it touch all the non-task (i.e. meta-reasoning) parts of the prompt
Goal: understand yourself better
self-improvement, "personality", mindset 

"""

"""
How in the world do I connect this to Active Inference?
- Code AcIn to a nice level independently and see what is missing there
- If it fits nicely, like a jigsaw puzzle, then you'll know perfectly what to dos
"""

