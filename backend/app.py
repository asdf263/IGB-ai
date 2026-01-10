from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
from werkzeug.utils import secure_filename
import tempfile
import logging
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'txt', 'md', 'pdf', 'docx'}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    logger.warning("GEMINI_API_KEY not found in environment variables")
    model = None


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_text_file(file_path):
    """Read text content from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'gemini_configured': model is not None
    }), 200


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and return content"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read file content
        content = read_text_file(filepath)
        
        # Clean up temp file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'content_length': len(content),
            'preview': content[:500]  # First 500 chars as preview
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """Analyze text using Gemini LLM"""
    if not model:
        return jsonify({'error': 'Gemini API not configured'}), 500
    
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text']
    analysis_type = data.get('analysis_type', 'general')
    
    if not text:
        return jsonify({'error': 'Text is empty'}), 400
    
    try:
        # Create prompt based on analysis type
        prompts = {
            'general': f"Analyze the following text and provide insights:\n\n{text}",
            'summary': f"Provide a comprehensive summary of the following text:\n\n{text}",
            'sentiment': f"Analyze the sentiment of the following text:\n\n{text}",
            'keywords': f"Extract key topics and keywords from the following text:\n\n{text}",
            'qa': f"Answer questions about the following text:\n\n{text}\n\nQuestion: {data.get('question', 'What are the main points?')}"
        }
        
        prompt = prompts.get(analysis_type, prompts['general'])
        
        # Generate response
        response = model.generate_content(prompt)
        
        return jsonify({
            'success': True,
            'analysis_type': analysis_type,
            'result': response.text,
            'input_length': len(text)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in Gemini analysis: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/analyze-file', methods=['POST'])
def analyze_uploaded_file():
    """Upload file and analyze it in one request"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    if not model:
        return jsonify({'error': 'Gemini API not configured'}), 500
    
    file = request.files['file']
    analysis_type = request.form.get('analysis_type', 'general')
    
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read file content
        content = read_text_file(filepath)
        
        # Analyze with Gemini
        prompts = {
            'general': f"Analyze the following text and provide insights:\n\n{content}",
            'summary': f"Provide a comprehensive summary of the following text:\n\n{content}",
            'sentiment': f"Analyze the sentiment of the following text:\n\n{content}",
            'keywords': f"Extract key topics and keywords from the following text:\n\n{content}"
        }
        
        prompt = prompts.get(analysis_type, prompts['general'])
        response = model.generate_content(prompt)
        
        # Clean up temp file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'analysis_type': analysis_type,
            'result': response.text,
            'input_length': len(content)
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing file: {str(e)}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint for conversational interaction with Gemini"""
    if not model:
        return jsonify({'error': 'Gemini API not configured'}), 500
    
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    message = data['message']
    context = data.get('context', '')
    
    try:
        prompt = f"{context}\n\nUser: {message}\n\nAssistant:"
        response = model.generate_content(prompt)
        
        return jsonify({
            'success': True,
            'response': response.text
        }), 200
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({'error': f'Chat failed: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

