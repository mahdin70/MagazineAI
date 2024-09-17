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

        for page_block in page_blocks:
            page_content = f"Page {page_block['Page']}\n"
            
            block_counts = {"LAYOUT_TITLE": [], "LAYOUT_SECTION_HEADER": [], "LAYOUT_TEXT": []}

            def render_block_with_counts(block, block_counts):
                output = ""
                if block["BlockType"] in block_counts:
                    word_count = self.get_word_count_from_parent(block)
                    block_counts[block["BlockType"]].append(1)
                    count_index = len(block_counts[block["BlockType"]])
                    output += f"{block['BlockType']} : {count_index} -> Word Count: {word_count}\n"

                for child_id in block.get("Relationships", [{}])[0].get("Ids", []):
                    child_block = self.get_block_by_id(child_id)
                    if child_block and child_block["BlockType"] in ["LAYOUT_TEXT", "LAYOUT_SECTION_HEADER"]:
                        output += render_block_with_counts(child_block, block_counts)
                
                return output

            block_content = "".join(render_block_with_counts(self.get_block_by_id(id), block_counts) for id in page_block["Relationships"][0]["Ids"])
            layout_details += page_content + block_content + "\n" 

        return layout_details
