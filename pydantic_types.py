from typing import Optional, List
from langchain_core.pydantic_v1 import BaseModel, Field


class Observation(BaseModel):
    """The observation of the state of the environment after the action is taken, recorded as a 'reflection' and 'correctness score' from 0 to 10 which is an evaluation of the correctness of the action taken."""
    reflection: str = Field(..., description="A reflection on the action taken and the result of the action. This should be detailed enough to provide insight into the action taken and the result. Do not shorten it for the sake of brevity.")
    correctness_score: int = Field(..., description="The correctness score of the observation from 0 to 10.")

class ReactorUnit(BaseModel):
    """A unit of the reactor function that generates the next action to take based on the history of the thought process (list of thought-action-observation tuples)."""
    thought_action: str = Field(..., description="The action taken in the thought process.")
    evaluation: Observation = Field(..., description="The evaluation of the action taken and the result of the action.")