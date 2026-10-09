from pathlib import Path
import hashlib, json, shutil, zipfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output'
OUT.mkdir(parents=True, exist_ok=True)
story = json.loads((ROOT / 'roteiro.json').read_text())
lines = ['Frenty | F-PDV | Motion narrado', 'Duração: 52 segundos | 1080 × 1920 | 30 fps', '']
for i, scene in enumerate(story['segments'], 1):
    lines.extend([f"{i:02d}. {scene['start']:05.1f}s – {scene['end']:05.1f}s", scene['title'].replace('\n', ' '), scene['text'], ''])
(ROOT / 'roteiro.txt').write_text('\n'.join(lines), encoding='utf-8')
html = OUT / 'frenty-f-pdv-motion.html'
shutil.copyfile(ROOT / 'index.html', html)
names = ['index.html', 'motion.template.html', 'build.py', 'render.mjs', 'contact.py', 'narracao.py', 'audio.py', 'package.py', 'roteiro.json', 'roteiro.txt', 'beats.json', 'legendas.json', 'legendas.srt', 'qa-review.json', 'verification.json', 'README.md', 'source.md', 'prompts.md', 'postagem.txt']
files = [ROOT / name for name in names]
files.extend(sorted((ROOT / 'assets').glob('*')))
files.extend(ROOT / 'work' / name for name in ['narracao.wav', 'trilha-original.wav', 'audio-final.wav', 'audio-final.m4a'])
files.extend(sorted((ROOT / 'work').glob('voice-*.mp3')))
files.extend(sorted((ROOT / 'work').glob('voice-*.jsonl')))
files.extend(sorted((ROOT / 'qa' / 'v2').glob('contact-*.jpg')))
files.append(ROOT / 'qa' / 'encoded-check.jpg')
assert len(set(files)) == len(files)
assert all(p.is_file() and p.stat().st_size > 0 for p in files)
zip_path = OUT / 'frenty-f-pdv-editavel.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as package:
    for p in files:
        package.write(p, str(Path('frenty-f-pdv') / p.relative_to(ROOT)))
with zipfile.ZipFile(zip_path) as package:
    assert package.testzip() is None
    assert len(package.namelist()) == len(files)
summary = []
for p in [OUT / 'frenty-f-pdv-motion-52s.mp4', html, zip_path]:
    summary.append({'file': p.name, 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
(ROOT / 'work' / 'delivery-manifest.json').write_text(json.dumps(summary, indent=2))
print(json.dumps({'files': summary, 'zip_entries': len(files), 'zip_crc': 'passed'}, ensure_ascii=False))
