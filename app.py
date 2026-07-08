import os
import time
import webbrowser
from threading import Thread
from flask import Flask, jsonify, request, render_template, send_from_directory
from face_processor import process_face
from questions import QUESTIONS, check_answer

app = Flask(__name__, template_folder='templates', static_folder='static')

# Configuration
UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure the static folder has a default avatar if upload is skipped
DEFAULT_AVATAR_PATH = os.path.join(app.static_folder, 'default_avatar.png')
# We will check or create a placeholder if it's missing (though JS will fallback to emoji, it's nice to have)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-face', methods=['POST'])
def upload_face():
    if 'face_image' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    
    file = request.files['face_image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    
    if file:
        # Create a unique filename to prevent browser caching issues
        timestamp = int(time.time())
        temp_input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{timestamp}_{file.filename}")
        output_filename = f"avatar_{timestamp}.png"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        try:
            file.save(temp_input_path)
            
            # Process face cropping
            success = process_face(temp_input_path, output_path)
            
            # Clean up temp input file
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
                
            if success:
                # Return relative web path to the cropped avatar
                avatar_url = f"/static/uploads/{output_filename}"
                return jsonify({'success': True, 'avatar_url': avatar_url})
            else:
                return jsonify({'success': False, 'error': 'Face processing failed'}), 500
        except Exception as e:
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/questions', methods=['GET'])
def get_questions():
    # Return questions list without acceptable_answers to prevent client cheating
    safe_questions = []
    for q in QUESTIONS:
        q_copy = q.copy()
        if 'acceptable_answers' in q_copy:
            del q_copy['acceptable_answers']
        safe_questions.append(q_copy)
    return jsonify(safe_questions)

@app.route('/api/check-answer', methods=['POST'])
def verify_answer():
    data = request.get_json() or {}
    question_id = data.get('question_id')
    user_answer = data.get('user_answer', '').strip()
    
    if not question_id:
        return jsonify({'error': 'Missing question_id'}), 400
        
    # Find question to retrieve detailed explanation
    question = next((q for q in QUESTIONS if q['id'] == question_id), None)
    if not question:
        return jsonify({'error': 'Question not found'}), 404
        
    is_correct = check_answer(question_id, user_answer)
    
    return jsonify({
        'correct': is_correct,
        'explanation': question['explanation']
    })

def open_browser():
    # Wait for Flask to boot up
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Start thread to open browser if running locally
    # (Avoid opening if running in specific environments like Colab/Docker)
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        # Only launch browser on the parent process, not on Werkzeug reloader threads
        print("Launching local browser in background...")
        Thread(target=open_browser, daemon=True).start()
        
    app.run(host='0.0.0.0', port=5000, debug=True)
