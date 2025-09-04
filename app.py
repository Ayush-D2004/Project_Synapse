from flask import Flask, render_template, request, jsonify, session, send_from_directory, url_for
import os
import base64
from PIL import Image
import io
import uuid
import tempfile
import assemblyai as aai

# Initialize Flask app with explicit static folder configuration
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configure AssemblyAI with API key from environment
try:
    from config import load_assemblyai_api_key
    aai.settings.api_key = load_assemblyai_api_key()
except Exception as e:
    print(f"Warning: AssemblyAI API key not loaded: {e}")

# Add route to serve static files explicitly (fallback)
@app.route('/static/<filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

# Test route to check if static files are accessible
@app.route('/test-image')
def test_image():
    return f"<img src='{url_for('static', filename='GRAB.jpg')}' alt='Test Image'>"

# Import agent after Flask setup to avoid circular imports
try:
    from agent_core import agent
    from langchain_core.messages import HumanMessage, AIMessage
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Agent not available: {e}")
    AGENT_AVAILABLE = False

# Initialize session data
def init_session():
    if 'messages' not in session:
        session['messages'] = []
    if 'memory' not in session:
        session['memory'] = []

@app.route('/')
def index():
    init_session()
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    init_session()
    
    try:
        # Get user input
        user_text = request.form.get('message', '').strip()
        
        if not user_text:
            return jsonify({'error': 'No message provided'}), 400
        
        # Handle image if provided
        image_file = request.files.get('image')
        user_message = {'type': 'user', 'content': user_text, 'timestamp': str(uuid.uuid4())}
        
        if image_file and image_file.filename:
            # Process image
            try:
                image = Image.open(image_file.stream)
                
                # Convert image to base64 for display
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                
                user_message['image'] = img_base64
                user_message['image_name'] = image_file.filename
                
            except Exception as e:
                print(f"Image processing error: {e}")
                return jsonify({'error': 'Failed to process image'}), 500
        
        # Store user message
        session['messages'].append(user_message)
        
        if not AGENT_AVAILABLE:
            assistant_message = {
                'type': 'assistant', 
                'content': 'I apologize, but the AI agent is currently unavailable. Please check the system configuration.',
                'timestamp': str(uuid.uuid4())
            }
        else:
            try:
                # Process with agent
                if image_file and image_file.filename:
                    # Create combined message with image context
                    user_prompt = f"Customer message: {user_text}\n[Customer has provided an image as evidence]"
                else:
                    user_prompt = user_text
                
                # Get agent response
                response = agent.invoke({
                    "input": user_prompt,
                    "chat_history": session['memory']
                })
                
                assistant_message = {
                    'type': 'assistant',
                    'content': response['output'],
                    'timestamp': str(uuid.uuid4())
                }
                
                # Update memory
                session['memory'].extend([
                    {'role': 'user', 'content': user_prompt},
                    {'role': 'assistant', 'content': response['output']}
                ])
                
            except Exception as e:
                print(f"Agent error: {e}")
                assistant_message = {
                    'type': 'assistant',
                    'content': 'I apologize, but I encountered an error processing your request. Please try again.',
                    'timestamp': str(uuid.uuid4())
                }
        
        session['messages'].append(assistant_message)
        session.modified = True
        
        return jsonify({
            'success': True,
            'user_message': user_message,
            'assistant_message': assistant_message
        })
        
    except Exception as e:
        print(f"Request error: {e}")
        return jsonify({'error': f'Request processing error: {str(e)}'}), 500

@app.route('/clear_conversation', methods=['POST'])
def clear_conversation():
    session['messages'] = []
    session['memory'] = []
    session.modified = True
    return jsonify({'success': True})

@app.route('/get_messages')
def get_messages():
    return jsonify(session.get('messages', []))

@app.route('/transcribe_audio', methods=['POST'])
def transcribe_audio():
    """
    Transcribe uploaded audio using AssemblyAI speech-to-text API
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400
            
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'success': False, 'error': 'No audio file selected'}), 400
            
        # Save uploaded audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            audio_file.save(temp_file.name)
            temp_file_path = temp_file.name
            
        try:
            # Configure AssemblyAI transcription
            config = aai.TranscriptionConfig(
                speech_model=aai.SpeechModel.universal,
                language_detection=True,  # Auto-detect language
                punctuate=True,  # Add punctuation
                format_text=True  # Format text properly
            )
            
            # Transcribe the audio
            transcriber = aai.Transcriber(config=config)
            transcript = transcriber.transcribe(temp_file_path)
            
            if transcript.status == "error":
                return jsonify({
                    'success': False, 
                    'error': f'Transcription failed: {transcript.error}'
                }), 500
                
            # Return successful transcription
            return jsonify({
                'success': True,
                'text': transcript.text,
                'confidence': transcript.confidence if hasattr(transcript, 'confidence') else 0.9
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        print(f"Transcription error: {e}")
        return jsonify({
            'success': False, 
            'error': f'Transcription processing error: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)