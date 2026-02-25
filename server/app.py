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

# --- SUMMARY ROUTES ---

@app.route('/summaries', methods=['GET'])
@token_required
def get_summaries(current_user):
    """Return all summaries for the logged-in user, newest first."""
    try:
        response = (
            supabase.table('summaries')
            .select("summary_id, summary_text, language, created_at")
            .eq('user_id', current_user)
            .order('created_at', desc=True)
            .execute()
        )
        return jsonify(response.data), 200
    except Exception as e:
        print(f"Get Summaries Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/summaries/<summary_id>', methods=['GET'])
@token_required
def get_summary(current_user, summary_id):
    """Return a single summary (only if it belongs to the current user)."""
    try:
        response = (
            supabase.table('summaries')
            .select("summary_id, summary_text, language, created_at")
            .eq('summary_id', summary_id)
            .eq('user_id', current_user)
            .single()
            .execute()
        )
        if not response.data:
            return jsonify({'error': 'Summary not found'}), 404
        return jsonify(response.data), 200
    except Exception as e:
        print(f"Get Summary Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/compare', methods=['POST'])
@token_required
def compare_summaries(current_user):
    """
    Accepts a list of summary objects { id, fullText } from the frontend,
    verifies ownership, sorts by creation date, and runs a Groq comparison.
    """
    body = request.get_json()
    summaries = body.get('summaries', [])

    if len(summaries) < 2:
        return jsonify({'error': 'At least 2 summaries are required'}), 400

    try:
        # Fetch creation dates from Supabase to ensure correct ordering and ownership
        ids = [s['id'] for s in summaries]
        db_rows = (
            supabase.table('summaries')
            .select("summary_id, created_at, summary_text")
            .in_('summary_id', ids)
            .eq('user_id', current_user)
            .execute()
        )

        if not db_rows.data or len(db_rows.data) < 2:
            return jsonify({'error': 'Could not verify ownership of summaries'}), 403

        # Sort by created_at ascending so index 0 = oldest
        sorted_rows = sorted(db_rows.data, key=lambda r: r['created_at'])

        older_text = sorted_rows[0]['summary_text']
        newer_text = sorted_rows[-1]['summary_text']

        result = diagnostic_system.generate_comparison(older_text, newer_text)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        print(f"Compare Error: {e}")
        return jsonify({'error': str(e)}), 500


# --- AI ROUTES ---

@app.route('/analyze', methods=['POST'])
@token_required
def analyze_medical_report(current_user):
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF file part'}), 400
    
    pdf_file = request.files.get('pdf')

    pdf_text = None
    image_findings = None
    
    try:
        # Process PDF if uploaded
        if pdf_file and pdf_file.filename != '':
            filename = secure_filename(pdf_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            pdf_file.save(filepath)
            
            pdf_text = diagnostic_system.extract_pdf_text(filepath)
            
            # Extract Image from PDF
            extracted_image_path = diagnostic_system.extract_images_from_pdf(filepath)

            if extracted_image_path:
                 extract_img_filename = os.path.basename(extracted_image_path)
                 print(f"Extracted Image: {extract_img_filename}")
                 image_findings = diagnostic_system.analyze_image(extracted_image_path)
                 
                 # Clean up extracted image
                 if os.path.exists(extracted_image_path):
                     os.remove(extracted_image_path)
            
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
