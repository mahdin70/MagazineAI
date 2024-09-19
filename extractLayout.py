import json
from typing import Dict, Any

class LayoutExtractor:
    def __init__(self, file_path: str):
        with open(file_path, "r") as f:
            self.data = json.load(f)

    def get_block_by_id(self, block_id: str) -> Dict[str, Any]:
        return next(block for block in self.data["Blocks"] if block["Id"] == block_id)

    def get_word_count_from_line(self, line_block: Dict[str, Any]) -> int:
        word_ids = line_block.get("Relationships", [{}])[0].get("Ids", [])
        words = [self.get_block_by_id(word_id) for word_id in word_ids if self.get_block_by_id(word_id)["BlockType"] == "WORD"]
        return sum(len(word_block["Text"].split()) for word_block in words if "Text" in word_block)

    def get_word_count_from_parent(self, parent_block: Dict[str, Any]) -> int:
        line_ids = parent_block.get("Relationships", [{}])[0].get("Ids", [])
        lines = [self.get_block_by_id(line_id) for line_id in line_ids if self.get_block_by_id(line_id)["BlockType"] == "LINE"]
        return sum(self.get_word_count_from_line(line) for line in lines)

    def get_layout_details(self) -> str:
        page_blocks = [block for block in self.data["Blocks"] if block["BlockType"] == "PAGE"]
        layout_details = ""

        block_counts = {
            "LAYOUT_TITLE": [], 
            "LAYOUT_SECTION_HEADER": [], 
            "LAYOUT_TEXT": [], 
            "LAYOUT_HEADER": [], 
            "LAYOUT_FOOTER": []
        }

        for page_block in page_blocks:
            page_content = f"Page {page_block['Page']}\n"
            layout_details += page_content

            def render_block_with_counts(block, block_counts):
                output = ""
                if block["BlockType"] in block_counts:
                    word_count = self.get_word_count_from_parent(block)
                    block_counts[block["BlockType"]].append(1)
                    count_index = len(block_counts[block["BlockType"]])
                    output += f"{block['BlockType']} : {count_index} -> Word Count: {word_count}\n"

                for child_id in block.get("Relationships", [{}])[0].get("Ids", []):
                    child_block = self.get_block_by_id(child_id)
                    if child_block and child_block["BlockType"] in block_counts:
                        output += render_block_with_counts(child_block, block_counts)
                
                return output

            block_content = "".join(render_block_with_counts(self.get_block_by_id(id), block_counts) for id in page_block["Relationships"][0]["Ids"])
            layout_details += block_content + "\n" 

        return layout_details
  
    def extract_text_from_block(self, block: Dict[str, Any]) -> str:
        if block["BlockType"] == "WORD":
            return block.get("Text", "")
        
        text_content = ""
        if "Relationships" in block:
            for child_id in block["Relationships"][0].get("Ids", []):
                child_block = self.get_block_by_id(child_id)
                text_content += self.extract_text_from_block(child_block) + " "
        
        return text_content.strip()

    def get_text_from_layout(self) -> str:
        page_blocks = [block for block in self.data["Blocks"] if block["BlockType"] == "PAGE"]
        layout_text = ""

        for page_block in page_blocks:
            page_content = f"Page {page_block['Page']}\n"
            layout_text += page_content

            for block_id in page_block["Relationships"][0].get("Ids", []):
                block = self.get_block_by_id(block_id)

                if block["BlockType"] in ["LAYOUT_TITLE", "LAYOUT_SECTION_HEADER", "LAYOUT_TEXT", "LAYOUT_HEADER", "LAYOUT_FOOTER"]:
                    block_type = block["BlockType"]
                    text = self.extract_text_from_block(block)
                    layout_text += f"{block_type}: {text}\n"
                    
        return layout_text