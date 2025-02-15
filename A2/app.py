from flask import Flask, request, jsonify
from authentication import auth_bp, jwt_required
from storage import UrlStorage
from user_storage import UserStorage
import requests
import string
import random
import re

app = Flask(__name__)
app.register_blueprint(auth_bp, url_prefix='/auth')  # register the auth_bp blueprint
storage = UrlStorage()
AUTH_SERVICE_URL = "http://localhost:5000/auth/validate_token"  # URL of the authentication service

def generate_short_code(length=4):
    # random.seed(42)
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/', methods=['POST'])
def create_short_url(user_id):
    data = request.get_json()
    if not data or 'value' not in data:
        return jsonify({'error': 'Missing URL'}), 400
    
    original_url = data['value']
    if not check_URL(original_url):
        return jsonify({'error': 'Invalid URL'}), 400
    
    code_length = 4
    max_short_codes_4 = 62**4
    if storage.count_codes_by_length(4) >= max_short_codes_4:
        code_length = 6

    short_code = None
    while not short_code:
        candidate = generate_short_code(code_length)
        if not storage.get_short_code_exists(candidate):
            short_code = candidate

    url_id = storage.add_url(original_url, short_code, user_id)
    return jsonify({
        'id': url_id,
        'short_url': f"{request.host_url}{short_code}"
    }), 201

@app.route('/<short_code>', methods=['GET'])
def redirect_to_original(short_code):
    original_url = storage.get_url_by_short_code(short_code)
    if original_url:
        return jsonify({'value': original_url}), 301
    return jsonify({'error': 'URL not found'}), 404

@app.route('/my-urls>', methods=['GET'])
def get_url(user_id):
    urls = storage.get_urls_by_user(user_id)
    return jsonify({'urls': urls}), 200

@app.route('/<int:url_id>', methods=['PUT'])
def update_url(user_id, url_id):
    # mind data may be not a valid JSON
    data = request.get_json(force=True, silent=True)

    if not data or 'url' not in data:
        return jsonify({'error': 'Invalid or missing JSON data'}), 400

    # check if id is valid  
    if not storage.get_url(url_id):
        return jsonify({'error': 'URL not found'}), 404

    # check if url is valid
    if not check_URL(data['url']):
        return jsonify({'error': 'Invalid URL'}), 400

    if storage.update_url(url_id, data['url']):
        return jsonify({'message': 'Updated'}), 200
    return jsonify({'error': 'URL not found'}), 404

@app.route('/<int:url_id>', methods=['DELETE'])
def delete_url(user_id, url_id):
    if storage.delete_url(url_id):
        return '', 204
    return jsonify({'error': 'URL not found'}), 404

@app.route('/', methods=['DELETE'])
def delete_all_urls():
    deleted_count = storage.delete_all()
    return "", 404

def get_current_user_id():
    """从请求头获取并验证 JWT"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    response = requests.post(AUTH_SERVICE_URL, json={"token": token})
    if response.status_code == 200:
        return response.json().get("user_id")
    return None

def check_URL(url):
    regex = re.compile(
        r'^(https?://)'                         # http:// or https://
        r'((([A-Za-z0-9-]+\.)+[A-Za-z]{2,})|'   # domain...
        r'localhost|'                           # localhost
        r'(\d{1,3}\.){3}\d{1,3})'               # IPv4 address
        r'(:\d+)?'                              # port
        r'(\/[^\s]*)?$'                         # paths
    )
    return re.match(regex, url) is not None

if __name__ == '__main__':
    app.run(debug=True, port=5000)