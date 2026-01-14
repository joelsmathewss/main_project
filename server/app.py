from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import bcrypt
import jwt
import datetime
from functools import wraps
from supabase import create_client, Client
from werkzeug.utils import secure_filename
from models.model import MedicalDiagnosticSystem

load_dotenv()

app = Flask(__name__)
CORS(app)

# Supabase Configuration
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY missing from .env")

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    print(f"Supabase Connection Error: {e}")

# Initialize AI System
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") 
diagnostic_system = MedicalDiagnosticSystem(GROQ_API_KEY)

# Upload Config
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# JWT Middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('token')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            data = jwt.decode(token, os.getenv('jwtSecret'), algorithms=["HS256"])
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 403

        return f(data['user']['id'], *args, **kwargs)

    return decorated

# --- AUTH ROUTES ---

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    age = data.get('age')
    sex = data.get('sex')

    try:
        existing_user = supabase.table('users').select("*").eq('user_email', email).execute()
        
        if existing_user.data and len(existing_user.data) > 0:
            return jsonify("User already exists"), 401

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        new_user_data = {
            "user_fullname": name,
            "user_email": email,
            "user_password": hashed_password,
            "user_age": age,
            "user_sex": sex
        }
        
        insert_response = supabase.table('users').insert(new_user_data).execute()
        
        if not insert_response.data:
             return jsonify("Failed to create user"), 500
             
        new_user_id = insert_response.data[0]['user_id']

        token = jwt.encode({
            'user': {'id': new_user_id},
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, os.getenv('jwtSecret'), algorithm="HS256")

        return jsonify({'token': token})

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify("Server Error"), 500

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        user_response = supabase.table('users').select("*").eq('user_email', email).execute()
        
        if not user_response.data or len(user_response.data) == 0:
            return jsonify("Password or Email is incorrect"), 401
            
        user = user_response.data[0]

        if bcrypt.checkpw(password.encode('utf-8'), user['user_password'].encode('utf-8')):
            token = jwt.encode({
                'user': {'id': user['user_id']},
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }, os.getenv('jwtSecret'), algorithm="HS256")
            
            return jsonify({'token': token})
        else:
            return jsonify("Password or Email is incorrect"), 401

    except Exception as e:
        print(f"Login Error: {e}")
        return jsonify("Server Error"), 500

@app.route('/auth/is-verify', methods=['GET'])
@token_required
def is_verify(current_user):
    return jsonify(True)

# --- AI ROUTES ---

@app.route('/analyze', methods=['POST'])
@token_required
def analyze_medical_report(current_user):
    if 'pdf' not in request.files and 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    pdf_file = request.files.get('pdf')
    image_file = request.files.get('image')

    pdf_text = None
    image_findings = None
    
    try:
        # Process PDF if uploaded
        if pdf_file and pdf_file.filename != '':
            filename = secure_filename(pdf_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            pdf_file.save(filepath)
            
            pdf_text = diagnostic_system.extract_pdf_text(filepath)
            
            if os.path.exists(filepath):
                os.remove(filepath)

        # Process Image if uploaded
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(filepath)
            
            image_findings = diagnostic_system.analyze_image(filepath)
            
            if os.path.exists(filepath):
                os.remove(filepath)

        # Generate Summary
        if not pdf_text and not image_findings:
             return jsonify({'error': 'No valid data extracted from files'}), 400

        # Get language from request (default to English)
        language = request.form.get('language', 'English')
        summary = diagnostic_system.generate_summary(pdf_text, image_findings, language)

        # Store summary in Supabase
        try:
            summary_data = {
                "user_id": current_user,
                "summary_text": summary,
                "language": language
            }
            supabase.table('summaries').insert(summary_data).execute()
        except Exception as e:
            print(f"Error saving summary to Supabase: {e}")
            # We continue even if saving fails, as the user still wants the result

        return jsonify({
            'summary': summary,
            'details': image_findings
        })

    except Exception as e:
        print(f"Analysis Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
