import json
import jenkspy

INPUT_JSON = "vision_output.json"
OUTPUT_JSON = "classified_text.json"

def classify_font_sizes(data, n_classes=4):
    # We use the avg_font_size instead of font_height
    font_sizes = [block["avg_font_size"] for block in data if block["avg_font_size"] > 0]

    # We calculate the Jenks breaks
    breaks = jenkspy.jenks_breaks(font_sizes, n_classes)
    print("Jenks breaks:", breaks)

    # Handy function to assign a label to a block
    def get_label(size):
        if size < breaks[1]:
            return "other"     # Small text, like footnotes
        elif size < breaks[2]:
            return "caption"   # Bigger text, like captions
        elif size < breaks[3]:
            return "body"      # Main text
        else:
            return "header"    # Biggest texts, like headers, titles...

    # Now we assign a label to each block
    for block in data:
        size = block["avg_font_size"]
        block["label"] = get_label(size)

    return data

if __name__ == "__main__":
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    classified_data = classify_font_sizes(data)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(classified_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Classified text saved to {OUTPUT_JSON}")
