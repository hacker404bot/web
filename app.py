# app.py
from flask import Flask, request, jsonify, render_template
import cv2
import numpy as np
from gtts import gTTS
import os

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

BRAILLE_DICT = {
    (1, 0, 0, 0, 0, 0): 'A', (1, 1, 0, 0, 0, 0): 'B',
    (1, 0, 0, 1, 0, 0): 'C', (1, 0, 0, 1, 1, 0): 'D',
    (1, 0, 0, 0, 1, 0): 'E', (1, 1, 0, 1, 0, 0): 'F',
    (1, 1, 0, 1, 1, 0): 'G', (1, 1, 0, 0, 1, 0): 'H',
    (0, 1, 0, 1, 0, 0): 'I', (0, 1, 0, 1, 1, 0): 'J',
    (1, 0, 1, 0, 0, 0): 'K', (1, 1, 1, 0, 0, 0): 'L',
    (1, 0, 1, 1, 0, 0): 'M', (1, 0, 1, 1, 1, 0): 'N',
    (1, 0, 1, 0, 1, 0): 'O', (1, 1, 1, 1, 0, 0): 'P',
    (1, 1, 1, 1, 1, 0): 'Q', (1, 1, 1, 0, 1, 0): 'R',
    (0, 1, 1, 1, 0, 0): 'S', (0, 1, 1, 1, 1, 0): 'T',
    (1, 0, 1, 0, 0, 1): 'U', (1, 1, 1, 0, 0, 1): 'V',
    (0, 1, 0, 1, 1, 1): 'W', (1, 0, 1, 1, 0, 1): 'X',
    (1, 0, 1, 1, 1, 1): 'Y', (1, 0, 1, 0, 1, 1): 'Z'
}

def preprocess_image(image):
    image = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
    return thresh

def extract_braille_dots(image):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    dot_positions = [cv2.boundingRect(cnt)[:2] for cnt in contours]
    return sorted(dot_positions, key=lambda pos: (pos[1], pos[0]))

def generate_braille_matrix(dot_positions):
    matrix = [[0, 0], [0, 0], [0, 0]]
    if len(dot_positions) >= 2:
        x_values = [pos[0] for pos in dot_positions]
        col_threshold = np.median(x_values)
    else:
        col_threshold = 15
    left_column = sorted([p for p in dot_positions if p[0] < col_threshold], key=lambda p: p[1])
    right_column = sorted([p for p in dot_positions if p[0] >= col_threshold], key=lambda p: p[1])
    for i, col in enumerate([left_column, right_column]):
        for j, dot in enumerate(col[:3]):
            matrix[j][i] = 1
    for row in matrix:
        row[0], row[1] = row[1], row[0]
    return matrix

def matrix_to_braille_text(matrix):
    flattened_tuple = tuple(sum(matrix, []))
    return BRAILLE_DICT.get(flattened_tuple, '?')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    image = request.files['image']
    processed_image = preprocess_image(image)
    dot_positions = extract_braille_dots(processed_image)
    braille_matrix = generate_braille_matrix(dot_positions)
    text = matrix_to_braille_text(braille_matrix)

    audio_file = "static/braille_audio.mp3"
    if text != '?':
        tts = gTTS(text=text, lang='en')
        tts.save(audio_file)

    return jsonify({'text': text, 'audio': '/static/braille_audio.mp3' if text != '?' else None})

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    app.run(debug=True,port=5503)