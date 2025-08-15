import fitz  # PyMuPDF
import easyocr
from langchain_core.tools import StructuredTool

from src.config import logger


def extract_text_with_easyocr(pdf_path, lang_list=None, include_OCR: bool = False):
    """
    Extract path from the given PDF path in the system
    :param pdf_path: string path to PDF file
    :param lang_list: list of languages for easyocr --> default to ["en", "fr", "de"]
    :param include_OCR: Boolean whether to use include_OCR or not, default to False
    :return: extracted text of the pdf
    """
    try:
        logger.info(f"Calling extract_text_with_easyocr with arguments:"
                    f"{pdf_path}, lang_list={lang_list}, include_OCR={include_OCR}")
        if lang_list is None:
            lang_list = ["en", "fr", "de"]
        reader = easyocr.Reader(list(lang_list))
        doc = fitz.open(fr"{str(pdf_path)}")
        full_text = ""

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            full_text += f"\n--- Page {page_num + 1} (Embedded Text) ---\n{text}"
            if include_OCR:
                pix = page.get_pixmap(dpi=300)  # render high-res image
                img_bytes = pix.tobytes("png")
                results = reader.readtext(img_bytes, detail=0)
                ocr_text = "\n".join(results)
                full_text += f"**OCR**: \n--- Page {page_num + 1} (OCR) ---\n{ocr_text}"

        logger.info("Extracting completed!")
        return full_text
    except Exception as e:
        logger.error(f"Error occured in extract_text_with_easyocr: {e}")
        return f"Error occured in extract_text_with_easyocr: {e}"


def get_tool() -> StructuredTool:
    return StructuredTool.from_function(extract_text_with_easyocr)