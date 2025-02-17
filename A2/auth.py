from flask import Blueprint, request, jsonify, Flask
import bcrypt
from user_storage import UserStorage
from jwt import generate_jwt, validate_jwt
from functools import wraps

auth_bp = Blueprint('auth', __name__)
user_storage = UserStorage()
JWT_SECRET = "your-strong-secret-key-here"

@auth_bp.route('/users', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Missing username or password"}), 400

    username = data['username']
    password = data['password'].encode('utf-8')
    hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

    if user_storage.add_user(username, hashed_pw):
        return jsonify({"message": "User created"}), 201
    else:
        return jsonify({"error": "duplicate"}), 409

@auth_bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '').encode('utf-8')

    user = user_storage.get_user(username)
    if not user or not bcrypt.checkpw(password, user[1].encode('utf-8')):
        return jsonify({"error": "forbidden"}), 403

    jwt_token = generate_jwt(user[0], JWT_SECRET)
    return jsonify({"token": jwt_token}), 200

@auth_bp.route('/users', methods=['PUT'])
def update_password():
    data = request.get_json()
    username = data.get('username', '')
    old_password = data.get('old', '').encode('utf-8')
    new_password = data.get('new', '').encode('utf-8')

    user = user_storage.get_user(username)
    if not user or not bcrypt.checkpw(old_password, user[1].encode('utf-8')):
        return jsonify({"error": "forbidden"}), 403

    new_hashed_pw = bcrypt.hashpw(new_password, bcrypt.gensalt()).decode('utf-8')
    if user_storage.update_user_password(username, new_hashed_pw):
        return jsonify({"message": "Password updated"}), 200
    else:
        return jsonify({"error": "Internal error"}), 500

@auth_bp.route('/validate_token', methods=['POST'])
def validate_token():
    token = request.json.get('token', '')
    user_id = validate_jwt(token, JWT_SECRET)
    if user_id:
        return jsonify({"valid": True, "user_id": user_id}), 200
    else:
        return jsonify({"valid": False}), 403

def jwt_required(func):
    """JWT验证装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        user_id = validate_jwt(token, JWT_SECRET)
        if not user_id:
            return jsonify({"error": "Invalid token"}), 403
        return func(user_id, *args, **kwargs)
    return wrapper

if __name__ == '__main__':
    app = Flask(__name__)
    app.register_blueprint(auth_bp)
    app.run(port=5001, debug=True)