from .thread_manager import APIThreadManager
from .looper_methods import LooperMethods
from .PromptBase import PromptBaseClass

class Looper:
    '''
    Wrapper for policies. Uses looper_methods and a thread manager
    '''
    def __init__(self, grammar_function, player="Player1"):
        self.thread_manager = APIThreadManager()
        self.max_threads = 1
        self.policy = [("wait", None) for _ in range(5)]
        self.grammar_function = grammar_function
        self.player = player
        self.prompt_base = PromptBaseClass(player=player)
        self.methods = LooperMethods(prompt_base=self.prompt_base)
        self.pipeline = {
            "Reasoner": (None, "Executor"), #The function is given at the start of the thread instead
            "Executor": (self.methods.executor, "SyntaxChecker"),
            "SyntaxChecker": (lambda input: self.methods.syntaxer(input=input, grammar_function=self.grammar_function), None),
        }
        self.debug_tick = 0

    def set_player(self, player):
        self.player = player
        self.prompt_base.player = player.__class__.__name__

    def update_agent(self, image):
        if self.thread_manager.threads_number < self.max_threads:
            self.thread_manager.add_thread(lambda img: self.methods.reason(remaining_actions=self.policy, current_image=image), "Reasoner", image)

        # Create a list of completed threads first
        completed_threads = []
        for thread in self.thread_manager.threads.values():
            if thread.future.done():
                completed_threads.append(thread)

        # Process completed threads after iteration
        for thread in completed_threads:
            self.thread_manager.remove_thread(thread)
            result = thread.future.result()
            self._process_result(thread_type=thread.type, result=result)

    def _process_result(self, thread_type, result):
        '''
        Find thread.type in self.pipeline 
        Find the next index
        Call that function with the result
        '''
        _, next_type = self.pipeline[thread_type]
        if next_type == None:
            if result is not None:
                self.policy = result
                while len(self.policy) < 10:
                    self.policy.append(("wait", None))
        else:
            next_function, _ = self.pipeline[next_type]
            print("FINISHED WITH: ", thread_type, ".    ADDING THREAD: ", next_type)
            self.thread_manager.add_thread(next_function, next_type, result)
    
    def get_policy(self):
        policy_name, policy_args = self.policy[0]
        return policy_name, policy_args
    
    def new_policy(self):
        self.policy.pop(0)
        self.policy.append(("wait", None))