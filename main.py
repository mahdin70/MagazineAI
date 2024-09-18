import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from layout import LayoutExtractor

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=openai_api_key)

history = ChatMessageHistory()

layout_extractor = LayoutExtractor("Texract-JSON/MedicalAnalyzeDocResponse.json")

def get_system_message() -> SystemMessage:
    layout_details = layout_extractor.get_layout_details()
    layout_text = layout_extractor.get_text_from_layout()
    
    system_prompt = f"""
    You are an AI assistant that generates magazine content based on user queries. Using the Document Layout Details, you will generate content that matches the layout element types and their word counts.
    
    Ensure the response includes all the necessary layout elements for example: 
    - Layout Title
    - Layout Section Header
    - Layout Text
    
    Strictly, Follow the WORD COUNT for each layout element type and respond accordingly.
    
    Layout Details:
    {layout_details}
    
    Also, Stricly follow the text content extracted from the layout. You need to give content that is relevent to the given layout text and your tone should match the layout text. Don't just copy that layout text. This is for reference only. You need to give a response with new content and more creativity.
    
    Layout Text:
    {layout_text}
    
    Your task is to create relevant magazine content based on these details and the user's query.
    """
    return SystemMessage(content=system_prompt)


def start_chat():                                    
    print("Start chatting with the AI (type 'exit' to stop):")
    
    system_message = get_system_message()
    history.add_message(system_message)
    
    while True:
        user_input = input("User: ")
        if user_input.lower() == 'exit':
            print("Ending chat session.")
            break
        
        start_time = time.time()
        user_message = HumanMessage(content=user_input)
        history.add_message(user_message)
    
        messages = history.messages
        response = llm.invoke(messages)
        end_time = time.time()

        print(f"Magazine-AI: {response.content}")
        history.add_message(response)
        print(f"Time taken: {end_time - start_time:.2f}s")

if __name__ == "__main__":
    start_chat()
