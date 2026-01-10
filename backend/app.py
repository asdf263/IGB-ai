from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
from werkzeug.utils import secure_filename
import tempfile
import logging
from dotenv import load_dotenv
import json
from datetime import datetime

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
    """Read text content from file
    
    Note: Currently only handles plain text files (.txt, .md).
    PDF and DOCX files require additional libraries (PyPDF2, python-docx).
    """
    # #region agent log
    file_ext = os.path.splitext(file_path)[1].lower() if os.path.exists(file_path) else 'unknown'
    with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'A','location':'app.py:39','message':'read_text_file entry','data':{'file_path':file_path,'extension':file_ext},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
    # #endregion
    try:
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'A','location':'app.py:46','message':'attempting utf-8 read','data':{'file_path':file_path},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'A','location':'app.py:48','message':'utf-8 read success','data':{'file_path':file_path,'content_length':len(content)},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        return content
    except UnicodeDecodeError:
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'A','location':'app.py:50','message':'utf-8 decode error, trying latin-1','data':{'file_path':file_path},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        # Try with different encoding
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'A','location':'app.py:53','message':'latin-1 read success','data':{'file_path':file_path,'content_length':len(content)},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        return content
    except Exception as e:
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'A','location':'app.py:55','message':'read_text_file exception','data':{'file_path':file_path,'error':str(e),'error_type':type(e).__name__},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise


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
    # #region agent log
    with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'B','location':'app.py:67','message':'upload_file entry','data':{'has_file':('file' in request.files)},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
    # #endregion
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    filepath = None
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # #region agent log
        file_ext = os.path.splitext(filename)[1].lower()
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'A','location':'app.py:82','message':'before file save','data':{'filename':filename,'extension':file_ext,'filepath':filepath},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        file.save(filepath)
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'B','location':'app.py:84','message':'file saved, before read','data':{'filepath':filepath,'exists':os.path.exists(filepath)},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        
        # Read file content
        content = read_text_file(filepath)
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'B','location':'app.py:87','message':'file read success, before cleanup','data':{'filepath':filepath,'content_length':len(content)},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        
        # Clean up temp file
        os.remove(filepath)
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'B','location':'app.py:90','message':'file cleanup success','data':{'filepath':filepath},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        
        return jsonify({
            'success': True,
            'filename': filename,
            'content_length': len(content),
            'preview': content[:500]  # First 500 chars as preview
        }), 200
        
    except Exception as e:
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'B','location':'app.py:99','message':'upload_file exception','data':{'filepath':filepath,'error':str(e),'error_type':type(e).__name__,'file_exists':(filepath and os.path.exists(filepath) if filepath else False)},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        logger.error(f"Error processing file: {str(e)}")
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
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
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'C','location':'app.py:131','message':'before Gemini API call','data':{'text_length':len(text),'prompt_length':len(prompt),'analysis_type':analysis_type},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        
        # Generate response
        response = model.generate_content(prompt)
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'C','location':'app.py:134','message':'Gemini API response received','data':{'has_text':hasattr(response,'text'),'response_type':type(response).__name__,'response_str':str(response)[:200]},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        
        # Get response text safely
        result_text = response.text if hasattr(response, 'text') else str(response)
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'C','location':'app.py:137','message':'result_text extracted','data':{'result_length':len(result_text) if result_text else 0},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        
        return jsonify({
            'success': True,
            'analysis_type': analysis_type,
            'result': result_text,
            'input_length': len(text)
        }), 200
        
    except Exception as e:
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'C','location':'app.py:146','message':'analyze_text exception','data':{'error':str(e),'error_type':type(e).__name__},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
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
    
    filepath = None
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Read file content
        content = read_text_file(filepath)
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'A','location':'app.py:173','message':'file content read for analysis','data':{'filepath':filepath,'content_length':len(content),'filename':filename},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        
        # Analyze with Gemini
        prompts = {
            'general': f"Analyze the following text and provide insights:\n\n{content}",
            'summary': f"Provide a comprehensive summary of the following text:\n\n{content}",
            'sentiment': f"Analyze the sentiment of the following text:\n\n{content}",
            'keywords': f"Extract key topics and keywords from the following text:\n\n{content}"
        }
        
        prompt = prompts.get(analysis_type, prompts['general'])
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'C','location':'app.py:183','message':'before Gemini API call (file)','data':{'content_length':len(content),'prompt_length':len(prompt),'analysis_type':analysis_type},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        response = model.generate_content(prompt)
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'C','location':'app.py:184','message':'Gemini API response received (file)','data':{'has_text':hasattr(response,'text'),'response_type':type(response).__name__},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        
        # Get response text safely
        result_text = response.text if hasattr(response, 'text') else str(response)
        
        # Clean up temp file
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'analysis_type': analysis_type,
            'result': result_text,
            'input_length': len(content)
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing file: {str(e)}")
        if filepath and os.path.exists(filepath):
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
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'D','location':'app.py:222','message':'before chat Gemini API call','data':{'message_length':len(message),'context_length':len(context),'prompt_length':len(prompt)},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        response = model.generate_content(prompt)
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'C','location':'app.py:224','message':'chat Gemini API response received','data':{'has_text':hasattr(response,'text'),'response_type':type(response).__name__},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        
        # Get response text safely
        result_text = response.text if hasattr(response, 'text') else str(response)
        
        return jsonify({
            'success': True,
            'response': result_text
        }), 200
        
    except Exception as e:
        # #region agent log
        with open('/home/ethanzheng/Documents/Projects/Hackathons/SBHACKS2026/IGB-ai/.cursor/debug.log', 'a') as f: f.write(json.dumps({'sessionId':'debug-session','runId':'run1','hypothesisId':'C','location':'app.py:234','message':'chat exception','data':{'error':str(e),'error_type':type(e).__name__},'timestamp':int(datetime.now().timestamp()*1000)})+'\n')
        # #endregion
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({'error': f'Chat failed: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

