# core/llm.py
import os

from langchain_openai import ChatOpenAI
from functools import lru_cache


class LLMSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ChatOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o", temperature=0
            )
        return cls._instance


# Get cached LLM instance
get_llm = lru_cache(maxsize=1)(LLMSingleton.get_instance)

