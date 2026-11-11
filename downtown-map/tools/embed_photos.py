"""Embed building photos into index.html as data URIs so the single file is self-contained.
Re-run after replacing any file in downtown-map/photos/."""
import base64, os, re, subprocess, tempfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
p = ROOT + 'index.html'
s = open(p).read()
ids = re.findall(r'id: "([a-z0-9-]+)", name:', s)
entries = []
tmp = tempfile.mkdtemp()
for bid in ids:
    src = ROOT + f'photos/{bid}.jpg'
    if not os.path.exists(src):
        continue
    out = os.path.join(tmp, bid + '.jpg')
    # 1000px wide is plenty for the matrix/detail sizes and keeps the HTML small
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-vf', "scale='min(1000,iw)':-2", '-q:v', '5', out], check=True)
    b64 = base64.b64encode(open(out, 'rb').read()).decode()
    entries.append(f'  "{bid}": "data:image/jpeg;base64,{b64}"')
    print(bid, os.path.getsize(out) // 1024, 'KB')
block = ('/* EMBEDDED PHOTOS — generated from the photos/ folder so this one file works on its own.\n'
         '   (Regenerate after changing a photo.) */\n'
         'const PHOTO_DATA = {\n' + ',\n'.join(entries) + '\n};\n')

# The aerial still (last frame of the flyover) — embedded too, so the map works without the media/ folder.
still = ROOT + 'media/orbit-end.jpg'
if os.path.exists(still):
    out = os.path.join(tmp, 'still.jpg')
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', still, '-vf', "scale='min(1920,iw)':-2", '-q:v', '4', out], check=True)
    block += 'const STILL_DATA = "data:image/jpeg;base64,' + base64.b64encode(open(out, 'rb').read()).decode() + '";\n'
    print('still', os.path.getsize(out) // 1024, 'KB')
start, end = '<!--PHOTO_DATA_START-->', '<!--PHOTO_DATA_END-->'
script = f'{start}<script>\n{block}</script>{end}\n'
if start in s:
    s = re.sub(re.escape(start) + r'.*?' + re.escape(end) + r'\n', lambda m: script, s, flags=re.S)
else:
    # must load before the main script
    i = s.index('<script>\n/* ============================================================\n   1) AERIAL IMAGE')
    s = s[:i] + script + s[i:]
open(p, 'w').write(s)
print('html size', os.path.getsize(p) // 1024, 'KB')
