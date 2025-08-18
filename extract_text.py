import fitz
import json

PDF_PATH = "book.pdf"
OUTPUT_JSON = "vision_output.json"
# Ignore text if belowe this font size
MIN_FONT_SIZE = 2

def extract_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    results = []

    for page_num, page in enumerate(doc, start=1):
        # Obtains the text of the page
        blocks = page.get_text("dict")["blocks"]

        for b in blocks:
            if "lines" not in b:
                continue
            font_sizes = []
            text_content = []

            for l in b["lines"]:
                for s in l["spans"]:
                    if s["size"] >= MIN_FONT_SIZE and s["text"].strip():
                        # Ignore alone numbers in the text, such as "1", "2", etc.
                        try:
                            num = int(s["text"])
                            continue
                        except:
                            font_sizes.append(s["size"])
                            text_content.append(s["text"].strip())

            if not text_content:
                continue

            avg_font_size = sum(font_sizes) / len(font_sizes)
            results.append({
                "page": page_num,
                "text": " ".join(text_content),
                "avg_font_size": round(avg_font_size, 2)
            })

    return results

if __name__ == "__main__":
    data = extract_from_pdf(PDF_PATH)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Extracted data saved to {OUTPUT_JSON}")
