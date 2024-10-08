from langchain.schema import SystemMessage
from extractLayout import LayoutExtractor

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
    
    **Document Layout Details**:\n
    {layout_details}
    
    **Extracted Layout Text**:
    The following text was extracted from the provided document layout. Use this as a reference to guide your tone, style, and overall structure, but generate new and creative content based on these themes:
    {layout_text}
    
    **Your Task**: Generate high-quality, creative magazine content that adheres to the layout structure and constraints. The content must match the users query, maintain the specified tone, and stay within the word count limits for each section.
    """
    return SystemMessage(content=system_prompt)