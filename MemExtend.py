import os
import json
from tkinter import filedialog
from docx import Document
from typing import Optional, List, Dict, Callable, Union 
import autogen
from autogen import AssistantAgent, ConversableAgent, UserProxyAgent, ChatCompletion, Completion
from langchain.document_loaders import UnstructuredHTMLLoader, UnstructuredPDFLoader, UnstructuredWordDocumentLoader, UnstructuredExcelLoader
from src.prompts import SPR_GENERATOR_SYS_MSG, SPR_INTERPRETER_SYS_MSG

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

config_list = [
        {
            "model": "gpt-3.5-turbo",
            "api_key": os.environ.get("OPENAI_API_KEY"),
            "api_type": "open_ai",
            "api_base": "https://api.openai.com/v1",
            "temperature": 0,
            "request_timeout": 300,
        },
       {
            "model": "gpt-4",
            "api_key": os.environ.get("OPENAI_API_KEY"),
            "api_type": "open_ai",
            "api_base": "https://api.openai.com/v1",
            "temperature": 0,
            "request_timeout": 300,
 
        }
       ]

class MemoryFileLoader:
    """Functions as a wrapper for document loaders from langchain."""
    def __init__(self, docx_loader, txt_loader, json_loader):
        self.docx_loader = docx_loader
        self.txt_loader = txt_loader 
        self.json_loader = json_loader
    
    def choose_file(self):
        """Opens a file dialog to choose a file to load."""
        file_types = [
            ("Word Documents", "*.docx"),
            ("Text Documents", "*.txt"),
            ("JSON Files", "*.json"),
            ]
        saved_doc = filedialog.askopenfilename(
                title="Select a file to load",
                filetypes=file_types,
                defaultextension=".txt",
            )
        return saved_doc
    
    def load_docx(self):
        """Loads a docx file."""
        self.docx_loader = UnstructuredWordDocumentLoader(self.saved_doc)
        document = self.docx_loader.load()
        return document
    
    def load_xlsx(self):
        """Loads a xlsx file."""
        self.xlsx_loader = UnstructuredExcelLoader(self.saved_doc)
        document = self.xlsx_loader.load()
        return document

    def load_pdf(self):
        """Loads a pdf file."""
        self.pdf_loader = UnstructuredPDFLoader(self.saved_doc)
        document = self.pdf_loader.load()
        return document
    
    def load_website(self):
        """
        Loads text from a website
        """
        url = input("Enter a valid HTML URL Address\n> ")
        self.txt_loader = UnstructuredHTMLLoader(url)
        document = self.txt_loader.load()
        return document

    def load_json(self):
        """Loads a json file."""
        self.json_loader = json.load(self.saved_doc)
        document = self.json_loader.load()
        return document

context = {"role": "system","content": SPR_GENERATOR_SYS_MSG  }

#  This version utilizes an agent instead of a chat completion
def spr_compress(prompt: str, document: str, llm_config: Dict = gpt3, **kwargs):
    """Compresses a document into an SPR.""" 
    spr_agent = SprGeneratorAgent(llm_config=llm_config)
    user = autogen.UserProxyAgent(
        name="USER",
        human_input_mode="NEVER",
        code_execution_config={},
        default_auto_reply="If the document has not been compressed to SPR format, please inform me and try again."
        max_consecutive_auto_reply=3 
    )
    compressed_document = user.initiate_chat(spr_agent, messages=document) 
    return compressed_document
    
 # TODO Potentially add a "filter function" to ensure high-quality llm response. 
def spr_compress_using_completion(document:str, llm_config: Dict=gpt4)->str:
    """Compresses a document into an SPR using a chat completion."""
    context = [
        {
            "role": "system", "content": SPR_GENERATOR_SYS_MSG,
        },
        {
            "role": "user", "content": document,
        },
    ]
    completion = ChatCompletion.create(
        context=context,
        config_list=config_list,
        allow_format_str_template=True,
        prompt=document 
    )

    SPR_DOCUMENT = completion.choices[0].message.content
    return SPR_DOCUMENT 
    
def decompress_spr (SPR :str, llm_config_list: List[Dict] = config_list):
     context = [
        {
            "role": "system", "content": SPR_INTERPRETER_SYS_MSG,
        },
        {
            "role": "user", "content": SPR,
        },
    ]
     condensed_document = ChatCompletion.create(
        context=context,
        config_list=config_list,
        allow_format_str_template=True,
    )
     return condensed_document 


