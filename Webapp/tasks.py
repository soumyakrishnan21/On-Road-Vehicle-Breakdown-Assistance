# chatbot/tasks.py
from celery import shared_task
from .models import Chat

@shared_task
def get_bot_response(user_question):
    # Simple rule-based logic for demonstration
    if 'hello' in user_question.lower():
        response = 'Hello! How can I help you today?'
    elif 'help' in user_question.lower():
        response = 'Sure, I am here to help you. Please ask your question.'
    else:
        response = 'Sorry, I did not understand that. Can you please rephrase?'

    # Save the chat to the database
    chat = Chat(user_question=user_question, bot_response=response)
    chat.save()

    return response
