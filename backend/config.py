"""Configuration settings for the Flask application"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    PORT = int(os.getenv('PORT', 5000))
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'txt', 'md', 'pdf', 'docx'}

