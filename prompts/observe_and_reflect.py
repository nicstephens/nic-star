from pydantic_types import Observation
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains.openai_functions import create_openai_fn_runnable
from langchain_openai import ChatOpenAI


def obs_and_ref(thought_action: str, outcome: str) -> Observation:
    """Evaluate the action taken and the result of the action."""
    formatted_thought_action_observation = f"AI Model Thoughts & Action: {thought_action} \n Outcome of the action: {outcome} "

    llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an AI tasked with evaluating the performance of another AI system that is designed to generate the next step in the chain of thought process where each thought leads to an action (potentially), which then yields a certain result. Given the result of the action you must evaluate the action take by providing an Observation with a reflection (i.e. feedback) and a correctness score that evaluates the performance of the AI model in relation to the action taken. "),
            ("human", "Make a call to the observation function to evaluate the following thought and action: {input}"),
            ("human", "Tip: Make sure to answer in the correct format. And make sure to provide a detailed reflection on the action taken and the result of the action. Do not shorten it for the sake of brevity."),
        ]
    )
    chain = create_openai_fn_runnable([Observation], llm, prompt)

    rez = chain.invoke({"input": formatted_thought_action_observation})
    return rez