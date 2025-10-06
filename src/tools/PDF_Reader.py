import fitz  # PyMuPDF
import easyocr
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.tools import StructuredTool

from src.config import logger


def extract_page(page_data):
    """Extract text from a single page"""
    page, page_num, reader, include_OCR = page_data
    try:
        text = page.get_text("text")
        result = f"\n--- Page {page_num + 1} (Embedded Text) ---\n{text}"

        if include_OCR:
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            ocr_results = reader.readtext(img_bytes, detail=0)
            ocr_text = "\n".join(ocr_results)
            result += f"**OCR**: \n--- Page {page_num + 1} (OCR) ---\n{ocr_text}"
        return result
    except Exception as e:
        return f"Error in extracting page {page_num}: {e}"


def extract_text_with_easyocr(pdf_path, lang_list=None, include_OCR: bool = True):
    """
    Extract path from the given PDF path in the system
    :param pdf_path: string path to PDF file
    :param lang_list: list of languages for easyocr --> default to ["en", "fr", "de"]
    :param include_OCR: Boolean whether to use include_OCR or not, default to True
    :return: extracted text of the pdf
    """
    try:
        logger.info(f"Calling extract_text_with_easyocr with arguments:"
                    f"{pdf_path}, lang_list={lang_list}, include_OCR={include_OCR}")
        if lang_list is None:
            lang_list = ["en", "fr", "de"]
        reader = easyocr.Reader(list(lang_list)) if include_OCR else None
        doc = fitz.open(fr"{str(pdf_path)}")
        num_pages = len(doc)
        # Extract pages in parallel using map
        page_data = [(doc[i], i, reader, include_OCR) for i in range(doc.page_count)]

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(extract_page, page_data))

        full_text = "".join(results)

        logger.info("Extracting completed!")
        return full_text
    except Exception as e:
        logger.error(f"Error occurred in extract_text_with_easyocr: {e}")
        return f"Error occurred in extract_text_with_easyocr: {e}"


def get_tool() -> StructuredTool:
    return StructuredTool.from_function(extract_text_with_easyocr)