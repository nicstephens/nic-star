from langchain_openai import ChatOpenAI
import graphviz
from langchain.chains.openai_functions import create_openai_fn_runnable
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pydantic_types import *
from prompts.reason_and_act import Reactor
from typing import List, Tuple

load_dotenv()




class Node():

    def __init__(self, task) -> None:
        self.task: str = task
        self.thought_action: str = None
        self.evaluation: Observation = None
        self.previous: Node = None
        self.next: list[Node] = []
        pass


    def get_previous_thought_actions(self) -> list[ReactorUnit]:
        parents: List[ReactorUnit] = []
        current = self
        while current.previous is not None:
            new_thought_action = current.previous.thought_action if current.previous.thought_action else "None"
            new_evaluation = current.previous.evaluation if current.previous.evaluation else Observation(reflection="No reflection given", correctness_score=10)
            parents += [ReactorUnit(thought_action=new_thought_action, evaluation=new_evaluation)]
            current = current.previous
        return parents


    def generate_subtree(self, width: int, depth: int) -> None:
        if depth == 0:
            return

        self.next = []
        for _ in range(width):
            new_node = Node(task=self.task)
            reactor_output = Reactor(self.get_previous_thought_actions(), self.task)
            new_node.thought_action = reactor_output.thought_action
            new_node.evaluation = reactor_output.evaluation
            new_node.previous = self
            self.next.append(new_node)
            new_node.generate_subtree(width, depth - 1)

    
    def bfs(self):
        g = graphviz.Digraph(format='svg')
        g.attr('node', shape='box', fixedsize='false', width='3', height='0', margin='0.2,0.2')
        queue = [(self, id(self))]
        visited = set()

        while queue:
            current_thought, current_id = queue.pop(0)

            if current_id in visited:
                continue

            visited.add(current_id)
            node_label = f"Correctness score: {str(current_thought.evaluation.correctness_score)}"
            g.node(str(current_id), label=node_label)

            if current_thought.next:
                for thought in current_thought.next:
                    thought_id = id(thought)
                    queue.append((thought, thought_id))
                    g.edge(str(current_id), str(thought_id))

        g.view()

    def evaluate(self):
        pass

        
question = "Your goal is create the most visually appealing portfolio website as possible for me. My name is Nic Stephens and I am an AI developer. You have access to my windows command line. Any work you do must be in the C:\\Users\\nicst\\OneDrive\\Documents\\Freelancing\\N-star\\nic-star\\tmp directory."

hello = Node(task=question)
hello.generate_subtree(width=1, depth=10)

hello.bfs()


    
