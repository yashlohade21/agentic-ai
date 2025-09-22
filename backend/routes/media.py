import os
import logging
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import uuid
from datetime import datetime
# from PIL import Image  # Commented for deployment
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
import mimetypes
from routes.auth import require_auth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint for media routes
media_bp = Blueprint("media", __name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {
    'images': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'},
    'documents': {'pdf', 'txt', 'md', 'doc', 'docx'},
    'audio': {'mp3', 'wav', 'ogg', 'm4a'},
    'video': {'mp4', 'avi', 'mov', 'mkv', 'webm'}
}

def ensure_upload_directory():
    """Ensure upload directory exists"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        logger.info(f"Created upload directory: {UPLOAD_FOLDER}")

def allowed_file(filename):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False, None
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return True, file_type
    
    return False, None

def get_file_info(file_path):
    """Get comprehensive file information"""
    try:
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        
        file_info = {
            'size': file_size,
            'size_human': format_file_size(file_size),
            'mime_type': mime_type,
            'created_at': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        }
        
        # Additional info for images
        if mime_type and mime_type.startswith('image/') and PIL_AVAILABLE:
            try:
                with Image.open(file_path) as img:
                    file_info.update({
                        'width': img.width,
                        'height': img.height,
                        'format': img.format
                    })
            except Exception as e:
                logger.warning(f"Could not get image info for {file_path}: {e}")
        
        return file_info
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        return {}

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def process_image(file_path, max_width=1920, max_height=1080, quality=85):
    """Process and optimize uploaded images"""
    if not PIL_AVAILABLE:
        logger.warning("PIL not available, skipping image processing")
        return

    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            # Resize if too large
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                logger.info(f"Resized image to {img.width}x{img.height}")

            # Save optimized version
            img.save(file_path, 'JPEG', quality=quality, optimize=True)
            logger.info(f"Optimized image saved: {file_path}")

    except Exception as e:
        logger.error(f"Error processing image {file_path}: {e}")

@media_bp.route('/upload', methods=['POST'])
@require_auth
def upload_file():
    """Handle file upload"""
    try:
        ensure_upload_directory()
        
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'error': f'File too large. Maximum size is {format_file_size(MAX_FILE_SIZE)}'
            }), 400
        
        # Check file type
        is_allowed, file_type = allowed_file(file.filename)
        if not is_allowed:
            return jsonify({
                'error': f'File type not allowed. Supported types: {", ".join(sum(ALLOWED_EXTENSIONS.values(), set()))}'
            }), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Create user-specific directory
        user_id = session.get('user_id', 'anonymous')
        user_upload_dir = os.path.join(UPLOAD_FOLDER, user_id)
        if not os.path.exists(user_upload_dir):
            os.makedirs(user_upload_dir)
        
        file_path = os.path.join(user_upload_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        logger.info(f"File saved: {file_path}")
        
        # Process image if it's an image file
        if file_type == 'images':
            process_image(file_path)
        
        # Get file information
        file_info = get_file_info(file_path)
        
        # Prepare response
        response_data = {
            'success': True,
            'message': 'File uploaded successfully',
            'file': {
                'id': unique_filename.split('.')[0],  # UUID without extension
                'original_name': original_filename,
                'filename': unique_filename,
                'file_type': file_type,
                'path': file_path,
                'url': f'/api/media/file/{user_id}/{unique_filename}',
                **file_info
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@media_bp.route('/file/<user_id>/<filename>', methods=['GET'])
def serve_file(user_id, filename):
    """Serve uploaded files"""
    try:
        # Security check - ensure filename is secure
        secure_filename_check = secure_filename(filename)
        if secure_filename_check != filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        file_path = os.path.join(UPLOAD_FOLDER, user_id, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Send file
        from flask import send_file
        return send_file(file_path)
        
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        return jsonify({'error': 'Failed to serve file'}), 500

@media_bp.route('/files', methods=['GET'])
@require_auth
def list_user_files():
    """List all files uploaded by the current user"""
    try:
        user_id = session.get('user_id', 'anonymous')
        user_upload_dir = os.path.join(UPLOAD_FOLDER, user_id)
        
        if not os.path.exists(user_upload_dir):
            return jsonify({'files': []}), 200
        
        files = []
        for filename in os.listdir(user_upload_dir):
            file_path = os.path.join(user_upload_dir, filename)
            if os.path.isfile(file_path):
                # Get file type
                _, file_type = allowed_file(filename)
                
                file_info = get_file_info(file_path)
                
                files.append({
                    'id': filename.split('.')[0],
                    'filename': filename,
                    'file_type': file_type,
                    'url': f'/api/media/file/{user_id}/{filename}',
                    **file_info
                })
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({'files': files}), 200
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({'error': 'Failed to list files'}), 500

@media_bp.route('/file/<file_id>', methods=['DELETE'])
@require_auth
def delete_file(file_id):
    """Delete a specific file"""
    try:
        user_id = session.get('user_id', 'anonymous')
        user_upload_dir = os.path.join(UPLOAD_FOLDER, user_id)
        
        # Find file with matching ID
        target_file = None
        for filename in os.listdir(user_upload_dir):
            if filename.startswith(file_id):
                target_file = filename
                break
        
        if not target_file:
            return jsonify({'error': 'File not found'}), 404
        
        file_path = os.path.join(user_upload_dir, target_file)
        os.remove(file_path)
        
        logger.info(f"File deleted: {file_path}")
        return jsonify({'message': 'File deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {e}")
        return jsonify({'error': 'Failed to delete file'}), 500

@media_bp.route('/analyze', methods=['POST'])
@require_auth
def analyze_media():
    """Analyze uploaded media using Groq AI"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        user_prompt = data.get('prompt', 'Analyze this file and describe what you see.')

        if not file_id:
            return jsonify({'error': 'File ID required'}), 400

        user_id = session.get('user_id', 'anonymous')
        user_upload_dir = os.path.join(UPLOAD_FOLDER, user_id)

        # Find file
        target_file = None
        for filename in os.listdir(user_upload_dir):
            if filename.startswith(file_id):
                target_file = filename
                break

        if not target_file:
            return jsonify({'error': 'File not found'}), 404

        file_path = os.path.join(user_upload_dir, target_file)
        _, file_type = allowed_file(target_file)

        # Get LLM manager
        from core.llm_manager_fixed import LLMManager
        llm_manager = LLMManager()

        analysis_result = None

        if file_type == 'images':
            # Analyze image using Groq vision model
            import base64
            try:
                with open(file_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')

                # Use Groq vision model for image analysis
                analysis_result = llm_manager.analyze_image_with_groq_sync(img_data, user_prompt)

            except Exception as e:
                logger.error(f"Error analyzing image with Groq: {e}")
                # Fallback to basic image analysis
                if PIL_AVAILABLE:
                    try:
                        with Image.open(file_path) as img:
                            analysis_result = f"Image Analysis: {img.width}x{img.height} pixels, format: {img.format}"
                    except Exception as img_e:
                        analysis_result = f"Could not analyze image: {img_e}"
                else:
                    analysis_result = "Image analysis not available"

        elif file_type == 'documents' and target_file.endswith('.pdf'):
            # Analyze PDF using Groq
            try:
                # Extract text from PDF
                try:
                    import PyPDF2
                    pdf_text = ""
                    with open(file_path, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        for page in pdf_reader.pages:
                            pdf_text += page.extract_text() + "\n"
                except ImportError:
                    # Fallback if PyPDF2 is not available
                    logger.warning("PyPDF2 not available, using basic PDF info")
                    file_size = os.path.getsize(file_path)
                    pdf_text = f"PDF document ({format_file_size(file_size)}) uploaded for analysis."

                # Use Groq to analyze the PDF content
                prompt = f"Analyze this PDF content and provide a summary:\n\n{pdf_text[:4000]}"  # Limit to avoid token limits
                analysis_result = llm_manager.generate_response_sync(prompt, "You are an AI assistant specialized in document analysis. Provide clear, concise summaries and insights.")

            except Exception as e:
                logger.error(f"Error analyzing PDF with Groq: {e}")
                try:
                    file_size = os.path.getsize(file_path)
                    analysis_result = f"PDF Analysis: File size {format_file_size(file_size)}, estimated {max(1, file_size // (1024 * 2))} pages"
                except Exception as basic_e:
                    analysis_result = f"Could not analyze PDF: {basic_e}"

        elif file_type == 'documents' and target_file.endswith('.txt'):
            # Analyze text files
            try:
                with open(file_path, 'r', encoding='utf-8') as txt_file:
                    content = txt_file.read()

                prompt = f"Analyze this text document:\n\n{content[:4000]}"
                analysis_result = llm_manager.generate_response_sync(prompt, "You are an AI assistant specialized in text analysis. Provide insights about the content, structure, and key points.")

            except Exception as e:
                logger.error(f"Error analyzing text with Groq: {e}")
                analysis_result = f"Could not analyze text file: {e}"

        else:
            analysis_result = f"File type '{file_type}' is not supported for AI analysis. Supported types: images (jpg, png, gif, etc.) and documents (pdf, txt)."

        response = {
            'success': True,
            'file_type': file_type,
            'analysis': analysis_result or "No analysis available for this file type.",
            'file_name': target_file
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error analyzing media: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

# Initialize upload directory on module import
ensure_upload_directory()

