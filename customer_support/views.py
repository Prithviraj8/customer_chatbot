from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.utility_functions import format_response
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from .components.chatbot import Chatbot
from .components.prompts import SystemPrompts


class ChatViewSet(APIView):
    """
    ViewSet for handling chat interactions.
    """
    serializer_class = ChatMessageSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chatbot = Chatbot(prompt_type=SystemPrompts.CRUSTDATA_SUPPORT)

    def get_session_id(self, request):
        if not request.session.session_key:
            request.session.create()
        return request.session.session_key

    def post(self, request):
        try:
            session_id = self.get_session_id(request)
            message = request.data.get('message')

            if not message:
                return Response(
                    {'error': 'Message is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user_message = ChatMessage.objects.create(
                role='user',
                content=message,
                session_id=session_id
            )

            bot_response = self.chatbot.generate_response([user_message])

            assistant_message = ChatMessage.objects.create(
                role='assistant',
                content=bot_response,
                session_id=session_id
            )

            response_data = {
                'user_message': self.serializer_class(user_message).data,
                'bot_response': self.serializer_class(assistant_message).data
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )