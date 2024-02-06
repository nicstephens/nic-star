from typing import List, Tuple
from pydantic_types import Observation, ReactorUnit
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import AIMessage, HumanMessage
import os
from prompts.observe_and_reflect import obs_and_ref
import subprocess
import json


class FileWrite(BaseModel):
    file_path: str = Field(
        description="Should be a file path that is accessible from the current environment.")
    file_text: str = Field(
        description="The text to write to the file.")
    
class FileRead(BaseModel):
    file_path: str = Field(
        description="Should be a file path that is accessible from the current environment.")
    
class WindowsCommand(BaseModel):
    command: str = Field(
        description="The command to run on the Windows operating system.")


@tool("read_file", args_schema=FileRead, return_direct=True)
def read_file(file_path: FileRead) -> str:
    """Read a file from the file system."""
    with open(file_path, "r") as file:
        return file.read()
    


@tool("write_file", args_schema=FileWrite, return_direct=True)
def write_file(file_path: str, file_text: str) -> str:
    """Write to a file in the file system."""
    with open(file_path, "w") as file:
        file.write(file_text)
    return "Successfully written to file."


@tool("run_windows_command", args_schema=WindowsCommand, return_direct=True)
def run_code(command: str) -> str:
    """Run a command and get the result."""

    try:
        result = subprocess.run(command, shell=True, text=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout or "Command ran successfully."
    except subprocess.CalledProcessError as e:
        return f"Command failed with exit code {e.returncode}:\n{e.stderr}"
    except Exception as e:
        return f"Error running command: {e}"



def Reactor(parent_nodes: List[ReactorUnit], task: str) -> ReactorUnit:
    """Generate the next action to take based on the history of the thought process (list of thought-action-observation tuples)."""

    tools = [run_code, read_file, write_file]
    prompt = hub.pull("hwchase17/structured-chat-agent")
    llm = ChatOpenAI(temperature=0, model="gpt-4-turbo-preview")
    agent = create_structured_chat_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, return_intermediate_steps=True
    )

    message_history = [HumanMessage(content=task)]

    # loop through parent nodes from the second entry to the last entry

    for elem in parent_nodes:
        print (type(elem), ' ', elem)
        message_history.append(AIMessage(content=elem.thought_action))
        message_history.append(HumanMessage(content=elem.evaluation.reflection))

    result = agent_executor.invoke(
        {
            "input": "Continue in your pursuit of the original task which was to: " + task,
            "chat_history": message_history,
        }
    )

    thought_action: str = result["intermediate_steps"][-1][0].log

    obs = obs_and_ref(thought_action, result["intermediate_steps"][-1][1])

    return ReactorUnit(thought_action=thought_action, evaluation=obs)
