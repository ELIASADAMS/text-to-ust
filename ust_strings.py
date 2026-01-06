# ust_strings.py

UST_HEADER_TEMPLATE = """[#VERSION]
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
"""

REST_NOTE_TEMPLATE = """[#{note_id:04d}]
Length={length}
Lyric=R
NoteNum=60
PreUtterance=0
VoiceOverlap=0
Intensity=0
Modulation=0
PBS=0
PBW=0
StartPoint=0
Envelope=0,0,0,0,0,0,0
"""

SMALL_TSU_TEMPLATE = """[#{note_id:04d}]
Length={length}
Lyric=っ
NoteNum={root_key}
PreUtterance=0
VoiceOverlap=0
Intensity=30
Modulation=0
PBS=0
PBW=0
StartPoint=0
Envelope=0,0,0,0,0,0,0
"""

NOTE_BLOCK_TEMPLATE = """[#{note_id:04d}]
Length={length}
Lyric={lyric}
PBS={pbs}
PBW={pbw}
NoteNum={note_num}
PreUtterance={pre_utter}
VoiceOverlap={voice_overlap}
Intensity={intensity}
StartPoint=0
Envelope={envelope}
"""

TRACK_END = "\n[#TRACKEND]\n"
