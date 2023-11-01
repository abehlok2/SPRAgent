import os 
import json
from tkinter import filedialog
from docx import Document
from typing import Optional, List, Dict, Callable, Union 
import autogen
from autogen import AssistantAgent, ConversableAgent, UserProxyAgent, ChatCompletion
from langchain.document_loaders import PyPDF2Loader, AsyncHtmlLoader, JSONLoader, DocxLoader, TextLoader

# TODO: add methods to add text to the SPR 
# TODO: add methods to load conversation history



gpt3 = {
    "api_key": os.environ["OPENAI_API_KEY"],
    "model": "gpt-3.5-turbo-16k",
    "temperature": 0,
    "request_timeout": 300,
}
gpt4 = {
    "api_key": os.environ["OPENAI_API_KEY"],
    "model": "gpt-4",
    "temperature": 0,
    "request_timeout": 500,
}

class SprGeneratorAgent(ConversableAgent):

    SPR_GENERATOR_SYS_MSG = """
    # MISSION
    You are a Sparse Priming Representation (SPR) writer. An SPR is a particular kind of use of language for advanced NLP, NLU, and NLG tasks, particularly useful for the latest generation of Large Language Models (LLMs). You will be given information by the USER which you are to render as an SPR.

    # THEORY
    LLMs are a kind of deep neural network. They have been demonstrated to embed knowledge, abilities, and concepts, ranging from reasoning to planning, and even to theory of mind. These are called latent abilities and latent content, collectively referred to as latent space. The latent space of an LLM can be activated with the correct series of words as inputs, which will create a useful internal state of the neural network. This is not unlike how the right shorthand cues can prime a human mind to think in a certain way. Like human minds, LLMs are associative, meaning you only need to use the correct associations to "prime" another model to think in the same way.

    # METHODOLOGY
    Render the input as a distilled list of succinct statements, assertions, associations, concepts, analogies, and metaphors. The idea is to capture as much, conceptually, as possible but with as few words as possible. Write it in a way that makes sense to you, as the future audience will be another language model, not a human.
    """

    def __init__(
        self,
        name: str = "Sparse_Priming_Representation_Generator",
        system_message: str = SPR_GENERATOR_SYS_MSG,
        human_input_mode: Optional[str] = "NEVER",
        llm_config: Dict = Optional[gpt3],
        max_consecutive_auto_reply: Optional[int] = 2,
        **kwargs
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            human_input_mode=human_input_mode,
            max_consecutive_auto_reply,
            llm_config,
            **kwargs
            )
        

class SprInterpreterAgent(ConversableAgent):
    SPR_INTERPRETER_SYS_MSG = """
    # MISSION
    You are a Sparse Priming Representation (SPR) decompressor. An SPR is a particular kind of use of language for advanced NLP, NLU, and NLG tasks, particularly useful for the latest generation of Large Language Models (LLMs). You will be given an SPR and your job is to fully unpack it.

    # THEORY
    LLMs are a kind of deep neural network. They have been demonstrated to embed knowledge, abilities, and concepts, ranging from reasoning to planning, and even to theory of mind. These are called latent abilities and latent content, collectively referred to as latent space. The latent space of an LLM can be activated with the correct series of words as inputs, which will create a useful internal state of the neural network. This is not unlike how the right shorthand cues can prime a human mind to think in a certain way. Like human minds, LLMs are associative, meaning you only need to use the correct associations to "prime" another model to think in the same way.

    # METHODOLOGY
    Use the primings given to you to fully unpack and articulate the concept. Talk through every aspect, impute what's missing, and use your ability to perform inference and reasoning to fully elucidate this concept. Your output should be in the form of the original article, document, or material.
    """

    def __init__(
        self,
        name: str = "Sparse_Priming_Representation_Interpreter",
        system_message: str = SPR_INTERPRETER_SYS_MSG,
        human_input_mode: Optional[str] = "NEVER",
        llm_config: Dict = gpt3,
        max_consecutive_auto_reply: Optional[int] = 2,
        **kwargs
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            human_input_mode=human_input_mode,
            llm_config,
            max_consecutive_auto_reply,
            **kwargs
            )


def open_files():

    file_types = [
        ("Word Documents", "*.docx"),
        ("Text Documents", "*.txt"),
        ("JSON Files", "*.json"),
        ]
        saved_doc = filedialog.askopenfile(
            title="Select a file to load",
            filetypes=file_types,
            defaultextension=".txt",
        )
    return saved_doc

def prepare_completion(system_message: str, request: str):
    setup_messages = [
        {
        "role": "system",
        "content": system_message, 
        },
        {
            "role": "user",
            "content": request,
        },
    ]
    return setup_messages 

def pack_documents (model: str = "gpt-3.5-turbo", context: Dict[str, str], prompt: str):
    config_list = [
        {
            "model": model,
            "api_key": os.environ["OPENAI_API_KEY"],
            "temperature": 0,
            "request_timeout": 300,
        },
        {
            "model": "gpt-3.5-turbo",
            "api_key": os.environ.get("OPENAI_API_KEY"),
            "api_type": "open_ai",
            "api_base": "https://api.openai.com/v1",
        },
       {
            "model": "gpt-3.5-turbo",
            "api_key": os.environ.get("OPENAI_API_KEY"),
            "api_type": "open_ai",
            "api_base": "https://api.openai.com/v1",
        }
       ]
    print("Packing documents...")


        #TODO fix this so that it works as SPR compressor/decompressor instead of just a chat completion. 
    completion = ChatCompletion.create(
        context=prepare_completion(),
        config_list=config_list,
        allow_format_str_template=True,
        prompt=prompt
    )
    if completion:
        return completion
    else:
        return "ERROR"

        
               

    
    
    
