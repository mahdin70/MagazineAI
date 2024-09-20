import os
import time
import threading
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from dbAddFetch import append_message, fetch_previous_context
from systemMessage import get_system_message

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=openai_api_key)
history = ChatMessageHistory()

stop_loader = False
     
def loader_animation():
    while not stop_loader:
        for symbol in '|/-\\':
            print(f'\rGenerating the Response {symbol}', end='', flush=True)
            time.sleep(0.1)

def start_chat():
    # Fetch the previous context (latest thread with layout and first messages)
    previous_context = fetch_previous_context()

    # Extract the latest thread (latest user message and AI reply)
    latest_thread = previous_context.get('latest_thread', {})
    first_user_message = previous_context.get('first_user_message', {})
    first_ai_reply = previous_context.get('first_ai_reply', {})
    
    # Print the latest thread (user message and AI reply)
    latest_user_message = latest_thread.get('user_message', {})
    latest_ai_reply = latest_thread.get('ai_reply', {})
    
    if latest_user_message:
        print(f"User: {latest_user_message.get('content', '')}")
    
    if latest_ai_reply:
        print(f"AI: {latest_ai_reply.get('content', '')}")
    
    print("================================================================================================") 
    print("Start chatting with the AI (type 'exit' to stop):")
    
    system_message = get_system_message()
    history.add_message(system_message)
        
    # Add previous messages to the langchain message history
    history.add_message(HumanMessage(content= latest_user_message.get('content', '')))
    history.add_message(AIMessage(content= latest_ai_reply.get('content', '')))

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
        
        content = response.content
        token_usage = response.usage_metadata

        print(f"\rMagazine-AI: {content}")

        history.add_message(AIMessage(content=content))

        # Store the first user message and first AI reply if not already stored
        if not first_user_message:
            append_message('user', user_input)
        if not first_ai_reply:
            append_message('ai', content)

        # Update the latest user message and AI reply
        append_message('user', user_input)
        append_message('ai', content)
        
        print("================================================================================================")
        print(f"Time taken: {elapsed_time:.2f}s")
        print(f"Input Tokens: {token_usage['input_tokens']}")
        print(f"Output Tokens: {token_usage['output_tokens']}")
        print(f"Total Tokens: {token_usage['total_tokens']}")

if __name__ == "__main__":
    start_chat()