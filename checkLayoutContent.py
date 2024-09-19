from extractLayout import LayoutExtractor

layout_extractor = LayoutExtractor("Texract-JSON/MedicalAnalyzeDocResponse.json")
layout_details = layout_extractor.get_layout_details()
layout_text = layout_extractor.get_text_from_layout()
print(layout_details)
print(layout_text)