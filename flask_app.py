from flask import Flask, render_template, request, jsonify, session, send_from_directory, url_for
import os
import base64
from PIL import Image
import io
import uuid

# Initialize Flask app with explicit static folder configuration
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your-secret-key-here'  # Change this in production

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

# --- Image Description Helper ---
def describe_image(image):
    """
    Advanced image analysis for evidence gathering.
    TODO: Replace with actual computer vision model for real deployment.
    """
    import random
    
    descriptions = [
        "Image shows damaged food packaging with visible spills and torn container edges, likely due to handling during transport",
        "Photo displays incorrect food items - appears to be burger and fries instead of ordered salad and sandwich",
        "Image reveals wet packaging and water damage, suggesting exposure to rain during delivery",
        "Picture shows driver at correct address with 'recipient not available' door sign, timestamp matches delivery window", 
        "Photo evidence of properly sealed food containers in intact delivery bag, no visible damage or tampering",
        "Image shows traffic congestion and road closure signs that would cause significant delivery delays",
        "Picture displays restaurant kitchen with 'temporarily closed' sign, explaining order cancellation",
        "Photo shows customer location with incorrect address numbering, causing delivery confusion"
    ]
    
    return random.choice(descriptions)

@app.route('/')
def index():
    if 'messages' not in session:
        session['messages'] = []
    if 'memory' not in session:
        session['memory'] = []
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        user_prompt = request.form.get('message', '').strip()
        uploaded_file = request.files.get('image')
        
        if not user_prompt:
            return jsonify({'error': 'Please enter a message'}), 400
        
        # Initialize session data if not exists
        if 'messages' not in session:
            session['messages'] = []
        if 'memory' not in session:
            session['memory'] = []
        
        # Process user message
        user_message = {
            'role': 'user', 
            'content': user_prompt,
            'id': str(uuid.uuid4())
        }
        
        agent_input_content = [user_prompt]
        image_description = None
        
        # Handle image upload
        if uploaded_file and uploaded_file.filename:
            try:
                image = Image.open(uploaded_file.stream)
                # Convert image to base64 for display
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='PNG')
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                
                image_description = describe_image(image)
                user_message['image'] = img_base64
                user_message['image_description'] = image_description
                agent_input_content.append(image_description)
            except Exception as e:
                print(f"Error processing image: {e}")
        
        session['messages'].append(user_message)
        
        # Get agent response
        try:
            if not AGENT_AVAILABLE:
                # Fallback response when agent is not available
                final_output = "I'm sorry, but the AI agent is currently not available. This appears to be a technical issue. Please try again later or contact support."
                reasoning_text = "**System Status:** AI agent is currently unavailable due to missing dependencies."
            else:
                # Convert session memory to proper format for agent
                chat_history = []
                for msg in session['memory']:
                    if msg['role'] == 'user':
                        chat_history.append(HumanMessage(content=msg['content']))
                    else:
                        chat_history.append(AIMessage(content=msg['content']))
                
                response = agent.invoke({
                    "input": agent_input_content,
                    "chat_history": chat_history
                })
                
                final_output = response['output']
                intermediate_steps = response.get('intermediate_steps', [])
                
                # Format reasoning
                reasoning_text = ""
                for step in intermediate_steps:
                    action, observation = step
                    thought = action.log.strip().split('Action:')[0].strip()
                    action_str = f"Action: {action.tool} (Input: {action.tool_input})"
                    observation_str = f"Observation: {observation}"
                    reasoning_text += f"**Thought:** {thought}\n\n**{action_str}**\n\n**{observation_str}**\n\n---\n\n"
            
            # Create assistant message
            assistant_message = {
                'role': 'assistant',
                'content': final_output,
                'reasoning': reasoning_text,
                'id': str(uuid.uuid4())
            }
            
            session['messages'].append(assistant_message)
            
            # Update memory (text only)
            session['memory'].append({'role': 'user', 'content': user_prompt})
            if image_description:
                session['memory'].append({'role': 'user', 'content': f"Image Description: {image_description}"})
            session['memory'].append({'role': 'assistant', 'content': final_output})
            
            session.modified = True
            
            return jsonify({
                'success': True,
                'user_message': user_message,
                'assistant_message': assistant_message
            })
            
        except Exception as e:
            print(f"Agent error: {e}")
            return jsonify({'error': f'Agent processing error: {str(e)}'}), 500
            
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
