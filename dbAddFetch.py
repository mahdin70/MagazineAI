import os
import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client['MagazineAIChatDatabase'] 
chat_collection = db['ChatHistory']


def append_message(role, content):
    conversation = chat_collection.find_one()

    if conversation:
        chat_collection.update_one(
            {'_id': conversation['_id']},
            {'$push': {'messages': {'role': role, 'content': content, 'timestamp': datetime.datetime.now()}},
             '$set': {'updatedAt': datetime.datetime.now()}}
        )
    else:
       chat_collection.insert_one({
            'messages': [{'role': role, 'content': content, 'timestamp': datetime.datetime.now()}],
            'createdAt': datetime.datetime.now(),
            'updatedAt': datetime.datetime.now()
        })

def fetch_previous_context():
    conversation = chat_collection.find_one()
    if conversation:
        return conversation['messages']
    return []