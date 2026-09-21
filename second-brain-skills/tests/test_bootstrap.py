import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / 'runtime'))
import brain
import bootstrap as boot


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / 'repo'
        self.repo.mkdir()
        self.git('init', '-b', 'develop-main')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.test')
        for name, text in {'src/app.py': 'def submit():\n    return "accepted"\n',
                           'db/schema.sql': 'create table orders(id integer primary key);\n',
                           'README.md': '# Orders\nSubmission service.\n',
                           'tests/test_app.py': 'assert False\n',
                           'generated/client.py': '# generated client\n'}.items():
            brain.atomic(self.repo/name, text)
        self.git('add', '.')
        self.git('commit', '-m', 'Fixture')
        # A local Git remote exercises real object transfer without network access.
        self.git('remote', 'add', 'origin', str(self.repo))
        self.root = self.base/'brain'
        self.c = {'brain_dir': str(self.root), 'max_parallel_agents': 2,
                  'repositories': [{'id': 'orders', 'path': str(self.repo), 'remote': 'origin'}]}
        self.b = boot.Bootstrap(self.c, 'orders')
        self.b.prepare('develop-main')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], check=True,
                              capture_output=True, text=True).stdout.strip()

    def analyze(self):
        self.b.claim('explorer', 'explorer')
        for chunk in self.b.status()['pending_chunks']:
            result = self.b.read('explorer', chunk['id'])
            kind = 'database' if chunk['path'].endswith('.sql') else 'technical'
            self.b.submit('explorer', {'chunk_id': chunk['id'], 'receipt': result['receipt'],
                                      'findings': [{'kind': kind, 'text': 'Fixture observation: '+chunk['path']}]})
        self.b.release('explorer')

    def plan(self):
        s = self.b.load()
        ids = list(s['results'])
        paths = ['knowledge/essence.md', 'knowledge/technical/orders/database/schema.md']
        return {'documents': [{'path': p, 'content': '# '+Path(p).stem+'\n\nFixture knowledge.\n',
                               'kind': 'database' if '/database/' in p else 'technical',
                               'evidence_chunks': ids} for p in paths],
                'file_summaries': [{'path': f['path'], 'summary': 'Observed source behavior.',
                                    'document_paths': paths} for f in s['files'] if f['status']=='included'],
                'dimensions': {d: {'assessment': 'Inspected fixture '+d, 'evidence_chunks': ids}
                               for d in boot.DIMENSIONS},
                'flows': [{'id': 'submit', 'description': 'Submission returns accepted.',
                           'stages': ['entry point', 'return value'], 'evidence_chunks': ids}]}

    def approve(self):
        self.b.claim('independent', 'reviewer')
        self.b.read('independent', self.b.load()['chunks'][0]['id'])
        self.b.review('independent', {'draft_hash': self.b.load()['draft_hash'], 'verdict': 'approved',
                                      'issues': [], 'checks': {k: 'Checked fixture '+k for k in boot.CHECKS}})

    def test_inventory_and_pinned_resume(self):
        s = self.b.status()
        excluded = {f['path'] for f in s['files'] if f['status']=='excluded'}
        self.assertEqual(excluded, {'tests/test_app.py', 'generated/client.py'})
        self.assertIn('README.md', {c['path'] for c in s['pending_chunks']})
        brain.atomic(self.repo/'src/app.py', 'changed remote\n')
        self.git('commit', '-am', 'Change remote')
        self.assertEqual(s['commit'], self.b.prepare('develop-main')['commit'])

    def test_incomplete_coverage_and_read_receipt_block_publication(self):
        with self.assertRaises(ValueError): self.b.stage({})
        self.b.claim('explorer', 'explorer')
        with self.assertRaises(ValueError):
            self.b.submit('explorer', {'chunk_id': self.b.load()['chunks'][0]['id'],
                                      'receipt': 'fake', 'no_knowledge_reason': 'Nothing'})
        self.assertFalse((self.root/'knowledge').exists())

    def test_parallel_limit_and_distinct_reviewer(self):
        self.b.claim('a', 'explorer'); self.b.claim('b', 'explorer')
        with self.assertRaises(ValueError): self.b.claim('c', 'reviewer')
        self.b.release('a')
        with self.assertRaises(ValueError): self.b.claim('a', 'reviewer')
        self.b.claim('c', 'reviewer')

    def test_full_publication_and_one_time_guard(self):
        self.analyze(); self.b.stage(self.plan())
        with self.assertRaises(ValueError): self.b.publish()
        self.approve(); self.b.publish()
        brain.validate(self.root)
        self.assertEqual('completed', self.b.status()['status'])
        with self.assertRaises(ValueError): self.b.prepare('develop-main')
        with self.assertRaises(ValueError): self.b.prepare('another-branch')

    def test_synthesis_database_and_file_accounting_required(self):
        self.analyze()
        for change in ('database', 'summary', 'dimensions', 'flows'):
            p = self.plan()
            if change=='database': p['documents'][1]['kind']='technical'
            if change=='summary': p['file_summaries'].pop()
            if change=='dimensions': del p['dimensions']['domain']
            if change=='flows': p['flows']=[]
            with self.subTest(change=change), self.assertRaises(ValueError): self.b.stage(p)

    def test_review_invalidated_and_existing_changes_guarded(self):
        self.analyze(); self.b.stage(self.plan()); self.approve()
        self.b.stage(self.plan())
        with self.assertRaises(ValueError): self.b.publish()
        self.approve()
        brain.atomic(self.root/'knowledge/new.md', '# External change\n')
        with self.assertRaises(ValueError): self.b.publish()

    def test_split_preserves_exact_coverage(self):
        c = self.b.load()['chunks'][0]
        result = self.b.split(c['id'], 5)
        self.assertGreater(len(result['new_chunks']), 1)
        self.analyze(); self.b.coverage(self.b.load())
        self.assertNotIn(c['id'], self.b.load()['results'])

    def test_block_requires_explicit_unblock(self):
        old = self.b.status()['commit']
        self.b.block('Need human help')
        with self.assertRaises(ValueError): self.b.prepare('develop-main')
        self.b.unblock()
        self.assertEqual(old, self.b.prepare('develop-main')['commit'])

    def test_interrupted_publication_recovery_and_external_edit(self):
        self.analyze(); self.b.stage(self.plan()); self.approve()
        with patch.object(brain, 'graph', side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt): self.b.publish()
        p = self.root/'knowledge/essence.md'
        original = p.read_text()
        brain.atomic(p, '# User edit after interruption\n')
        with self.assertRaises(ValueError): self.b.recover()
        self.assertEqual('# User edit after interruption\n', p.read_text())
        brain.atomic(p, original)
        self.b.recover()
        self.assertFalse(p.exists())
        self.assertEqual('analyzing', self.b.status()['status'])
        self.b.publish()

    def test_ordinary_publication_error_rolls_back(self):
        self.analyze(); self.b.stage(self.plan()); self.approve()
        with patch.object(brain, 'validate', side_effect=ValueError('fixture failure')):
            with self.assertRaises(ValueError): self.b.publish()
        self.assertFalse((self.root/'knowledge/essence.md').exists())
        self.assertFalse(self.b.journal.exists())

    def test_state_markdown_never_enters_graph(self):
        brain.atomic(self.b.home/'private.md', '# Internal draft\n')
        brain.graph(self.root)
        self.assertNotIn('private', (self.root/'index.md').read_text())

    def test_only_one_repo_in_progress(self):
        c=copy.deepcopy(self.c)
        c['repositories'].append(dict(c['repositories'][0], id='other'))
        with self.assertRaises(ValueError): boot.Bootstrap(c, 'other').prepare('develop-main')

    def test_long_line_ranges_have_no_gaps(self):
        text='x'*(boot.CHUNK_CHARS*3+7)
        chunks=boot.units_for('long.py', 'blob', text)
        self.assertEqual(text, ''.join(text[c['start']:c['end']] for c in chunks))
        self.assertEqual(4, len(chunks))

    def test_document_extraction_keeps_provenance_and_integrity(self):
        # Build a fresh snapshot with a non-UTF8 repository document.
        (self.repo/'manual.txt').write_bytes(b'caf\xe9')
        self.git('add', '.'); self.git('commit', '-m', 'Legacy document')
        c=copy.deepcopy(self.c); c['brain_dir']=str(self.base/'other-brain')
        b=boot.Bootstrap(c, 'orders'); b.prepare('develop-main')
        entry=next(f for f in b.status()['files'] if f['path']=='manual.txt')
        self.assertEqual('blocked', entry['status'])
        extraction=self.base/'extraction.txt'; extraction.write_text('café', encoding='utf-8')
        b.extract('manual.txt', extraction, 'Decoded pinned blob using ISO-8859-1')
        b.claim('reader', 'explorer')
        chunk=next(c for c in b.status()['pending_chunks'] if c['path']=='manual.txt')
        self.assertEqual('café', b.read('reader', chunk['id'])['content'])
        f=next(f for f in b.load()['files'] if f['path']=='manual.txt')
        self.assertEqual(entry['sha256'], f['extraction']['source_sha256'])
        (b.home/'extractions'/f['extraction']['file']).write_text('tampered')
        with self.assertRaises(ValueError): b.read('reader', chunk['id'])

    def test_resume_uses_git_pin_if_interrupted_before_state_commit_save(self):
        state=self.b.load(); original=state['commit']
        state['commit']=None; state['status']='preparing'; self.b.save(state)
        brain.atomic(self.repo/'src/app.py', 'new remote head\n')
        self.git('commit', '-am', 'Move branch')
        self.assertEqual(original, self.b.prepare('develop-main')['commit'])

    def test_recovery_preserves_crlf_existing_notes(self):
        p=self.root/'knowledge/existing.md'
        p.parent.mkdir(parents=True)
        original=b'# Existing\r\n\r\nKeep bytes.\r\n'
        p.write_bytes(original)
        self.analyze(); self.b.stage(self.plan()); self.approve()
        with patch.object(brain, 'validate', side_effect=ValueError('fixture failure')):
            with self.assertRaisesRegex(ValueError, 'fixture failure'): self.b.publish()
        self.assertEqual(original, p.read_bytes())


if __name__ == '__main__': unittest.main()
