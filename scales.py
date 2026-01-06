"""Musical scales for melody generation"""

SCALES = {
    # 12-note (Chromatic)
    'Chromatic': list(range(12)),

    # 9-note (Nonatonic Blues)
    'Nonatonic Blues': [0, 2, 3, 5, 6, 7, 8, 10, 11],

    # 8-note (Octatonic)
    'Octatonic': [0, 1, 3, 4, 6, 7, 9, 10],

    # 7-note (Diatonic)
    'C Major': [0, 2, 4, 5, 7, 9, 11], 'C Minor': [0, 2, 3, 5, 7, 8, 10],
    'D Major': [2, 4, 6, 7, 9, 11, 1], 'D Minor': [2, 4, 5, 7, 9, 10, 0],
    'E Major': [4, 6, 8, 9, 11, 1, 3], 'E Minor': [4, 6, 7, 9, 11, 0, 2],
    'F Major': [5, 7, 9, 10, 0, 2, 4], 'F Minor': [5, 7, 8, 10, 0, 1, 3],
    'G Major': [7, 9, 11, 0, 2, 4, 6], 'G Minor': [7, 9, 10, 0, 2, 3, 5],
    'A Major': [9, 11, 1, 2, 4, 6, 8], 'A Minor': [9, 11, 0, 2, 4, 5, 7],

    # 6-note (Hexatonic)
    'Whole Tone': [0, 2, 4, 6, 8, 10],
    'Hexatonic Blues': [0, 3, 5, 6, 9, 10],

    # 5-note (Pentatonic)
    'Major Pentatonic': [0, 2, 4, 7, 9],
    'Minor Pentatonic': [0, 3, 5, 7, 10],

    # 4-note (Tetratonic)
    'Tetratonic': [0, 4, 7, 11]
}
