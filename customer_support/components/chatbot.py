# chatbot.py
from langchain.schema import SystemMessage, HumanMessage
from utils.llm import get_llm
from .prompts import SystemPrompts

class Chatbot:
    def __init__(self, prompt_type: SystemPrompts = SystemPrompts.CRUSTDATA_SUPPORT):
        self.llm = get_llm()
        self.system_prompt = prompt_type.value

    def generate_response(self, messages) -> str:
        try:
            formatted_messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=messages[0].content)
            ]
            response = self.llm.invoke(formatted_messages)
            return response.content
        except Exception as e:
            raise Exception(f"Error generating chatbot response: {str(e)}")