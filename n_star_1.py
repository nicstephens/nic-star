
import random
from langchain_openai import ChatOpenAI
import graphviz
from langchain.prompts import PromptTemplate
from langchain.chains.openai_functions import create_openai_fn_runnable
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Optional

class NextStep(BaseModel):
    """Record some identifying information about a person."""

    next_thought: Optional[str] = Field(None, description="The next logical reasoning step in the chain of thoughts")
    final_answer: Optional[str] = Field(None, description="The final answer or solutions to the task given.")



def generate_next_step(question: str, chain_of_thought: str | None) -> NextStep:
    if chain_of_thought == None:
        chain_of_thought = 'None so far - please start start off with your first thought.'
    else:
        LLM = ChatOpenAI(api_key="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")
        thought_generation_prompt = ChatPromptTemplate.from_template(
            """You are an AI that thinks step-by-step before providing answers to thwe questions or tasks you are given. You have been given the following question: {question}. 
In answering the question, you are thinking step by step to arrive at the answer. These are your thoughts so far:
{chain_of_thought}
Now, you have two options: Provide an additional thought step to get you closer to the answer, or conclude the chain of thought by providing the final answer. """
        )
        
        chain = create_openai_fn_runnable([NextStep], LLM, thought_generation_prompt)
        response = chain.invoke({"question":question, "chain_of_thought": chain_of_thought})

        return response




class Thought():

    def __init__(self, base_question) -> None:
        self.previous: Thought = None
        self.next: list(Thought) = None
        self.current: str = None
        self.score: int = None
        self.base_question: str = base_question
        pass


    def get_previous_thoughts(self):
        parents = ""
        current = self
        while current.previous is not None:
            parents = "Thought:" + current.previous.current + "\n" + parents
            current = current.previous
        return parents.strip()

    def generate_subtree(self, width: int, depth: int) -> None:
        if depth == 0:
            return

        self.next = []
        for _ in range(width):
            new_thought = Thought(base_question=self.base_question)
            next_step = generate_next_step(self.base_question, self.get_previous_thoughts())
            if next_step.next_thought != None :
                new_thought.current = next_step.next_thought
                new_thought.previous = self
                self.next.append(new_thought)
                new_thought.generate_subtree(width, depth - 1)
            if next_step.final_answer != None:
                new_thought.current = next_step.final_answer
                new_thought.previous = self

    
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
            node_label = f"{current_thought.current[:500]}..." if len(current_thought.current) > 500 else current_thought.current
            g.node(str(current_id), label=node_label)

            if current_thought.next:
                for thought in current_thought.next:
                    thought_id = id(thought)
                    queue.append((thought, thought_id))
                    g.edge(str(current_id), str(thought_id))

        g.view()

    def evaluate(self):
        pass

        

    





question = "Create a python script that implements a simple MPL Neural Net to predict stock prices."

hello = Thought(base_question=question)
hello.current = question
hello.generate_subtree(width=1, depth=20)

hello.bfs()


    
