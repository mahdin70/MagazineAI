import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from layout import LayoutExtractor

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=openai_api_key)

history = ChatMessageHistory()

layout_extractor = LayoutExtractor("Texract-JSON/TestanalyzeDocResponse.json")

def compose_prompt(user_input: str) -> str:
    layout_details = layout_extractor.get_layout_details()
    prompt = f"""
    You are an AI assistant that genrates magazine content based on user queries. Using the Document Layout Details you will generate real content that matches the layout element types and their word counts. In the response you need to provide Layout Title, Layout Section Header, and Layout Text based on the provided layout details while strictly following the word count for each layout element type.

    Layout Details and the Word Counts Follow the same format and structure in your response:
    {layout_details}

    User's Query:
    {user_input}

    Please respond based on the provided layout details and make sure your response is informative and helpful. Give relevant content based on the input query and the layout details.
    """
    return prompt

def start_chat():                                    
    print("Start chatting with the AI (type 'exit' to stop):")
    while True:
        user_input = input("User: ")
        if user_input.lower() == 'exit':
            print("Ending chat session.")
            break
        
        user_message = HumanMessage(content=user_input)
        history.add_message(user_message)
    
        prompt = compose_prompt(user_input)
        
        response = llm.invoke(prompt)

        print(f"AI: {response.content}")
        history.add_message(response)

if __name__ == "__main__":
    start_chat()
