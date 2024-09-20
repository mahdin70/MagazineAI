import os
import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from extractLayout import LayoutExtractor

load_dotenv()

# MongoDB connection setup
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client['MagazineAIChatDatabase'] 
chat_collection = db['ChatHistory']

# Initialize the layout extractor
layout_extractor = LayoutExtractor("Texract-JSON/MedicalAnalyzeDocResponse.json")
layout_details = layout_extractor.get_layout_details()  # Get layout details from layout extractor
layout_text = layout_extractor.get_text_from_layout()   # Get text from layout

def append_message(role, content):
    # Fetch the existing conversation
    conversation = chat_collection.find_one()

    if conversation:
        # Update only the latest user/AI message
        if role == 'user':
            chat_collection.update_one(
                {'_id': conversation['_id']},
                {'$set': {
                    'latest_user_message': {'role': role, 'content': content, 'timestamp': datetime.datetime.now()},
                    'updatedAt': datetime.datetime.now()
                }}
            )
        elif role == 'ai':
            # Check if the first AI reply exists and insert it if not already present
            if not conversation.get('first_ai_reply'):
                chat_collection.update_one(
                    {'_id': conversation['_id']},
                    {'$set': {
                        'first_ai_reply': {'role': role, 'content': content, 'timestamp': datetime.datetime.now()},
                        'latest_ai_reply': {'role': role, 'content': content, 'timestamp': datetime.datetime.now()},
                        'updatedAt': datetime.datetime.now()
                    }}
                )
            else:
                # Just update the latest AI message
                chat_collection.update_one(
                    {'_id': conversation['_id']},
                    {'$set': {
                        'latest_ai_reply': {'role': role, 'content': content, 'timestamp': datetime.datetime.now()},
                        'updatedAt': datetime.datetime.now()
                    }}
                )
    else:
        # Insert both first user message and AI reply when the conversation is created
        if role == 'user':
            chat_collection.insert_one({
                'first_user_message': {'role': 'user', 'content': content, 'timestamp': datetime.datetime.now()},
                'latest_user_message': {'role': 'user', 'content': content, 'timestamp': datetime.datetime.now()},
                'layout_details': layout_details,
                'layout_text': layout_text,
                'createdAt': datetime.datetime.now(),
                'updatedAt': datetime.datetime.now()
            })
        elif role == 'ai':
            # Insert conversation with the first AI message if this is the first AI reply
            chat_collection.insert_one({
                'first_ai_reply': {'role': 'ai', 'content': content, 'timestamp': datetime.datetime.now()},
                'latest_ai_reply': {'role': 'ai', 'content': content, 'timestamp': datetime.datetime.now()},
                'createdAt': datetime.datetime.now(),
                'updatedAt': datetime.datetime.now()
            })


def fetch_previous_context():
    conversation = chat_collection.find_one()  # Find the conversation from the collection
    
    if conversation:
        # Return the layout details, first user prompt, first AI reply, and the latest user prompt-AI reply pair
        return {
            'first_user_message': conversation.get('first_user_message', {}),
            'first_ai_reply': conversation.get('first_ai_reply', {}),
            'latest_thread': {
                'user_message': conversation.get('latest_user_message', {}),
                'ai_reply': conversation.get('latest_ai_reply', {})
            }
        }
    return {}
