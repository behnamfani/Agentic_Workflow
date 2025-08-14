import fitz  # PyMuPDF
import easyocr


def extract_text_with_easyocr(pdf_path, lang_list=["en"]):
    reader = easyocr.Reader(lang_list)
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]

        # First try extracting embedded text (if any)
        text = page.get_text("text")
        # if text.strip():
        full_text += f"\n--- Page {page_num + 1} (Embedded Text) ---\n{text}"
        # else
        # If no text, run OCR on the image of the page
        pix = page.get_pixmap(dpi=300)  # render high-res image
        img_bytes = pix.tobytes("png")
        results = reader.readtext(img_bytes, detail=0)
        ocr_text = "\n".join(results)
        full_text += f"**OCR**: \n--- Page {page_num + 1} (OCR) ---\n{ocr_text}"

    return full_text


if __name__ == "__main__":
    pdf_file = "Bitcoin.pdf"  # Replace with your file
    text_output = extract_text_with_easyocr(pdf_file)
    print(text_output)
