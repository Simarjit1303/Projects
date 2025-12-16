import pytesseract
from PIL import Image
from ..config import Config
from ..logger import get_logger

logger = get_logger(__name__)

class ImageProcessor:
    @staticmethod
    def extract_text(uploaded_file):
        try:
            if isinstance(uploaded_file, str):
                image = Image.open(uploaded_file)
            else:
                if hasattr(uploaded_file, 'seek'):
                    uploaded_file.seek(0)
                image = Image.open(uploaded_file)

            if image.mode != 'RGB':
                image = image.convert('RGB')
            image = image.convert('L')

            width, height = image.size
            new_size = (width * Config.OCR_RESIZE_FACTOR, height * Config.OCR_RESIZE_FACTOR)
            image = image.resize(new_size, Image.Resampling.LANCZOS)

            text = pytesseract.image_to_string(image, config=r'--oem 3 --psm 6').strip()
            return text or None
        except Exception as e:
            logger.error(f"OCR error: {e}", exc_info=True)
            return None
