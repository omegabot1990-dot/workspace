import re, collections, statistics, json
from pathlib import Path
try:
    import yaml
except Exception:
    yaml = None

root = Path('002 - research')
md_files = list(root.rglob('*.md'))
# Exclude non-research stray files if present
md_files = [p for p in md_files if p.name.lower() != 'work.md']

def parse_frontmatter(text: str):
    if not text.startswith('---'):
        return None, text
    parts = text.split('---', 2)
    if len(parts) < 3:
        return None, text
    fm_raw = parts[1]
    body = parts[2]
    if yaml is None:
        return {'_raw': fm_raw, '_yaml_missing': True}, body
    try:
        fm = yaml.safe_load(fm_raw) or {}
    except Exception:
        fm = {'_parse_error': True, '_raw': fm_raw}
    return fm, body

wikilink_pat = re.compile(r'\[\[([^\]]+)\]\]')
mdlink_pat = re.compile(r'\[[^\]]+\]\(([^\)]+)\)')
checkbox_pat = re.compile(r'^\s*- \[ \] ')

stats = {
    'files': len(md_files),
    'has_frontmatter': 0,
    'tags': collections.Counter(),
    'parent_present': 0,
    'child_present': 0,
    'parent_counts': [],
    'parent_style': collections.Counter(),
    'parent_targets': collections.Counter(),
    'body_wikilinks': collections.Counter(),
    'body_mdlinks': 0,
    'checkbox_lines': 0,
    'lines_total': 0,
    'file_prefix_kind': collections.Counter(),
    'frontmatter_keys': collections.Counter(),
}

prefix_dt = re.compile(r'^(\d{12})\s*-\s*(.+)\.md$')
prefix_date = re.compile(r'^(\d{4}-\d{2}-\d{2})\s*-\s*(.+)\.md$')
prefix_compact = re.compile(r'^(\d{8})\s*-\s*(.+)\.md$')

missing_parent = []

for p in md_files:
    text = p.read_text(encoding='utf-8', errors='ignore')
    lines = text.splitlines()
    stats['lines_total'] += len(lines)
    stats['checkbox_lines'] += sum(1 for ln in lines if checkbox_pat.match(ln))

    name = p.name
    if prefix_dt.match(name):
        stats['file_prefix_kind']['yyyymmddhhmm'] += 1
    elif prefix_compact.match(name):
        stats['file_prefix_kind']['yyyymmdd'] += 1
    elif prefix_date.match(name):
        stats['file_prefix_kind']['yyyy-mm-dd'] += 1
    elif re.match(r'^\d{4,}.*\.md$', name):
        stats['file_prefix_kind']['numeric-other'] += 1
    else:
        stats['file_prefix_kind']['no-date-prefix'] += 1

    fm, body = parse_frontmatter(text)
    if isinstance(fm, dict):
        stats['has_frontmatter'] += 1
        for k in fm.keys():
            stats['frontmatter_keys'][k] += 1

        tags = fm.get('tags')
        if isinstance(tags, list):
            for t in tags:
                if isinstance(t, str):
                    stats['tags'][t.strip()] += 1
        elif isinstance(tags, str):
            stats['tags'][tags.strip()] += 1

        parents = fm.get('parent nodes')
        if parents is not None:
            stats['parent_present'] += 1
            if isinstance(parents, list):
                stats['parent_style']['list'] += 1
                stats['parent_counts'].append(len(parents))
                for it in parents:
                    if isinstance(it, str):
                        m = wikilink_pat.search(it)
                        stats['parent_targets'][m.group(1) if m else it] += 1
            elif isinstance(parents, str):
                stats['parent_style']['string'] += 1
                stats['parent_counts'].append(1)
                m = wikilink_pat.search(parents)
                stats['parent_targets'][m.group(1) if m else parents] += 1
            else:
                stats['parent_style'][type(parents).__name__] += 1

        pn = fm.get('parent nodes')
        if pn in (None, [], ''):
            missing_parent.append(str(p))
    else:
        missing_parent.append(str(p))

    for m in wikilink_pat.finditer(body):
        stats['body_wikilinks'][m.group(1)] += 1
    stats['body_mdlinks'] += len(mdlink_pat.findall(body))

pct_front = stats['has_frontmatter'] / max(1, stats['files'])

print('Files:', stats['files'])
print('With YAML frontmatter:', stats['has_frontmatter'], f'({pct_front:.0%})')
print('Total lines:', stats['lines_total'])
print("Checkbox lines '- [ ]':", stats['checkbox_lines'])

print('\nFilename date-prefix styles:')
for k,v in stats['file_prefix_kind'].most_common():
    print('  -', k + ':', v)

print('\nTop tags:')
for t,c in stats['tags'].most_common(12):
    print('  -', t + ':', c)

print('\nFrontmatter keys (top 12):')
for k,c in stats['frontmatter_keys'].most_common(12):
    print('  -', k + ':', c)

print('\nparent nodes present:', stats['parent_present'], 'files')
print('parent nodes style:', json.dumps(dict(stats['parent_style']), indent=2))
if stats['parent_counts']:
    print('parent count: min=', min(stats['parent_counts']),
          'median=', statistics.median(stats['parent_counts']),
          'max=', max(stats['parent_counts']))

print('\nMost common parent targets (top 15):')
for k,c in stats['parent_targets'].most_common(15):
    print('  -', k + ':', c)

print('\nMost common wikilinks in bodies (top 15):')
for k,c in stats['body_wikilinks'].most_common(15):
    print('  -', k + ':', c)

print('\nMarkdown external links in bodies:', stats['body_mdlinks'])

print('\nFiles missing parent nodes or empty:', len(missing_parent))
for x in missing_parent[:15]:
    print('  -', x)
