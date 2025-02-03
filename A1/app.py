from flask import Flask, request, jsonify, redirect
import string
import random
import os
from dotenv import load_dotenv
from storage import UrlStorage

load_dotenv()

app = Flask(__name__)
storage = UrlStorage()
DOMAIN = os.getenv('DOMAIN', 'http://localhost:5000')

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing URL'}), 400
    
    original_url = data['url']
    short_code = generate_short_code()
    
    while not storage.add_url(original_url, short_code):
        short_code = generate_short_code()
    
    short_url = f"{DOMAIN}/{short_code}"
    return jsonify({'short_url': short_url}), 201

@app.route('/<short_code>')
def redirect_url(short_code):
    original_url = storage.get_url(short_code)
    if original_url:
        storage.increment_visits(short_code)
        return redirect(original_url)
    return jsonify({'error': 'Short URL not found'}), 404

@app.route('/api/stats/<short_code>')
def get_stats(short_code):
    visits = storage.get_stats(short_code)
    if visits is not None:
        return jsonify({'short_code': short_code, 'visits': visits})
    return jsonify({'error': 'Short URL not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)