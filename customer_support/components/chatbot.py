### chatbot/components/chatbot.py ###

from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from typing import List
from ..models import ChatMessage


class Chatbot:
    """
    Chatbot component for handling Crustdata API support conversations.
    """

    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        self.chat_model = ChatOpenAI(
            temperature=temperature,
            model_name=model_name
        )
        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        """
        Define the system prompt for the chatbot.
        """
        return """You are a helpful customer support agent for Crustdata's APIs. 
        Your role is to assist users with technical questions about the APIs.

        Key information about the APIs:
        1. The main endpoints are:
           - /screener/person/search for searching people
           - /search/enrichment for enriching data
        2. The API requires proper authentication using a token
        3. Region values must match specific formats from the provided list

        Always:
        - Provide clear, accurate technical information
        - Include example API calls when relevant
        - Explain any error messages
        - Suggest best practices
        - Be concise but thorough

        If you don't know something, admit it and suggest contacting Crustdata support directly."""

    def _format_chat_history(self, messages: List[ChatMessage]) -> List[dict]:
        """
        Format chat history into a format suitable for the language model.

        Args:
            messages: List of ChatMessage objects from the database

        Returns:
            List of formatted messages for the language model
        """
        formatted_messages = [SystemMessage(content=self.system_prompt)]

        for msg in messages:
            if msg.role == 'user':
                formatted_messages.append(HumanMessage(content=msg.content))

        return formatted_messages

    def generate_response(self, chat_history: List[ChatMessage]) -> str:
        """
        Generate a response based on chat history.

        Args:
            chat_history: List of ChatMessage objects representing the conversation

        Returns:
            str: Generated response from the chatbot

        Raises:
            Exception: If there's an error generating the response
        """
        try:
            # Format messages for the model
            formatted_messages = self._format_chat_history(chat_history)

            # Generate response
            response = self.chat_model(formatted_messages)

            return response.content

        except Exception as e:
            # Log error here if needed
            raise Exception(f"Error generating chatbot response: {str(e)}")

    def handle_api_specific_queries(self, content: str) -> str:
        """
        Handle specific API-related queries with predefined responses.
        This method can be expanded to handle common API questions.

        Args:
            content: The user's query

        Returns:
            str: Response for specific API queries, or None if no match
        """
        # Example of handling specific API queries
        api_responses = {
            "region values": """
            You can find the complete list of supported regions at:
            https://crustdata-docs-region-json.s3.us-east-2.amazonaws.com/updated_regions.json

            Make sure to use the exact region names from this list in your API calls.
            """,
            "authentication": """
            All API calls require authentication using a token in the Authorization header:

            --header 'Authorization: Token YOUR_API_TOKEN'

            Contact Crustdata support to obtain your API token.
            """
        }

        # Check if the query matches any predefined responses
        for key, response in api_responses.items():
            if key.lower() in content.lower():
                return response

        return None

    def validate_api_request(self, request_content: str) -> dict:
        """
        Validate API request examples before sending them to users.
        This method can be expanded to include more validation logic.

        Args:
            request_content: The API request example to validate

        Returns:
            dict: Validation result with status and any errors
        """
        required_fields = {
            '/screener/person/search': ['filters', 'page'],
            '/search/enrichment': ['email']
        }

        validation_result = {
            'is_valid': True,
            'errors': []
        }

        # Basic validation logic - can be expanded
        for endpoint, fields in required_fields.items():
            if endpoint in request_content:
                for field in fields:
                    if field not in request_content:
                        validation_result['is_valid'] = False
                        validation_result['errors'].append(
                            f"Missing required field '{field}' for {endpoint}"
                        )

        return validation_result