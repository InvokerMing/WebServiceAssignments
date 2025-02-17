from flask import Flask, request, jsonify
from auth import auth_bp, jwt_required
from url_storage import UrlStorage
import string
import random
import re

app = Flask(__name__)
app.register_blueprint(auth_bp, url_prefix='/auth')  # register the auth_bp blueprint
storage = UrlStorage()


def generate_short_code(length=4):
    # random.seed(42)
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/', methods=['POST'])
@jwt_required
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

@app.route('/<int:url_id>', methods=['GET'])
def get_url_by_id(url_id):
    url_data = storage.get_url(url_id)
    if url_data:
        return jsonify({'value': url_data['original_url']}), 301
    return jsonify({'error': 'URL not found'}), 404

# @app.route('/<int:url_id>', methods=['GET'])
# def redirect_to_original(url_id):
#     url_data = storage.get_url(url_id)
#     if url_data:
#         return jsonify({'value': url_data['original_url']}), 301
#     return jsonify({'error': 'URL not found'}), 404

@app.route('/my-urls', methods=['GET'])
@jwt_required
def get_user_urls(user_id):
    urls = storage.get_urls_by_user(user_id)
    return jsonify({'urls': urls}), 200

@app.route('/<int:url_id>', methods=['PUT', 'DELETE'])
@jwt_required
def manage_url(user_id, url_id): # update or delete
    url_data = storage.get_url(url_id)
    if not url_data:
        return jsonify({'error': 'URL not found'}), 404
    
    if url_data['user_id'] != user_id:
        return jsonify({'error': 'Forbidden: Not the owner'}), 403

    if request.method == 'PUT':
        data = request.get_json(force=True)
        if not data:
            return jsonify({'error': 'Missing JSON body'}), 400
        
        new_url = data.get('url')
        if not new_url:
            return jsonify({'error': 'Missing URL'}), 400
        if not check_URL(new_url):
            return jsonify({'error': 'Invalid URL'}), 400
        
        if storage.update_url(url_id, new_url):
            return jsonify({'message': 'Updated'}), 200
        else:
            return jsonify({'error': 'Internal error'}), 500
    
    elif request.method == 'DELETE':
        storage.delete_url(url_id)
        return '', 204

@app.route('/', methods=['DELETE'])
@jwt_required
def delete_all_urls(user_id):
    deleted_count = storage.delete_all_by_user(user_id)
    return "", 404

@app.route('/', methods=['GET'])
@jwt_required
def get_all_urls(user_id):
    urls = storage.get_urls_by_user(user_id)
    return jsonify({'urls': urls}), 200

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