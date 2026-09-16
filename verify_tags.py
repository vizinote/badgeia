import glob, re, subprocess

bad = []
for path in sorted(glob.glob('blog/*.html')):
    if path.endswith('index.html'):
        continue
    new = open(path, encoding='utf-8').read()
    old = subprocess.run(['git', 'show', f'HEAD:{path}'], capture_output=True, text=True).stdout
    if not old:
        continue
    for tag in ('article', 'main', 'div', 'section', 'ul', 'ol', 'p', 'h2', 'h3'):
        o, c = f'<{tag}', f'</{tag}>'
        if (new.count(o), new.count(c)) != (old.count(o), old.count(c)):
            bad.append((path, tag, (old.count(o), old.count(c)), (new.count(o), new.count(c))))
print('deséquilibres balises:', bad or 'aucun')
assert not bad
