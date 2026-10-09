from pathlib import Path
import base64, json
ROOT=Path(__file__).resolve().parent
def data(path):return base64.b64encode(path.read_bytes()).decode()
html=(ROOT/'motion.template.html').read_text()
values=dict(FONT_REG=data(ROOT/'assets/space-regular.ttf'),FONT_BOLD=data(ROOT/'assets/space-bold.ttf'),
    AUDIO=data(ROOT/'work/audio-final.m4a'),LOGO=data(ROOT/'assets/logo-frenty.png'),
    HERO=data(ROOT/'assets/pdv-hero.png'),STORY=(ROOT/'roteiro.json').read_text(),
    GRID=(ROOT/'beats.json').read_text(),CAPS=(ROOT/'legendas.json').read_text())
for k,v in values.items():html=html.replace('__'+k+'__',v)
assert '__FONT_' not in html
(ROOT/'index.html').write_text(html)
print(json.dumps({'file':'index.html','size':(ROOT/'index.html').stat().st_size,'duration':json.loads(values['STORY'])['duration']}))
