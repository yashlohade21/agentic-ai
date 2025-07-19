import numpy as np
from PIL import Image
import cv2
import base64
import io
from typing import Union, List, Dict, Any
import logging
import PyPDF2
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Utilities for processing image data for deep learning models"""
    
    @staticmethod
    def base64_to_image(base64_string: str) -> Image.Image:
        """Convert base64 string to PIL Image"""
        try:
            # Remove data URL prefix if present
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            
            image_data = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_data))
            return image
        except Exception as e:
            logger.error(f"Failed to convert base64 to image: {str(e)}")
            raise
    
    @staticmethod
    def preprocess_for_classification(image: Image.Image, target_size: tuple = (224, 224)) -> np.ndarray:
        """Preprocess image for classification models (e.g., ResNet, VGG)"""
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image
            image = image.resize(target_size)
            
            # Convert to numpy array and normalize
            img_array = np.array(image, dtype=np.float32)
            img_array = img_array / 255.0  # Normalize to [0, 1]
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
        except Exception as e:
            logger.error(f"Failed to preprocess image for classification: {str(e)}")
            raise
    
    @staticmethod
    def extract_text_from_image(image: Image.Image) -> str:
        """Extract text from image using OCR"""
        try:
            import pytesseract
            text = pytesseract.image_to_string(image)
            return text.strip()
        except ImportError:
            logger.error("pytesseract not installed. Install with: pip install pytesseract")
            return "OCR not available - pytesseract not installed"
        except Exception as e:
            logger.error(f"Failed to extract text from image: {str(e)}")
            return f"Error extracting text: {str(e)}"

class PDFProcessor:
    """Utilities for processing PDF documents"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            # Try with PyMuPDF first (better for complex PDFs)
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except Exception as e:
            logger.warning(f"PyMuPDF failed, trying PyPDF2: {str(e)}")
            try:
                # Fallback to PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text.strip()
            except Exception as e2:
                logger.error(f"Failed to extract text from PDF: {str(e2)}")
                return f"Error extracting text from PDF: {str(e2)}"
    
    @staticmethod
    def pdf_to_images(pdf_content: bytes) -> List[Image.Image]:
        """Convert PDF pages to images"""
        try:
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            images = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()
                img_data = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_data))
                images.append(img)
            doc.close()
            return images
        except Exception as e:
            logger.error(f"Failed to convert PDF to images: {str(e)}")
            return []

class TextProcessor:
    """Utilities for processing text data for deep learning models"""
    
    @staticmethod
    def preprocess_for_sentiment(text: str, tokenizer, max_length: int = 512) -> Dict[str, Any]:
        """Preprocess text for sentiment analysis"""
        try:
            # Tokenize text
            encoded = tokenizer(
                text,
                truncation=True,
                padding='max_length',
                max_length=max_length,
                return_tensors='pt'
            )
            return encoded
        except Exception as e:
            logger.error(f"Failed to preprocess text for sentiment: {str(e)}")
            raise
    
    @staticmethod
    def preprocess_for_ner(text: str, tokenizer, max_length: int = 512) -> Dict[str, Any]:
        """Preprocess text for named entity recognition"""
        try:
            # Tokenize text
            encoded = tokenizer(
                text,
                truncation=True,
                padding='max_length',
                max_length=max_length,
                return_tensors='pt',
                return_offsets_mapping=True
            )
            return encoded
        except Exception as e:
            logger.error(f"Failed to preprocess text for NER: {str(e)}")
            raise

class OutputProcessor:
    """Utilities for post-processing model outputs"""
    
    @staticmethod
    def process_classification_output(predictions: np.ndarray, class_labels: List[str]) -> Dict[str, Any]:
        """Process classification model output"""
        try:
            # Get predicted class
            predicted_class_idx = np.argmax(predictions[0])
            predicted_class = class_labels[predicted_class_idx]
            confidence = float(predictions[0][predicted_class_idx])
            
            # Get top 3 predictions
            top_indices = np.argsort(predictions[0])[-3:][::-1]
            top_predictions = [
                {
                    'class': class_labels[idx],
                    'confidence': float(predictions[0][idx])
                }
                for idx in top_indices
            ]
            
            return {
                'predicted_class': predicted_class,
                'confidence': confidence,
                'top_predictions': top_predictions
            }
        except Exception as e:
            logger.error(f"Failed to process classification output: {str(e)}")
            raise
    
    @staticmethod
    def process_sentiment_output(predictions: np.ndarray) -> Dict[str, Any]:
        """Process sentiment analysis output"""
        try:
            # Assuming binary sentiment (negative, positive)
            sentiment_labels = ['negative', 'positive']
            
            # Apply softmax to get probabilities
            probabilities = np.exp(predictions) / np.sum(np.exp(predictions), axis=1, keepdims=True)
            
            predicted_idx = np.argmax(probabilities[0])
            predicted_sentiment = sentiment_labels[predicted_idx]
            confidence = float(probabilities[0][predicted_idx])
            
            return {
                'sentiment': predicted_sentiment,
                'confidence': confidence,
                'probabilities': {
                    'negative': float(probabilities[0][0]),
                    'positive': float(probabilities[0][1])
                }
            }
        except Exception as e:
            logger.error(f"Failed to process sentiment output: {str(e)}")
            raise

