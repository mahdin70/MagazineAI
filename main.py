import datetime
import os
import time
import threading
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from layout import LayoutExtractor
from pymongo import MongoClient

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client['MagazineAIChatDatabase'] 
chat_collection = db['ChatHistory']

openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=openai_api_key)

history = ChatMessageHistory()
stop_loader = False

layout_extractor = LayoutExtractor("Texract-JSON/MedicalAnalyzeDocResponse.json")

def get_system_message() -> SystemMessage:
    layout_details = layout_extractor.get_layout_details()
    layout_text = layout_extractor.get_text_from_layout()
    
    system_prompt = f"""
    You are a highly creative AI assistant tasked with generating engaging, relevant, and well-structured magazine content based on the provided layout details and user queries.
    
    **Instructions**:
    1. **Content Structure**: Use the provided document layout to ensure the magazine content follows the appropriate structure. For example:
       - Layout Header
       - Layout Title
       - Layout Section Header
       - Layout Text
       - Layout Footer
    
    2. **Word Count**: Strictly adhere to the word count for each layout element type. For instance:
       - Titles should be concise, within the specified limit.
       - Section headers should be informative but brief.
       - Text sections should be comprehensive yet aligned with the word count constraints.
    
    3. **Content Tone & Style**:
       - The tone of the response should match the extracted layout text's intended style.
       - Feel free to be creative, but always keep the content relevant to the theme suggested by the layout.
       - Avoid simply copying the provided text; instead, create new content that is inspired by the layout text and meets user intent.

    4. **User's Query**: Base your content on the users query, ensuring the response is aligned with their needs while following the layout structure.
    
    **Document Layout Details**:
    {layout_details}
    
    **Extracted Layout Text**:
    The following text was extracted from the provided document layout. Use this as a reference to guide your tone, style, and overall structure, but generate new and creative content based on these themes:
    {layout_text}
    
    **Your Task**: Generate high-quality, creative magazine content that adheres to the layout structure and constraints. The content must match the users query, maintain the specified tone, and stay within the word count limits for each section.
    """
    return SystemMessage(content=system_prompt)

     
def loader_animation():
    while not stop_loader:
        for symbol in '|/-\\':
            print(f'\rGenerating the Response {symbol}', end='', flush=True)
            time.sleep(0.1)

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

def start_chat():
    previous_context = fetch_previous_context()
    for item in previous_context:
        print(f"{item['role'].capitalize()}: {item['content']}")
        
    history.add_messages(previous_context)
    
    print("Start chatting with the AI (type 'exit' to stop):")
    
    system_message = get_system_message()
    history.add_message(system_message)

    global stop_loader
    stop_loader = False
    
    while True:
        user_input = input("User: ")
        if user_input.lower() == 'exit':
            print("Ending chat session.")
            break
        
        start_time = time.time()
        stop_loader = False
        loader_thread = threading.Thread(target=loader_animation)
        loader_thread.start()
        
        user_message = HumanMessage(content=user_input)
        history.add_message(user_message)

        messages = history.messages
        
        response = llm.invoke(messages)
        
        stop_loader = True
        loader_thread.join()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"\rMagazine-AI: {response.content}")
        history.add_message(response)

        append_message('user', user_input)
        append_message('ai', response.content)
        
        print(f"Time taken: {elapsed_time:.2f}s")

if __name__ == "__main__":
    start_chat()