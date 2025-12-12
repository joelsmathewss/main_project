from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import bcrypt
import jwt
import datetime
from functools import wraps
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)
CORS(app)

# Supabase Configuration
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY missing from .env")

supabase: Client = create_client(url, key)

# JWT Middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('token')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            # Verify using our custom secret OR Supabase's JWT secret if you switch to their auth later
            # For now keeping our custom JWT logic as per previous implementation
            data = jwt.decode(token, os.getenv('jwtSecret'), algorithms=["HS256"])
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    age = data.get('age')
    sex = data.get('sex')

    try:
        # Check if user exists using Supabase Client
        existing_user = supabase.table('users').select("*").eq('user_email', email).execute()
        
        if existing_user.data and len(existing_user.data) > 0:
            return jsonify("User already exists"), 401

        # Hash password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        # Insert user
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

        # Generate Token
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
        # Fetch user
        user_response = supabase.table('users').select("*").eq('user_email', email).execute()
        
        if not user_response.data or len(user_response.data) == 0:
            return jsonify("Password or Email is incorrect"), 401
            
        user = user_response.data[0]

        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user['user_password'].encode('utf-8')):
            # Generate Token
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
def is_verify():
    return jsonify(True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
