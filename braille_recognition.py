import cv2
import numpy as np

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

def process_braille_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    dot_positions = sorted([cv2.boundingRect(cnt)[:2] for cnt in contours], key=lambda pos: (pos[1], pos[0]))

    matrix = [[0, 0], [0, 0], [0, 0]]
    col_threshold = np.median([x for x, _ in dot_positions]) if dot_positions else 15

    left = sorted([p for p in dot_positions if p[0] < col_threshold], key=lambda p: p[1])
    right = sorted([p for p in dot_positions if p[0] >= col_threshold], key=lambda p: p[1])

    for i, col in enumerate([left, right]):
        for j, dot in enumerate(col[:3]):
            matrix[j][i] = 1

    flattened = tuple(sum(matrix, []))
    return BRAILLE_DICT.get(flattened, "?")
