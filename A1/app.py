from flask import Flask, request, jsonify
import string
import random
from storage import UrlStorage

app = Flask(__name__)
storage = UrlStorage()

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/', methods=['POST'])
def create_short_url():
    data = request.get_json()
    if not data or 'value' not in data:
        return jsonify({'error': 'Missing URL'}), 400

    original_url = data['value']

    if not original_url.strip() or not original_url.startswith(('http://', 'https://')):
        return jsonify({'error': 'Invalid URL'}), 400

    short_code = generate_short_code()
    url_id = None

    while not url_id:
        url_id = storage.add_url(original_url, short_code)
        if not url_id:
            short_code = generate_short_code()

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
    # print(deleted_count)
    # if deleted_count == 0:
    #     return jsonify({'error': 'No URLs to delete'}), 404
    return "", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)