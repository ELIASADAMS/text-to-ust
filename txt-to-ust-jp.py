import re

import pykakasi


def kana_to_romaji(text):
    kks = pykakasi.kakasi()
    kks.setMode('H', 'a')
    kks.setMode('K', 'a')
    conv = kks.getConverter()
    romaji = conv.do(text)
    phonemes = re.findall(r'[bcdfghjklmnpqrstvwxyz]*[aeiouyn]', romaji.lower())
    return phonemes


def text_to_ust(lyrics, project_name='Kana Project', tempo=120.00):
    phonemes = kana_to_romaji(lyrics)

    ust = f'''[#VERSION]
UST Version1.2
[#SETTING]
Tempo={tempo}
Tracks=1
ProjectName={project_name}
VoiceDir=%VOICE%
OutFile=
CacheDir=.cache
Tool1=wavtool.exe
Tool2=resampler.exe
Mode2=True
'''

    for i, phoneme in enumerate(phonemes):
        note_id = f"{i:04d}"
        ust += f'\n[#{note_id}]\n'
        ust += f'Length=480\n'
        ust += f'Lyric={phoneme}\n'
        ust += f'NoteNum=69\n'
        ust += f'PreUtterance=25\n'
        ust += f'VoiceOverlap=10\n'
        ust += f'Intensity=100\n'
        ust += f'Modulation=0\n'
        ust += f'PBS=-40\n'
        ust += f'PBW=80\n'
        ust += f'StartPoint=0\n'
        ust += f'Envelope=0,10,35,0,100,100,0\n'

    ust += '\n[#TRACKEND]\n'
    return ust


# Test with your lyrics
lyrics = 'さく ら さ く ら や よ い の そ ら'
ust_content = text_to_ust(lyrics)
with open('output.ust', 'w', encoding='utf-8-sig') as f:
    f.write(ust_content)
print('Fixed UST: output.ust - Headers now [#0000]')
