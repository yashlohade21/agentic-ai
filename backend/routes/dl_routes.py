from flask import Blueprint, request, jsonify, current_app
from core.model_manager_lite import model_manager
from core.data_processors import ImageProcessor, TextProcessor, OutputProcessor, PDFProcessor
import logging
import traceback
import base64

logger = logging.getLogger(__name__)

dl_bp = Blueprint("dl_bp", __name__, url_prefix="/api/dl")

@dl_bp.route("/models", methods=["GET"])
def list_models():
    """Get list of loaded models"""
    try:
        models = model_manager.list_loaded_models()
        return jsonify({"success": True, "models": models})
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@dl_bp.route("/image/classify", methods=["POST"])
def classify_image():
    """Classify an image using a loaded classification model"""
    try:
        data = request.get_json()

        if "image" not in data:
            return jsonify({"success": False, "error": "No image data provided"}), 400

        model_name = data.get("model_name", "image_classifier")

        # Check if model is loaded
        if not model_manager.is_model_loaded(model_name):
            return jsonify({"success": False, "error": f"Model {model_name} not loaded"}), 400

        # Get model
        model_info = model_manager.get_model(model_name)
        model = model_info["model"]

        # Process image
        image = ImageProcessor.base64_to_image(data["image"])
        processed_image = ImageProcessor.preprocess_for_classification(image)

        # Make prediction
        if model_info["framework"] == "tensorflow":
            predictions = model.predict(processed_image)
        else:
            # Handle PyTorch models
            import torch

            with torch.no_grad():
                predictions = model(torch.from_numpy(processed_image))
                predictions = predictions.numpy()

        # Process output (you'll need to define class labels for your specific model)
        class_labels = data.get(
            "class_labels", ["class_0", "class_1", "class_2"]
        )  # Default labels
        result = OutputProcessor.process_classification_output(predictions, class_labels)

        return jsonify({"success": True, "result": result})

    except Exception as e:
        logger.error(f"Error in image classification: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@dl_bp.route("/image/ocr", methods=["POST"])
def ocr_image():
    """Perform OCR on an image"""
    try:
        data = request.get_json()
        if "image" not in data:
            return jsonify({"success": False, "error": "No image data provided"}), 400

        image = ImageProcessor.base64_to_image(data["image"])
        extracted_text = ImageProcessor.extract_text_from_image(image)

        return jsonify({"success": True, "text": extracted_text})
    except Exception as e:
        logger.error(f"Error in OCR: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@dl_bp.route("/text/sentiment", methods=["POST"])
def analyze_sentiment():
    """Analyze sentiment of text using a loaded sentiment model"""
    try:
        data = request.get_json()

        if "text" not in data:
            return jsonify({"success": False, "error": "No text data provided"}), 400

        model_name = data.get("model_name", "sentiment_analyzer")

        # Check if model is loaded
        if not model_manager.is_model_loaded(model_name):
            return jsonify({"success": False, "error": f"Model {model_name} not loaded"}), 400

        # Get model and tokenizer
        model_info = model_manager.get_model(model_name)
        model = model_info["model"]
        tokenizer = model_manager.get_tokenizer(model_name)

        if not tokenizer:
            return jsonify({"success": False, "error": f"No tokenizer found for model {model_name}"}), 400

        # Process text
        processed_text = TextProcessor.preprocess_for_sentiment(data["text"], tokenizer)

        # Make prediction
        if model_info["framework"] == "huggingface":
            import torch

            with torch.no_grad():
                outputs = model(**processed_text)
                predictions = outputs.logits.numpy()
        else:
            # Handle other frameworks
            predictions = model.predict(processed_text)

        # Process output
        result = OutputProcessor.process_sentiment_output(predictions)

        return jsonify({"success": True, "result": result})

    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@dl_bp.route("/text/generate", methods=["POST"])
def generate_text():
    """Generate text using a loaded language model"""
    try:
        data = request.get_json()

        if "prompt" not in data:
            return jsonify({"success": False, "error": "No prompt provided"}), 400

        model_name = data.get("model_name", "text_generator")
        max_length = data.get("max_length", 100)

        # Check if model is loaded
        if not model_manager.is_model_loaded(model_name):
            return jsonify({"success": False, "error": f"Model {model_name} not loaded"}), 400

        # Get model and tokenizer
        model_info = model_manager.get_model(model_name)
        model = model_info["model"]
        tokenizer = model_manager.get_tokenizer(model_name)

        if not tokenizer:
            return jsonify({"success": False, "error": f"No tokenizer found for model {model_name}"}), 400

        # Generate text
        if model_info["framework"] == "huggingface":
            from transformers import pipeline

            generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
            generated = generator(
                data["prompt"],
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
            )
            result = {"generated_text": generated[0]["generated_text"], "prompt": data["prompt"]}
        else:
            # Handle other frameworks
            result = {"error": "Text generation not implemented for this framework"}

        return jsonify({"success": True, "result": result})

    except Exception as e:
        logger.error(f"Error in text generation: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@dl_bp.route("/pdf/extract_text", methods=["POST"])
def extract_text_from_pdf_route():
    """Extract text from a PDF file"""
    try:
        data = request.get_json()
        if "pdf_base64" not in data:
            return jsonify({"success": False, "error": "No PDF data provided"}), 400

        pdf_content = base64.b64decode(data["pdf_base64"])
        extracted_text = PDFProcessor.extract_text_from_pdf(pdf_content)

        return jsonify({"success": True, "text": extracted_text})
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@dl_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for deep learning services"""
    try:
        loaded_models = model_manager.list_loaded_models()
        return jsonify(
            {
                "success": True,
                "status": "healthy",
                "loaded_models": loaded_models,
                "model_count": len(loaded_models),
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({"success": False, "status": "unhealthy", "error": str(e)}), 500


