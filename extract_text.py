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
        # Skip some pages (If needed)
        # if page_num <= 3:
        #     continue

        # Skip empty pages
        # if not page.get_text("text"):
        #     continue

        # Remove tables
        for tab in page.find_tables():
            # process the content of table 'tab'
            page.add_redact_annot(tab.bbox)  # wrap table in a redaction annotation
        
        page.apply_redactions()  # erase all table text

        # Obtains the text of the page
        blocks = page.get_text("dict")["blocks"]

        for b in blocks:
            if "lines" not in b:
                continue
            font_sizes = []
            text_content = []

            # Set to true if you want to ignore everything that comes after the unwanted text
            ignore = False

            for l in b["lines"]:
                if ignore:
                    continue

                for s in l["spans"]:
                    if ignore:
                        continue

                    if s["size"] >= MIN_FONT_SIZE and s["text"].strip():
                        print(s["text"].strip())
                        # Ignore the whole line
                        # if "Test ignore" in s["text"].strip():
                        #     ignore = True
                        #     text_content = []
                        #     continue
                        
                        # Only ignore the character "•"
                        # if "•" in s["text"].strip():
                        #     continue

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
