import os
import logging
import tensorflow as tf
import torch
from transformers import AutoTokenizer, AutoModel
from typing import Dict, Any, Optional
import numpy as np
from PIL import Image
import cv2

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Centralized manager for loading and managing deep learning models
    """
    
    def __init__(self):
        self.models = {}
        # self.tokenizers = {}
        self.model_configs = {}
        
    def load_tensorflow_model(self, model_name: str, model_path: str) -> bool:
        """Load a TensorFlow/Keras model"""
        try:
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                return False
                
            model = tf.keras.models.load_model(model_path)
            self.models[model_name] = {
                'model': model,
                'framework': 'tensorflow',
                'type': 'keras'
            }
            logger.info(f"Successfully loaded TensorFlow model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load TensorFlow model {model_name}: {str(e)}")
            return False
    
    def load_pytorch_model(self, model_name: str, model_path: str, model_class=None) -> bool:
        """Load a PyTorch model"""
        try:
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                return False
                
            if model_class:
                # Load custom model class
                model = model_class()
                model.load_state_dict(torch.load(model_path, map_location='cpu'))
            else:
                # Load entire model
                model = torch.load(model_path, map_location='cpu')
                
            model.eval()  # Set to evaluation mode
            
            self.models[model_name] = {
                'model': model,
                'framework': 'pytorch',
                'type': 'custom'
            }
            logger.info(f"Successfully loaded PyTorch model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load PyTorch model {model_name}: {str(e)}")
            return False
    
    def load_huggingface_model(self, model_name: str, model_identifier: str) -> bool:
        """Load a Hugging Face transformers model"""
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_identifier)
            model = AutoModel.from_pretrained(model_identifier)
            
            self.models[model_name] = {
                'model': model,
                'framework': 'huggingface',
                'type': 'transformer'
            }
            # self.tokenizers[model_name] = tokenizer
            
            logger.info(f"Successfully loaded Hugging Face model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Hugging Face model {model_name}: {str(e)}")
            return False
    
    def get_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get a loaded model by name"""
        return self.models.get(model_name)
    
    # def get_tokenizer(self, model_name: str):
    #     """Get a tokenizer by model name"""
    #     return self.tokenizers.get(model_name)
    
    def is_model_loaded(self, model_name: str) -> bool:
        """Check if a model is loaded"""
        return model_name in self.models
    
    def list_loaded_models(self) -> list:
        """Get list of all loaded model names"""
        return list(self.models.keys())

# Global model manager instance
model_manager = ModelManager()

