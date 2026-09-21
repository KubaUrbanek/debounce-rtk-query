#!/usr/bin/env python3
"""Second Brain v2. Python standard library only; no model calls or Git writes."""
import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import quote, unquote, urlsplit, urlencode
from zoneinfo import ZoneInfo

TZ = ZoneInfo('Europe/Warsaw')
LINK = re.compile(r'(?<!!)\[([^\]]*)\]\(([^)]+)\)')
AUTO = re.compile(r'\n<!-- brain-links:start -->.*?<!-- brain-links:end -->\n?', re.S)
FIELDS = {'date', 'include_in_daily', 'type', 'repositories', 'source_url',
          'daily_hash', 'daily_output', 'knowledge_hash', 'status', 'supersedes'}

def fail(message):
    raise ValueError(message)

def scalar(value):
    value = value.strip()
    if not value:
        fail('Empty scalar; use unknown or none')
    if value.startswith('"'):
        parsed = json.loads(value)
        if not isinstance(parsed, str):
            fail('Expected a quoted string')
        return parsed
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if any(x in value for x in '\t\n') or value[0] in '&*!|>{[' or ' #' in value:
        fail('Unsupported YAML syntax; follow config.example.yaml')
    return value

def config(path):
    """Strict fixed-schema YAML subset, deliberately not a general YAML parser."""
    c = {}; section = None; repo = None
    for number, line in enumerate(Path(path).read_text().splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if '\t' in line:
            fail(f'Line {number}: tabs are unsupported')
        if not line.startswith(' '):
            key, sep, value = line.partition(':')
            if not sep or key in c:
                fail(f'Line {number}: invalid/duplicate field')
            if key in ('repositories', 'author_emails') and not value.strip():
                c[key] = []; section = key
            else:
                c[key] = scalar(value); section = None
        elif section == 'author_emails' and line.startswith('  - '):
            c[section].append(scalar(line[4:]))
        elif section == 'repositories':
            if line.startswith('  - id: '):
                repo = {'id': scalar(line[8:])}; c[section].append(repo)
            elif line.startswith('    ') and not line.startswith('     ') and repo is not None:
                key, sep, value = line.strip().partition(':')
                if not sep or key in repo:
                    fail(f'Line {number}: invalid repository field')
                repo[key] = scalar(value)
            else:
                fail(f'Line {number}: invalid repository indentation')
        else:
            fail(f'Line {number}: unsupported YAML structure')
    c.setdefault('max_parallel_agents', '4')
    if set(c) != {'version', 'brain_dir', 'timezone', 'author_emails', 'repositories', 'max_parallel_agents'}:
        fail('Configuration must have exactly the fields in config.example.yaml')
    if not str(c['max_parallel_agents']).isdigit() or int(c['max_parallel_agents']) < 1:
        fail('max_parallel_agents must be a positive integer')
    c['max_parallel_agents'] = int(c['max_parallel_agents'])
    if c['version'] != '2' or c['timezone'] != 'Europe/Warsaw':
        fail('Expected version 2 and timezone Europe/Warsaw')
    if not Path(c['brain_dir']).is_absolute() or Path(c['brain_dir']).resolve() == Path('/'):
        fail('brain_dir must be an absolute, dedicated directory')
    if not c['author_emails'] or any('@' not in x for x in c['author_emails']):
        fail('Provide your exact author emails')
    ids = set()
    if not c['repositories']:
        fail('At least one repository is required')
    for r in c['repositories']:
        r.setdefault('remote', 'origin')
        if set(r) != {'id', 'path', 'gitlab_host', 'gitlab_project', 'remote'}:
            fail('Unexpected repository fields')
        if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', r['id']) or r['id'] in ids:
            fail('Repository IDs must be unique lowercase slugs')
        ids.add(r['id'])
        if not Path(r['path']).is_absolute():
            fail('Repository paths must be absolute')
        if not re.fullmatch(r'[a-zA-Z0-9.-]+(?::[0-9]+)?', r['gitlab_host']):
            fail('gitlab_host must be a hostname, optionally with port')
        if r['remote'].startswith('-') or not r['gitlab_project']:
            fail('Invalid remote or project')
    return c

def atomic(path, text):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.brain-')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def run(args, cwd=None):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=180)
    if p.returncode:
        # Do not leak credential-bearing remote URLs or arbitrary stderr.
        raise RuntimeError(f'{args[0]} failed (exit {p.returncode}); check authentication/access locally')
    return p.stdout

def bounds(day):
    day = dt.date.fromisoformat(day)
    a = dt.datetime.combine(day, dt.time(), TZ)
    b = dt.datetime.combine(day + dt.timedelta(days=1), dt.time(), TZ)
    return a, b

def today(): return dt.datetime.now(TZ).date().isoformat()

def api(r, endpoint):
    return json.loads(run(['glab', 'api', '--hostname', r['gitlab_host'], endpoint]))

def pages(r, endpoint, params=None):
    for page in range(1, 10001):
        data = api(r, endpoint + '?' + urlencode(dict(params or {}, per_page=100, page=page)))
        if not isinstance(data, list): fail('GitLab returned a non-list response')
        yield from data
        if len(data) < 100: return
    fail('Pagination limit exceeded; report must be marked partial')

def collect_system(c, day):
    start, end = bounds(day)
    if day > today(): fail('Future system report date is unsupported')
    result = {'kind': 'system', 'date': day, 'repositories': [], 'errors': []}
    for r in c['repositories']:
        group = {'id': r['id'], 'merge_requests': []}; result['repositories'].append(group)
        try:
            endpoint = 'projects/' + quote(r['gitlab_project'], safe='') + '/merge_requests'
            # updated_after avoids relying on recent merged_after API support.
            mrs = list(pages(r, endpoint, {'state': 'merged', 'scope': 'all',
                'updated_after': start.isoformat(), 'order_by': 'updated_at', 'sort': 'asc'}))
            for mr in sorted(mrs, key=lambda x: x.get('merged_at') or ''):
                merged = mr.get('merged_at')
                if not merged or not mr['target_branch'].startswith('develop'): continue
                if not start <= dt.datetime.fromisoformat(merged.replace('Z', '+00:00')) < end: continue
                item = {k: mr.get(k) for k in ('iid', 'title', 'description', 'web_url', 'target_branch', 'merged_at')}
                group['merge_requests'].append(item)
                try:
                    item['diffs'] = list(pages(r, endpoint + f"/{mr['iid']}/diffs"))
                    detail = api(r, endpoint + f"/{mr['iid']}")
                    item['diff_refs'] = detail.get('diff_refs')
                    incomplete = not item['diffs'] or any(d.get('too_large') or d.get('collapsed') for d in item['diffs'])
                    changes = str(detail.get('changes_count', ''))
                    if changes.endswith('+') or (changes.isdigit() and int(changes) > len(item['diffs'])):
                        incomplete = True
                    if incomplete: raise RuntimeError('MR diff is empty, limited or incomplete; inspect before claiming full coverage')
                except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as e:
                    result['errors'].append({'repo': r['id'], 'mr': mr['iid'], 'error': str(e)})
        except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as e:
            result['errors'].append({'repo': r['id'], 'error': str(e)})
    result['activity'] = any(r['merge_requests'] for r in result['repositories'])
    return result

def split_note(text):
    if not text.startswith('---\n') or '\n---\n' not in text[4:]: fail('Missing YAML frontmatter')
    front, body = text[4:].split('\n---\n', 1); meta = {}
    for line in front.splitlines():
        if not line or line.startswith('#'): continue
        key, sep, value = line.partition(':')
        if not sep or key not in FIELDS or key in meta: fail('Unknown/duplicate frontmatter field: ' + key)
        meta[key] = scalar(value)
    if meta.get('include_in_daily', 'false') not in ('true', 'false'): fail('include_in_daily must be true/false')
    return meta, body

def note_text(meta, body):
    return '---\n' + ''.join(k + ': ' + json.dumps(str(v), ensure_ascii=False) + '\n' for k, v in meta.items()) + '---\n' + body

def digest(meta, body):
    relevant = {k:v for k,v in meta.items() if k not in ('daily_hash', 'daily_output', 'knowledge_hash')}
    return hashlib.sha256((json.dumps(relevant, sort_keys=True) + AUTO.sub('', body)).encode()).hexdigest()

def inventory(c, stage):
    root = Path(c['brain_dir']).resolve(); rows = []
    for p in sorted((root / 'inbox').rglob('*')):
        if not p.is_file(): continue
        rel = p.relative_to(root).as_posix()
        if p.is_symlink() or p.suffix != '.md':
            rows.append({'path': rel, 'error': 'Only regular .md inputs are supported'}); continue
        try:
            text = p.read_text(); meta, body = split_note(text); h = digest(meta, body)
            try: dt.date.fromisoformat(meta.get('date', '')); valid_date = True
            except ValueError: valid_date = False
            needs = meta.get(stage + '_hash') != h
            if stage == 'daily':
                needs = needs and meta.get('include_in_daily') == 'true' and valid_date and meta['date'] <= today()
            rows.append({'path': rel, 'hash': h, 'metadata': meta, 'valid_date': valid_date,
                         'needs_processing': needs, 'body': body if needs else None})
        except ValueError as e: rows.append({'path': rel, 'error': str(e)})
    return rows

def collect_personal(c):
    day = today(); start, end = bounds(day); wanted = set(c['author_emails'])
    result = {'kind': 'personal', 'date': day, 'repositories': [], 'errors': [], 'notes': inventory(c, 'daily')}
    for r in c['repositories']:
        group = {'id': r['id'], 'commits': [], 'patches': ''}; result['repositories'].append(group)
        def git(*args): return run(['git', '-C', r['path'], *args])
        try:
            try: git('fetch', '--prune', r['remote'], '+refs/heads/*:refs/remotes/' + r['remote'] + '/*')
            except (RuntimeError, OSError, subprocess.TimeoutExpired):
                result['errors'].append({'repo': r['id'], 'error': 'Fetch failed; local and cached remote refs only'})
            # No --since: Git filters committer dates, whereas daily uses author dates.
            raw = git('log', '--branches', '--remotes', 'HEAD', '--format=%H%x09%at%x09%ae%x09%an%x09%s')
            seen = set()
            for line in raw.splitlines():
                sha, epoch, email, name, subject = line.split('\t', 4)
                if sha in seen or email not in wanted or not start.timestamp() <= int(epoch) < end.timestamp(): continue
                seen.add(sha)
                refs = git('for-each-ref', '--contains', sha, '--format=%(refname:short)', 'refs/heads', 'refs/remotes').splitlines()
                group['commits'].append({'sha': sha, 'author': name, 'email': email, 'subject': subject, 'branches': refs})
            # Batch patches for the agent to synthesize by topic, not commit-by-commit prose.
            for offset in range(0, len(group['commits']), 50):
                hashes = [x['sha'] for x in group['commits'][offset:offset+50]]
                group['patches'] += git('show', '--no-ext-diff', '--no-textconv', '--format=medium', '--diff-merges=first-parent', *hashes, '--')
        except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired) as e:
            result['errors'].append({'repo': r['id'], 'error': str(e)})
    result['activity'] = any(r['commits'] for r in result['repositories']) or any(n.get('needs_processing') for n in result['notes'])
    return result

def safe(root, relative):
    p = (root / relative).resolve()
    if not p.is_relative_to(root) or p == root: fail('Path escapes brain directory')
    return p

def active(root):
    # Never descend into private bootstrap snapshots, state, archive or Git internals.
    result = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in ('archive', '.state', '.git')
                   and not (Path(directory) / d).is_symlink()]
        result.extend(Path(directory)/f for f in files if f.endswith('.md')
                      and not (Path(directory)/f).is_symlink())
    return sorted(result)

def targets(p, text):
    for _, raw in LINK.findall(AUTO.sub('', text)):
        u = urlsplit(raw)
        if u.scheme or u.netloc or not u.path: continue
        yield (p.parent / unquote(u.path)).resolve()

def rel_link(source, target): return quote(os.path.relpath(target, source.parent), safe='/.-_')

def graph(root, writer=None):
    """Never open archive content. Backlink sections are excluded from content hashes."""
    writer = writer or atomic
    index = root / 'index.md'
    if not index.exists(): writer(index, '# Second Brain\n')
    files = active(root); texts = {p:AUTO.sub('', p.read_text()).rstrip() + '\n' for p in files}
    adjacency = {p:set() for p in files}
    for p, text in texts.items():
        if p != index: adjacency[p].add(index); adjacency[index].add(p)
        for t in targets(p, text):
            if t in adjacency and t != p: adjacency[p].add(t); adjacency[t].add(p)
    for p in files:
        links = ''.join(f'- [{t.stem}]({rel_link(p,t)})\n' for t in sorted(adjacency[p]))
        writer(p, texts[p] + '\n<!-- brain-links:start -->\n## Related\n\n' + links + '<!-- brain-links:end -->\n')

def validate(root):
    errors = []
    for p in active(root):
        text = p.read_text()
        for _, raw in LINK.findall(text):
            u = urlsplit(raw)
            if u.scheme or u.netloc or not u.path: continue
            target = (p.parent / unquote(u.path)).resolve()
            if not target.is_relative_to(root) or not target.exists(): errors.append(f'{p.relative_to(root)}: broken/outside link {raw}')
        if p != root / 'index.md' and '<!-- brain-links:start -->' not in text: errors.append(f'{p}: missing graph links')
    if errors: fail('\n'.join(errors))

def move(root, src, dst):
    """Rename only; archived content is never opened. Rewrite active incoming links."""
    if dst.exists(): fail('Destination already exists: ' + str(dst))
    dst.parent.mkdir(parents=True, exist_ok=True); os.rename(src, dst)
    for p in active(root):
        # Archived source link paths remain correct because inbox/archive have equal depth.
        text = p.read_text()
        def fix(m):
            raw = m[2]; u = urlsplit(raw)
            if not u.scheme and u.path and (p.parent / unquote(u.path)).resolve() == src:
                return '[' + m[1] + '](' + rel_link(p,dst) + ('#' + u.fragment if u.fragment else '') + ')'
            return m[0]
        updated = LINK.sub(fix, text)
        if updated != text: atomic(p, updated)

def archive_ready(c):
    root = Path(c['brain_dir']).resolve(); moved = []
    for n in inventory(c, 'knowledge'):
        if 'error' in n or not n['valid_date']: continue
        m = n['metadata']; h = n['hash']
        if m.get('knowledge_hash') != h: continue
        if m.get('include_in_daily') == 'true' and m.get('daily_hash') != h: continue
        src = root / n['path']; dst = root / 'archive' / src.relative_to(root / 'inbox')
        move(root, src, dst); moved.append(str(dst.relative_to(root)))
    return moved

def publish(c, plan):
    """Apply explicit semantic output, validate, then mark exact source versions done."""
    root = Path(c['brain_dir']).resolve(); stage = plan['stage']
    if (root/'.state/thoughts-publishing.json').exists(): fail('Run thoughts recover first')
    if (root/'.state/bootstrap-publishing.json').exists():
        fail('Interrupted bootstrap publication; run bootstrap recover first')
    if stage not in ('system','daily','knowledge'): fail('Invalid stage')
    sources = plan.get('processed', [])
    for s in sources:
        p = safe(root,s['path'])
        if not p.is_relative_to(root / 'inbox'): fail('Only inbox sources may be marked')
        m,b = split_note(p.read_text())
        if digest(m,b) != s['hash']: fail('Source changed; reread before publishing: ' + s['path'])
    if stage == 'knowledge' and not plan.get('human_review_complete'):
        fail('Complete scope/conflict review before knowledge publication')
    documents = plan.get('documents', [])
    for d in documents:
        p = safe(root,d['path'])
        allowed = {'system': ['inbox'], 'daily': ['personal'], 'knowledge': ['knowledge','architecture','conflicts']}
        if p.suffix != '.md' or p.relative_to(root).parts[0] not in allowed[stage]: fail('Invalid document target')
        if stage == 'daily' and p.name != today() + '-daily.md': fail('Personal daily is today-only')
        if stage == 'system':
            day = p.name.removesuffix('-system.md'); bounds(day)
            if p.name != day + '-system.md': fail('Invalid system filename')
        if stage in ('daily','system'):
            day = today() if stage == 'daily' else p.name[:10]
            if '# Daily summary — ' + dt.date.fromisoformat(day).strftime('%d %m %Y') not in d['content']:
                fail('Missing report title with DD MM YYYY')
        if stage == 'system':
            m,_ = split_note(d['content'])
            if m.get('include_in_daily') != 'false' or m.get('date') != day: fail('Invalid system metadata')
        if stage == 'knowledge' and p.is_relative_to(root / 'architecture') and not p.exists():
            m,_ = split_note(d['content'])
            if m.get('status') != 'proposed': fail('New ADRs must be proposed')
        # Optimistic guard prevents accidentally erasing an unread existing daily/note.
        if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() != d.get('expected_sha256'):
            fail('Existing document changed or was not read: ' + d['path'])
    # Validate proposed links before writing any document.
    future = {safe(root,d['path']) for d in documents} | {root / 'index.md'}
    for d in documents:
        p = safe(root,d['path'])
        for t in targets(p,d['content']):
            if not t.is_relative_to(root) or (not t.exists() and t not in future): fail('Unresolved source link: ' + str(t))
    for d in documents: atomic(safe(root,d['path']), d['content'])
    graph(root); validate(root)
    if stage in ('daily','knowledge'):
        if stage == 'daily' and sources and not documents: fail('Cannot mark daily without a report')
        for s in sources:
            p = root / s['path']; m,b = split_note(p.read_text())
            if digest(m,b) != s['hash']: fail('Source changed during publication')
            m[stage + '_hash'] = s['hash']
            if stage == 'daily': m['daily_output'] = 'personal/' + today() + '-daily.md'
            atomic(p,note_text(m,b))
    moved = archive_ready(c); graph(root); validate(root)
    return {'written': [d['path'] for d in documents], 'archived': moved}

@contextlib.contextmanager
def lock(root):
    root.mkdir(parents=True, exist_ok=True)
    with (root / '.brain.lock').open('w') as f:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default=str(Path.home()/'.config/second-brain/config.yaml'))
    subs = ap.add_subparsers(dest='command', required=True)
    subs.add_parser('check')
    subs.add_parser('init')
    p = subs.add_parser('system'); p.add_argument('--date', default=today())
    subs.add_parser('personal')
    p = subs.add_parser('inventory'); p.add_argument('--stage', choices=['daily','knowledge'], default='knowledge')
    p = subs.add_parser('read'); p.add_argument('path')
    p = subs.add_parser('restore'); p.add_argument('--date', required=True)
    p = subs.add_parser('publish'); p.add_argument('plan')
    subs.add_parser('validate')
    args = ap.parse_args(); c = config(args.config); root = Path(c['brain_dir']).resolve()
    if (root/'.state/thoughts-publishing.json').exists(): fail('Run thoughts recover first')
    if (root/'.state/bootstrap-publishing.json').exists() and args.command not in ('read','check'):
        fail('Interrupted bootstrap publication; run bootstrap recover first')
    if args.command == 'check': result = {'valid': True, 'repositories': len(c['repositories'])}
    elif args.command == 'system': result = collect_system(c,args.date)
    elif args.command == 'personal': result = collect_personal(c)
    elif args.command == 'inventory': result = inventory(c,args.stage)
    elif args.command == 'read':
        p = safe(root,args.path)
        if p.is_relative_to(root/'archive'): fail('Archive content is not readable by the agent')
        raw = p.read_bytes(); result = {'path': args.path, 'expected_sha256': hashlib.sha256(raw).hexdigest(), 'content': raw.decode()}
    else:
        with lock(root):
            if args.command == 'init':
                for d in ('thoughts/drafts','thoughts/notes/learnings','thoughts/notes/reflections','inbox','personal','archive','knowledge/domain','knowledge/technical/shared','knowledge/technical/unknown','conflicts','architecture/cross-repository','architecture/unknown'):
                    (root/d).mkdir(parents=True,exist_ok=True)
                for r in c['repositories']:
                    for d in ('architecture','knowledge/technical'): (root/d/r['id']).mkdir(parents=True,exist_ok=True)
                    (root/'knowledge/technical'/r['id']/'database').mkdir(parents=True,exist_ok=True)
                essence=root/'knowledge/essence.md'
                if not essence.exists(): atomic(essence,'# Knowledge guide\n\n## Technical knowledge\n\n## Domain knowledge\n')
                graph(root); result={'initialized': str(root)}
            elif args.command == 'restore':
                bounds(args.date); name=args.date+'-system.md'; src=root/'archive'/name; dst=root/'inbox'/name
                if src.exists(): move(root,src,dst)
                graph(root); result={'path': str(dst), 'exists': dst.exists()}
            elif args.command == 'publish': result=publish(c,json.loads(Path(args.plan).read_text()))
            else: validate(root); result={'valid': True}
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    try: main()
    except (ValueError, KeyError, OSError, RuntimeError, subprocess.TimeoutExpired) as e:
        raise SystemExit('ERROR: ' + str(e))
