# romaji_dict.py - Hepburn Romanization to Hiragana mapping
ROMAJI_MAP = {
    # Vowels
    'a': 'あ', 'i': 'い', 'u': 'う', 'e': 'え', 'o': 'お',

    # K/G row
    'ka': 'か', 'ki': 'き', 'ku': 'く', 'ke': 'け', 'ko': 'こ',
    'ga': 'が', 'gi': 'ぎ', 'gu': 'ぐ', 'ge': 'げ', 'go': 'ご',
    'kya': 'きゃ', 'kyu': 'きゅ', 'kyo': 'きょ',
    'gya': 'ぎゃ', 'gyu': 'ぎゅ', 'gyo': 'ぎょ',

    # S/Z row
    'sa': 'さ', 'shi': 'し', 'su': 'す', 'se': 'せ', 'so': 'そ',
    'za': 'ざ', 'ji': 'じ', 'zu': 'ず', 'ze': 'ぜ', 'zo': 'ぞ',
    'sha': 'しゃ', 'shu': 'しゅ', 'sho': 'しょ',
    'ja': 'じゃ', 'ju': 'じゅ', 'jo': 'じょ',
    'cha': 'ちゃ', 'chu': 'ちゅ', 'cho': 'ちょ',  # ch- treated as ja/ja/ja variant

    # T/D row
    'ta': 'た', 'chi': 'ち', 'tsu': 'つ', 'te': 'て', 'to': 'と',
    'da': 'だ', 'ji_t': 'ぢ', 'zu_t': 'づ', 'de': 'で', 'do': 'ど',

    # N row
    'na': 'な', 'ni': 'に', 'nu': 'ぬ', 'ne': 'ね', 'no': 'の',
    'nya': 'にゃ', 'nyu': 'にゅ', 'nyo': 'にょ',

    # H/B/P row
    'ha': 'は', 'hi': 'ひ', 'fu': 'ふ', 'he': 'へ', 'ho': 'ほ',
    'ba': 'ば', 'bi': 'び', 'bu': 'ぶ', 'be': 'べ', 'bo': 'ぼ',
    'pa': 'ぱ', 'pi': 'ぴ', 'pu': 'ぷ', 'pe': 'ぺ', 'po': 'ぽ',
    'hya': 'ひゃ', 'hyu': 'ひゅ', 'hyo': 'ひょ',
    'bya': 'びゃ', 'byu': 'びゅ', 'byo': 'びょ',
    'pya': 'ぴゃ', 'pyu': 'ぴゅ', 'pyo': 'ぴょ',

    # M row
    'ma': 'ま', 'mi': 'み', 'mu': 'む', 'me': 'め', 'mo': 'も',
    'mya': 'みゃ', 'myu': 'みゅ', 'myo': 'みょ',

    # Y row
    'ya': 'や', 'yu': 'ゆ', 'yo': 'よ',

    # R row
    'ra': 'ら', 'ri': 'り', 'ru': 'る', 're': 'れ', 'ro': 'ろ',
    'rya': 'りゃ', 'ryu': 'りゅ', 'ryo': 'りょ',

    # W row
    'wa': 'わ', 'wo': 'を',
    'wi': 'うぃ', 'we': 'うぇ',  # Extended

    # N (nasal)
    'n': 'ん',

    # Small tsu (sokuon/gemination)
    'っ': 'っ',

    # Prolonged sound
    '-': 'ー',

    # Long vowels (Hepburn style)
    'ā': 'あー', 'ī': 'いー', 'ū': 'うー', 'ē': 'えー', 'ō': 'おー',
    'aa': 'ああ', 'ii': 'いい', 'uu': 'うう', 'ee': 'ええ', 'oo': 'おお',
}

# Common extended mappings
EXTENDED_MAP = {
    'tsa': 'つぁ', 'tsi': 'つぃ', 'tse': 'つぇ',
    'l': 'る',  # Common romaji approximation
}
