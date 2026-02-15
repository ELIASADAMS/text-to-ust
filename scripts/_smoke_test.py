import sys
import traceback

# Ensure src is on path
import os
sys.path.insert(0, os.path.abspath('src'))

try:
    from hiro_ust.core import HiroUSTProcessor, GeneratorConfig
    cfg = GeneratorConfig(tempo=120, scale='Major Pentatonic')
    proc = HiroUSTProcessor(cfg)
    ust = proc.process_lyrics("きゃっきゃ", "SmokeTest", output_format='ust')
    print('UST generated (first 400 chars):')
    print(ust[:400])
except Exception as e:
    print('Smoke test failed:')
    traceback.print_exc()
    raise

