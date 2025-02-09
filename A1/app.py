from flask import Flask, request, jsonify
import string
import random
from storage import UrlStorage
import re

app = Flask(__name__)
storage = UrlStorage()

def generate_short_code(length=4):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/', methods=['POST'])
def create_short_url():
    data = request.get_json()
    if not data or 'value' not in data:
        return jsonify({'error': 'Missing URL'}), 400
    
    code_length = 4
    max_short_codes_4 = 62**4

    if storage.count_codes_by_length(4) >= max_short_codes_4:
        code_length = 6

    short_code = generate_short_code(code_length)
    url_id = None
    original_url = data['value']

    if not checkURL(original_url):
        return jsonify({'error': 'Invalid URL'}), 400

    while not url_id:
        if code_length == 4 and storage.count_codes_by_length(4) >= max_short_codes_4:
            code_length = 6
        short_code = generate_short_code(code_length)
        url_id = storage.add_url(original_url, short_code)

    return jsonify({'id': url_id}), 201

@app.route('/<int:url_id>', methods=['GET'])
def get_url(url_id):
    original_url = storage.get_url(url_id)
    print("url: " + original_url)
    if original_url:
        return jsonify({'value': original_url}), 301
    return jsonify({'error': 'URL not found'}), 404

@app.route('/<int:url_id>', methods=['PUT'])
def update_url(url_id):
    # mind data may be not a valid JSON
    data = request.get_json(force=True, silent=True)

    if not data or 'url' not in data:
        return jsonify({'error': 'Invalid or missing JSON data'}), 400

    # check if id is valid
    if not storage.get_url(url_id):
        return jsonify({'error': 'URL not found'}), 404

    # check if url is valid
    if not data['url'].strip() or not data['url'].startswith(('http://', 'https://')):
        return jsonify({'error': 'Invalid URL'}), 400

    if storage.update_url(url_id, data['url']):
        return jsonify({'message': 'Updated'}), 200
    return jsonify({'error': 'URL not found'}), 404

@app.route('/<int:url_id>', methods=['DELETE'])
def delete_url(url_id):
    if storage.delete_url(url_id):
        return '', 204
    return jsonify({'error': 'URL not found'}), 404

@app.route('/', methods=['GET'])
def get_all_urls():
    urls = storage.get_all_urls()
    if not urls:
        return jsonify({'value': None}), 404
    return jsonify(urls), 200

@app.route('/', methods=['DELETE'])
def delete_all_urls():
    deleted_count = storage.delete_all()
    return "", 404

def checkURL(url):
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