import os
import json
from tkinter import filedialog
from docx import Document
from typing import Optional, List, Dict, Callable, Union
import autogen
from autogen import (
    AssistantAgent,
    ConversableAgent,
    UserProxyAgent,
    ChatCompletion,
    Completion,
)
from langchain.document_loaders import (
    UnstructuredHTMLLoader,
    UnstructuredPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
)
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
        "model": "gpt-4",
        "api_key": os.environ.get("OPENAI_API_KEY"),
        "api_type": "open_ai",
        "api_base": "https://api.openai.com/v1",
        "temperature": 0,
        "request_timeout": 300,
        "seed": 1,
    }
]


class MemoryFileLoader:
    """Functions as a wrapper for document loaders from langchain."""

    def choose_file(self):
        """Opens a file dialog to choose a file to load."""
        file_types = [
            ("Word Documents", "*.docx"),
            ("Text Documents", "*.txt"),
            ("JSON Files", "*.json"),
            ("PDF Files", "*.pdf"),
        ]
        self.saved_doc = filedialog.askopenfilename(
            title="Select a file to load",
            filetypes=file_types,
            defaultextension=".txt",
        )
        return self.saved_doc

    def load_docx(self):
        """Loads a docx file."""
        self.docx_loader = UnstructuredWordDocumentLoader(self.saved_doc)
        document2 = self.docx_loader.load()
        for doc in document2:
            doc = document2[0].page_content
        document = ""
        document += doc
        return document

    def load_pdf(self):
        """Loads a pdf file."""
        self.pdf_loader = UnstructuredPDFLoader(self.saved_doc)
        document2 = self.pdf_loader.load()
        for doc in document2:
            doc = document2[0].page_content
        document = ""
        document += doc
        return document


# TODO Potentially add a "filter function" to ensure high-quality llm response.
def spr_compress_using_completion(document: str) -> str:
    """Compresses a document into an SPR using a chat completion."""
    context = [{"role": "system", "content": SPR_GENERATOR_SYS_MSG}]

    completion = ChatCompletion.create(
        context=context, config_list=config_list, prompt=document
    )

    SPR_DOCUMENT = completion.choices[0].message.content
    return SPR_DOCUMENT


def decompress_spr(SPR: str) -> str:
    context = [
        {
            "role": "system",
            "content": SPR_INTERPRETER_SYS_MSG,
        },
        {
            "role": "user",
            "content": SPR,
        },
    ]
    condensed_document = ChatCompletion.create(
        context=context,
        config_list=config_list,
        allow_format_str_template=True,
    )
    return condensed_document


class MemorySPR:
    def __init__(self):
        self.document_loader = MemoryFileLoader()

    def _load_document(self) -> str:
        """Loads a document from a file."""
        memory_file_loader = MemoryFileLoader()
        document = memory_file_loader.choose_file()
        if document.endswith(".docx"):
            document = memory_file_loader.load_docx()
        elif document.endswith(".pdf"):
            document = memory_file_loader.load_pdf()
        elif document.endswith(".txt"):
            document = memory_file_loader.load_txt()
        elif document.endswith(".xlsx"):
            document = memory_file_loader.load_xlsx()
        return document

    def generate_spr(self):
        """Compresses a document into an SPR using chat completion from autogen"""
        document = self._load_document()
        context = [{"role": "system", "content": SPR_GENERATOR_SYS_MSG}]
        completion = ChatCompletion.create(
            context=context, config_list=config_list, prompt=document
        )
        document_spr = completion.choices[0].message.content
        return document_spr

    def decompress_spr(SPR: str) -> str:
        context = [
            {
                "role": "system",
                "content": SPR_INTERPRETER_SYS_MSG,
            },
            {
                "role": "user",
                "content": SPR,
            },
        ]
        interpreted_document = ChatCompletion.create(
            context=context,
            config_list=config_list,
            allow_format_str_template=True,
        )
        return interpreted_document

    # TODO Complete a more permanent memory store for SPR (vector database)
    def save_spr_to_memory_file(
        file_path,
        spr_document: Optional[str] = None,
        interpreted_document: Optional[str] = None,
    ):
        """Saves an SPR to a memory file."""


def main():
    memory = MemorySPR()
    spr = memory.generate_spr()
    interpreted_spr = memory.decompress_spr(spr)
    print(interpreted_spr)
    return


if __name__ == "__main__":
    main()
