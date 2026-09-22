#!/usr/bin/env python3
"""Draft refinement and semantic link publication. Python standard library only."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import brain


def digest(data):
    return hashlib.sha256(data).hexdigest()


def eligible(root, path):
    rel = path.relative_to(root).as_posix()
    return path.suffix == '.md' and any(rel.startswith(x) for x in
        ('knowledge/', 'architecture/', 'personal/', 'thoughts/notes/'))


def read(root, name):
    p = brain.safe(root, name)
    if not (eligible(root, p) or p.is_relative_to(root/'thoughts/drafts')):
        brain.fail('Only finished notes or thought drafts may be read')
    data = p.read_bytes()
    return {'path': str(p.relative_to(root)), 'sha256': digest(data), 'content': data.decode('utf-8')}


def inventory(root, scope):
    # Do not traverse inbox, archive, snapshots or other source repositories.
    bases = ['thoughts/drafts'] if scope == 'drafts' else ['knowledge', 'architecture', 'personal', 'thoughts/notes']
    result = []
    for base in bases:
        directory = brain.safe(root, base)
        if directory != root/base: brain.fail('Symlinked source directories are not supported')
        for p in brain.active(directory):
            result.append({'path': str(p.relative_to(root)), 'sha256': digest(p.read_bytes())})
    return result


def journal_path(root):
    return root/'.state/thoughts-publishing.json'


def recover(root):
    p = journal_path(root)
    if not p.exists(): return {'recovered': False}
    j = json.loads(p.read_text())
    # Check everything before rollback; concurrent manual edits are never erased.
    for name, change in j['changes'].items():
        target = brain.safe(root, name)
        current = target.read_bytes().decode('utf-8') if target.exists() else None
        if current not in (change['before'], change['after']):
            brain.fail('External edit blocks recovery: '+name+'; ask the user')
    for move in j['moves']:
        src, dst = brain.safe(root, move['source']), brain.safe(root, move['destination'])
        if src.exists() == dst.exists(): brain.fail('Ambiguous archive move; ask user: '+move['source'])
        if src.exists() and digest(src.read_bytes()) != move['sha256']:
            brain.fail('Draft changed during interruption; ask user')
        if dst.exists() and [dst.stat().st_ino, dst.stat().st_size, dst.stat().st_mtime_ns] != move['stat']:
            brain.fail('Archived draft changed during interruption; ask user')
        # Archive content is never opened, including recovery.
    for move in reversed(j['moves']):
        src, dst = brain.safe(root, move['source']), brain.safe(root, move['destination'])
        if dst.exists():
            src.parent.mkdir(parents=True, exist_ok=True)
            dst.rename(src)
    for name, change in j['changes'].items():
        target = brain.safe(root, name)
        if change['before'] is None:
            if target.exists(): target.unlink()
        else: brain.atomic(target, change['before'])
    p.unlink()
    return {'recovered': True, 'action': 'Rolled back; reread sources and retry'}


def commit(root, changes, moves):
    if journal_path(root).exists() or (root/'.state/bootstrap-publishing.json').exists():
        brain.fail('Recover interrupted publication first')
    j = {'changes': {}, 'moves': moves}
    for name, content in changes.items():
        p = brain.safe(root, name)
        j['changes'][name] = {'before': p.read_bytes().decode('utf-8') if p.exists() else None, 'after': content}
    brain.atomic(journal_path(root), json.dumps(j, ensure_ascii=False, indent=2))
    try:
        for name, content in changes.items(): brain.atomic(brain.safe(root, name), content)
        for move in moves:
            src, dst = brain.safe(root, move['source']), brain.safe(root, move['destination'])
            if digest(src.read_bytes()) != move['sha256'] or dst.exists(): brain.fail('Draft or archive destination changed')
            dst.parent.mkdir(parents=True, exist_ok=True)
            src.rename(dst)
    except Exception:
        recover(root)
        raise
    journal_path(root).unlink()
    return {'written': list(changes), 'archived': [m['destination'] for m in moves]}


def guard(root, name, expected):
    p = brain.safe(root, name)
    actual = digest(p.read_bytes()) if p.exists() else None
    if actual != expected: brain.fail('Reread changed document: '+name)
    return p


def refine(root, plan):
    if journal_path(root).exists(): brain.fail('Run thoughts recover first')
    if plan.get('clarifications_complete') is not True: brain.fail('Resolve ambiguous meaning with the user first')
    sources = plan.get('sources', [])
    if not sources: brain.fail('At least one draft is required')
    moves, source_names = [], set()
    for s in sources:
        p = guard(root, s['path'], s['sha256'])
        if not p.is_relative_to(root/'thoughts/drafts') or p.suffix != '.md' or not p.exists():
            brain.fail('Only Markdown thought drafts can be processed')
        name = str(p.relative_to(root))
        if name != s['path'] or name in source_names: brain.fail('Duplicate or noncanonical source')
        source_names.add(name)
        destination = 'archive/thoughts/'+p.relative_to(root/'thoughts/drafts').as_posix()
        if brain.safe(root, destination).exists():
            q = Path(destination)
            destination = str(q.with_name(q.stem+'-'+s['sha256'][:12]+q.suffix))
        if brain.safe(root, destination).exists(): brain.fail('Archive collision; use a new draft filename')
        st = p.stat()
        moves.append({'source': name, 'destination': destination, 'sha256': s['sha256'],
                      'stat': [st.st_ino, st.st_size, st.st_mtime_ns]})
    changes, accounted = {}, set()
    for d in plan.get('documents', []):
        p = guard(root, d['path'], d.get('expected_sha256'))
        name = p.relative_to(root).as_posix()
        if p.suffix != '.md' or not (name == 'thoughts/notes/ideas.md' or
                name.startswith(('thoughts/notes/learnings/', 'thoughts/notes/reflections/'))):
            brain.fail('Refinement may only write thought notes')
        if name != d['path'] or name in changes: brain.fail('Duplicate/noncanonical output')
        content = d['content']
        if not content.strip(): brain.fail('Empty output')
        refs = d.get('sources', [])
        if not refs or not set(refs) <= source_names: brain.fail('Each output must identify contributing drafts')
        accounted.update(refs)
        # Deterministic provenance; duplicate thoughts still retain their new source.
        for move in moves:
            if move['source'] in refs:
                target = brain.safe(root, move['destination'])
                link = brain.rel_link(p, target)
                if link not in content:
                    content = content.rstrip()+'\n\n[Draft source]('+link+')\n'
        if '<!-- brain-links:start -->' not in content:
            content = content.rstrip()+'\n\n<!-- brain-links:start -->\n## Related\n\n- [Second Brain]('+brain.rel_link(p, root/'index.md')+')\n<!-- brain-links:end -->\n'
        changes[name] = content
    if accounted != source_names: brain.fail('Every draft must be represented, including duplicate content')
    if not (root/'index.md').exists(): changes['index.md'] = '# Second Brain\n'
    # Existing incoming draft links are repaired without reading archive.
    for p in brain.active(root):
        name = p.relative_to(root).as_posix()
        if name in source_names: continue
        text = changes.get(name, p.read_bytes().decode('utf-8'))
        def replace(m):
            u = brain.urlsplit(m[2])
            for move in moves:
                if not u.scheme and not u.netloc and u.path and (p.parent/brain.unquote(u.path)).resolve() == root/move['source']:
                    return '['+m[1]+']('+brain.rel_link(p, root/move['destination'])+('#'+u.fragment if u.fragment else '')+')'
            return m[0]
        updated = brain.LINK.sub(replace, text)
        if updated != text: changes[name] = updated
    future = {brain.safe(root,n) for n in changes} | {root/m['destination'] for m in moves}
    for name, content in changes.items():
        for t in brain.targets(root/name, content):
            if not t.is_relative_to(root) or (not t.exists() and t not in future): brain.fail('Broken output link: '+str(t))
    return commit(root, changes, moves)


def link(root, plan):
    if journal_path(root).exists(): brain.fail('Run thoughts recover first')
    changes = {}
    for relation in plan.get('relations', []):
        a = guard(root, relation['source'], relation['source_sha256'])
        b = guard(root, relation['target'], relation['target_sha256'])
        if a == b or not eligible(root,a) or not eligible(root,b) or not a.exists() or not b.exists():
            brain.fail('Links require two distinct finished notes')
        reason = relation.get('reason', '').strip()
        if not reason or '\n' in reason or any(x in reason for x in ('[',']','<','>')):
            brain.fail('Provide a plain one-line explanation of the relationship')
        for source, target in ((a,b),(b,a)):
            name = source.relative_to(root).as_posix()
            content = changes.get(name, source.read_bytes().decode('utf-8'))
            # Semantic links are distinct from automatically generated graph backlinks.
            if target in set(brain.targets(source, content)): continue
            marker = '<!-- thought-connections:end -->'
            entry = '- ['+brain.link_label(root,source,target)+']('+brain.rel_link(source,target)+') — '+reason+'\n'
            if marker not in content:
                content += '\n<!-- thought-connections:start -->\n## Connections\n\n'+marker+'\n'
            content = content.replace(marker, entry+marker)
            changes[name] = content
    if not changes: return {'written': [], 'archived': []}
    return commit(root, changes, [])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default=str(Path.home()/'.config/second-brain/config.yaml'))
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('inventory'); p.add_argument('--scope', choices=['drafts','notes'], required=True)
    p = sub.add_parser('read'); p.add_argument('path')
    for name in ('refine','link'):
        p = sub.add_parser(name); p.add_argument('plan')
    sub.add_parser('recover')
    a = parser.parse_args(); c = brain.config(a.config); root = Path(c['brain_dir']).resolve()
    with brain.lock(root):
        if a.command != 'recover' and journal_path(root).exists(): brain.fail('Run thoughts recover first')
        if a.command == 'inventory': result = inventory(root, a.scope)
        elif a.command == 'read': result = read(root, a.path)
        elif a.command == 'recover': result = recover(root)
        else: result = globals()[a.command](root, json.loads(Path(a.plan).read_text()))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try: main()
    except (ValueError, KeyError, OSError, RuntimeError) as e: raise SystemExit('ERROR: '+str(e))
