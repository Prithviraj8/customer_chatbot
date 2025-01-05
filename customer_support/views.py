from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from .utils import get_chatbot_response


class ChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling chat interactions.
    Provides CRUD operations for chat messages and bot interactions.
    """
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    def get_session_id(self, request):
        """Get or create a session ID for the current user."""
        if not request.session.session_key:
            request.session.create()
        return request.session.session_key

    def get_chat_history(self, session_id, limit=10):
        """Retrieve chat history for the current session."""
        return ChatMessage.objects.filter(
            session_id=session_id
        ).order_by('-timestamp')[:limit]

    @action(detail=False, methods=['GET'])
    def chat_page(self, request):
        """Render the chat interface."""
        return render(request, 'chatbot/chat.html')

    @action(detail=False, methods=['GET'])
    def history(self, request):
        """
        Retrieve chat history for the current session.
        """
        session_id = self.get_session_id(request)
        messages = self.get_chat_history(session_id)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def send_message(self, request):
        """
        Process a new message and get response from the chatbot.
        """
        try:
            # Get session ID
            session_id = self.get_session_id(request)

            # Get message from request
            message = request.data.get('message')
            if not message:
                return Response(
                    {'error': 'Message is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save user message
            user_message = ChatMessage.objects.create(
                role='user',
                content=message,
                session_id=session_id
            )

            # Get chat history for context
            chat_history = self.get_chat_history(session_id)

            # Get response from chatbot
            bot_response = get_chatbot_response(chat_history)

            # Save bot response
            assistant_message = ChatMessage.objects.create(
                role='assistant',
                content=bot_response,
                session_id=session_id
            )

            # Prepare response data
            response_data = {
                'user_message': self.get_serializer(user_message).data,
                'bot_response': self.get_serializer(assistant_message).data
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['DELETE'])
    def clear_history(self, request):
        """
        Clear chat history for the current session.
        """
        session_id = self.get_session_id(request)
        ChatMessage.objects.filter(session_id=session_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        """
        Override create method to automatically set session_id.
        """
        request.data['session_id'] = self.get_session_id(request)
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Override list method to only return messages from current session.
        """
        self.queryset = self.queryset.filter(
            session_id=self.get_session_id(request)
        )
        return super().list(request, *args, **kwargs)