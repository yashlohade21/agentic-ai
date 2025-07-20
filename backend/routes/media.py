import logging
import os
import uuid
from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename
from datetime import datetime
try:
    from firebase_config import db
except:
    from firebase_config_mock import db
from routes.auth import require_auth
import base64
import mimetypes

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create a Blueprint for media routes
media_bp = Blueprint("media", __name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp',
    'mp3', 'wav', 'ogg', 'mp4', 'avi', 'mov', 'webm',
    'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'csv', 'json', 'xml', 'zip', 'rar'
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    """Determine file type category"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp']:
        return 'image'
    elif ext in ['mp3', 'wav', 'ogg']:
        return 'audio'
    elif ext in ['mp4', 'avi', 'mov', 'webm']:
        return 'video'
    elif ext in ['pdf']:
        return 'pdf'
    elif ext in ['txt', 'csv', 'json', 'xml']:
        return 'text'
    elif ext in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']:
        return 'document'
    elif ext in ['zip', 'rar']:
        return 'archive'
    else:
        return 'other'

@media_bp.route("/media/upload", methods=["POST"])
@require_auth
def upload_file():
    """Handle file upload"""
    try:
        user_id = session["user_id"]
        
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check file size
        if request.content_length > MAX_FILE_SIZE:
            return jsonify({"error": f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"}), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
        
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        filename = f"{file_id}.{file_extension}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save file
        file.save(filepath)
        
        # Get file info
        file_size = os.path.getsize(filepath)
        file_type = get_file_type(original_filename)
        mime_type = mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'
        
        # Save file metadata to database
        try:
            files_ref = db.collection("uploaded_files")
            file_doc = files_ref.document(file_id)
            file_doc.set({
                "file_id": file_id,
                "original_filename": original_filename,
                "filename": filename,
                "filepath": filepath,
                "file_size": file_size,
                "file_type": file_type,
                "mime_type": mime_type,
                "user_id": user_id,
                "upload_timestamp": datetime.now(),
                "status": "uploaded"
            })
            
            logging.info(f"File uploaded successfully: {original_filename} by user {user_id}")
            
        except Exception as db_error:
            logging.error(f"Database error saving file metadata: {db_error}")
            # Clean up file if database save fails
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify({"error": "Failed to save file metadata"}), 500
        
        return jsonify({
            "success": True,
            "file_id": file_id,
            "original_filename": original_filename,
            "file_size": file_size,
            "file_type": file_type,
            "mime_type": mime_type,
            "message": "File uploaded successfully"
        }), 200
        
    except Exception as e:
        logging.error(f"Error in file upload: {e}", exc_info=True)
        return jsonify({"error": "File upload failed"}), 500

@media_bp.route("/media/files", methods=["GET"])
@require_auth
def get_user_files():
    """Get list of files uploaded by the current user"""
    try:
        user_id = session["user_id"]
        
        files_ref = db.collection("uploaded_files")
        query = files_ref.where("user_id", "==", user_id).limit(50)
        files = []
        
        for doc in query.stream():
            file_data = doc.to_dict()
            files.append({
                "file_id": file_data.get("file_id"),
                "original_filename": file_data.get("original_filename"),
                "file_size": file_data.get("file_size"),
                "file_type": file_data.get("file_type"),
                "mime_type": file_data.get("mime_type"),
                "upload_timestamp": file_data.get("upload_timestamp"),
                "status": file_data.get("status")
            })
        
        return jsonify({
            "success": True,
            "files": files
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting user files: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve files"}), 500

@media_bp.route("/media/file/<file_id>", methods=["GET"])
@require_auth
def get_file_info(file_id):
    """Get information about a specific file"""
    try:
        user_id = session["user_id"]
        
        files_ref = db.collection("uploaded_files")
        file_doc = files_ref.document(file_id).get()
        
        if not file_doc.exists:
            return jsonify({"error": "File not found"}), 404
        
        file_data = file_doc.to_dict()
        
        # Check if user owns the file
        if file_data.get("user_id") != user_id:
            return jsonify({"error": "Access denied"}), 403
        
        return jsonify({
            "success": True,
            "file": {
                "file_id": file_data.get("file_id"),
                "original_filename": file_data.get("original_filename"),
                "file_size": file_data.get("file_size"),
                "file_type": file_data.get("file_type"),
                "mime_type": file_data.get("mime_type"),
                "upload_timestamp": file_data.get("upload_timestamp"),
                "status": file_data.get("status")
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting file info: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve file information"}), 500

@media_bp.route("/media/file/<file_id>", methods=["DELETE"])
@require_auth
def delete_file(file_id):
    """Delete a file"""
    try:
        user_id = session["user_id"]
        
        files_ref = db.collection("uploaded_files")
        file_doc = files_ref.document(file_id).get()
        
        if not file_doc.exists:
            return jsonify({"error": "File not found"}), 404
        
        file_data = file_doc.to_dict()
        
        # Check if user owns the file
        if file_data.get("user_id") != user_id:
            return jsonify({"error": "Access denied"}), 403
        
        # Delete physical file
        filepath = file_data.get("filepath")
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                logging.warning(f"Failed to delete physical file {filepath}: {e}")
        
        # Delete from database
        files_ref.document(file_id).delete()
        
        logging.info(f"File deleted successfully: {file_id} by user {user_id}")
        
        return jsonify({
            "success": True,
            "message": "File deleted successfully"
        }), 200
        
    except Exception as e:
        logging.error(f"Error deleting file: {e}", exc_info=True)
        return jsonify({"error": "Failed to delete file"}), 500

