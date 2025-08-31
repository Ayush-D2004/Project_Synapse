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

# --- Enhanced Image Analysis with Real AI Vision ---
def analyze_image_content(image):
    """
    Real image analysis using Google Gemini Vision API for customer service evidence.
    Analyzes actual uploaded images to extract relevant information.
    """
    try:
        # Import Google Generative AI for vision
        import google.generativeai as genai
        from config import load_api_key
        
        # Load API key (same as used for the chat agent)
        load_api_key()
        
        # Configure Gemini for vision analysis
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Convert PIL image to bytes for API
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Prepare the image for Gemini
        image_data = {
            'mime_type': 'image/png',
            'data': img_buffer.getvalue()
        }
        
        # Detailed prompt for food delivery analysis
        analysis_prompt = """
You are an AI assistant for Grab food delivery service analyzing customer complaint images. 

Analyze this image and provide a detailed assessment for customer service purposes. Focus on:

1. **Food Condition**: Is the food spilled, damaged, cold, or in poor condition?
2. **Order Accuracy**: Does this match what a customer might have ordered? Any obvious wrong items?
3. **Packaging Issues**: Is packaging damaged, opened, or compromised?
4. **Delivery Issues**: Any signs of delivery problems, weather damage, or mishandling?
5. **Quality Concerns**: Food freshness, temperature indicators, presentation issues?

Provide your analysis in this exact JSON format:
{
    "issue_type": "food_damage|wrong_order|quality_issue|delivery_proof|packaging_issue",
    "description": "Clear description of what you observe in the image",
    "evidence": {
        "condition": "what condition the food/items are in",
        "accuracy": "whether items match typical food orders",
        "damage_level": "none|minor|moderate|severe",
        "compensation_recommended": "suggested resolution based on what you see"
    },
    "confidence": 0.85
}

Analyze the actual image content - don't make up scenarios. Base your assessment only on what you can see.
"""
        
        # Get analysis from Gemini Vision
        response = model.generate_content([analysis_prompt, image_data])
        analysis_text = response.text.strip()
        
        # Try to parse JSON response
        import json
        try:
            # Extract JSON from response (in case there's extra text)
            start = analysis_text.find('{')
            end = analysis_text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = analysis_text[start:end]
                analysis_data = json.loads(json_str)
            else:
                raise ValueError("No valid JSON found")
                
        except (json.JSONDecodeError, ValueError):
            # Fallback: parse the text response manually
            analysis_data = {
                "issue_type": "general_complaint",
                "description": f"AI Analysis: {analysis_text[:200]}...",
                "evidence": {
                    "condition": "requires human review",
                    "accuracy": "image uploaded for complaint",
                    "damage_level": "moderate",
                    "compensation_recommended": "standard resolution"
                },
                "confidence": 0.75
            }
        
        # Format for return
        from datetime import datetime
        return {
            "analysis": analysis_data["description"],
            "evidence": analysis_data["evidence"],
            "image_metadata": {
                "dimensions": f"{image.size[0]}x{image.size[1]}",
                "analyzed_at": datetime.now().isoformat(),
                "analysis_confidence": analysis_data.get("confidence", 0.8),
                "analysis_type": "real_ai_vision"
            }
        }
        
    except Exception as e:
        print(f"Vision API error: {e}")
        # Fallback to basic analysis
        from datetime import datetime
        return {
            "analysis": f"Image uploaded by customer. Technical analysis unavailable. Manual review recommended for: {e}",
            "evidence": {
                "condition": "customer provided visual evidence",
                "accuracy": "requires manual verification", 
                "damage_level": "moderate",
                "compensation_recommended": "standard customer service resolution"
            },
            "image_metadata": {
                "dimensions": f"{image.size[0]}x{image.size[1]}",
                "analyzed_at": datetime.now().isoformat(),
                "analysis_confidence": 0.6,
                "analysis_type": "fallback_analysis"
            }
        }

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
                
                # Enhanced image analysis
                image_analysis = analyze_image_content(image)
                image_description = image_analysis["analysis"]
                
                user_message['image'] = img_base64
                user_message['image_description'] = image_description
                user_message['image_analysis'] = image_analysis
                user_message['has_image'] = True
                
                # Add detailed image context to agent input
                agent_input_content.append(f"Image Evidence: {image_description}")
                agent_input_content.append(f"Evidence Details: {image_analysis['evidence']}")
                
            except Exception as e:
                print(f"Error processing image: {e}")
                user_message['image_error'] = str(e)
        
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
            if 'image_analysis' in user_message:
                # Store comprehensive image context in memory
                image_context = f"""Image Evidence Analyzed:
- Description: {user_message['image_description']}
- Evidence: {user_message['image_analysis']['evidence']}
- Analysis Confidence: {user_message['image_analysis']['image_metadata']['analysis_confidence']:.1%}
- Analyzed at: {user_message['image_analysis']['image_metadata']['analyzed_at']}"""
                session['memory'].append({'role': 'system', 'content': image_context})
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
