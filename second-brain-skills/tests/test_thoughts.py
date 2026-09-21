import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]/'runtime'))
import brain
import thoughts as t


class ThoughtTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source='thoughts/drafts/example.md'
        brain.atomic(self.root/self.source, '# Rough\n\n## Ideas\nTry batching.\n')
        self.note='thoughts/notes/ideas.md'

    def plan(self):
        return {'clarifications_complete': True,
                'sources': [{'path': self.source, 'sha256': t.read(self.root,self.source)['sha256']}],
                'documents': [{'path': self.note, 'content': '# Ideas\n\n## Batching\nTry a batching experiment.\n',
                               'sources': [self.source]}]}

    def relation(self):
        a='thoughts/notes/reflections/batching.md'; b='knowledge/technical/one/batching.md'
        brain.atomic(self.root/a, '# Reflection\r\n\r\nMy observation.\r\n')
        brain.atomic(self.root/b, '# Batching\n\nCurrent implementation.\n')
        return {'source': a, 'source_sha256': t.read(self.root,a)['sha256'],
                'target': b, 'target_sha256': t.read(self.root,b)['sha256'],
                'reason': 'The reflection discusses the documented batching behavior.'}

    def test_refine_archives_original_and_adds_provenance(self):
        original=(self.root/self.source).read_bytes()
        t.refine(self.root,self.plan())
        self.assertFalse((self.root/self.source).exists())
        self.assertEqual(original,(self.root/'archive/thoughts/example.md').read_bytes())
        self.assertIn('../../archive/thoughts/example.md',(self.root/self.note).read_text())
        self.assertFalse((self.root/'personal').exists())

    def test_unresolved_clarification_no_writes(self):
        plan=self.plan(); plan['clarifications_complete']=False
        with self.assertRaises(ValueError): t.refine(self.root,plan)
        self.assertTrue((self.root/self.source).exists())
        self.assertFalse((self.root/self.note).exists())

    def test_cannot_publish_thought_as_domain_fact_or_personal(self):
        for name in ['knowledge/domain/topic.md','personal/daily.md','thoughts/notes/ideas/topic.md']:
            plan=self.plan(); plan['documents'][0]['path']=name
            with self.subTest(name=name), self.assertRaises(ValueError): t.refine(self.root,plan)

    def test_changed_source_and_existing_note_require_hash(self):
        plan=self.plan(); brain.atomic(self.root/self.source,'changed')
        with self.assertRaises(ValueError): t.refine(self.root,plan)
        plan=self.plan(); brain.atomic(self.root/self.note,'# Existing\n')
        with self.assertRaises(ValueError): t.refine(self.root,plan)
        plan['documents'][0]['expected_sha256']=t.read(self.root,self.note)['sha256']
        t.refine(self.root,plan)

    def test_every_draft_requires_output(self):
        plan=self.plan(); plan['documents']=[]
        with self.assertRaises(ValueError): t.refine(self.root,plan)

    def test_link_preserves_body_and_is_idempotent(self):
        r=self.relation(); a=self.root/r['source']; b=self.root/r['target']
        originals=[p.read_bytes() for p in (a,b)]
        t.link(self.root,{'relations':[r]})
        for p,original in zip((a,b),originals): self.assertTrue(p.read_bytes().startswith(original))
        for key in ('source','target'): r[key+'_sha256']=t.read(self.root,r[key])['sha256']
        self.assertEqual([],t.link(self.root,{'relations':[r]})['written'])

    def test_inventory_and_link_exclude_drafts_inbox_archive(self):
        r=self.relation()
        for directory in ['inbox','archive','thoughts/drafts']:
            brain.atomic(self.root/directory/'secret.md','# Secret\n')
        names={x['path'] for x in t.inventory(self.root,'notes')}
        self.assertEqual({r['source'],r['target']},names)
        r['target']=self.source; r['target_sha256']=t.read(self.root,self.source)['sha256']
        with self.assertRaises(ValueError): t.link(self.root,{'relations':[r]})

    def test_link_never_reads_archive_or_inbox(self):
        r=self.relation()
        original=Path.read_bytes
        def guarded(p,*args,**kwargs):
            if p.is_relative_to(self.root/'archive') or p.is_relative_to(self.root/'inbox'):
                raise AssertionError('Excluded source read')
            return original(p,*args,**kwargs)
        with patch.object(Path,'read_bytes',guarded):
            t.inventory(self.root,'notes'); t.link(self.root,{'relations':[r]})

    def test_interruption_recovers_outputs_and_move(self):
        plan=self.plan()
        original_unlink=Path.unlink
        def interrupt(p,*args,**kwargs):
            if p==t.journal_path(self.root): raise KeyboardInterrupt()
            return original_unlink(p,*args,**kwargs)
        with patch.object(Path,'unlink',interrupt):
            with self.assertRaises(KeyboardInterrupt): t.refine(self.root,plan)
        self.assertFalse((self.root/self.source).exists())
        t.recover(self.root)
        self.assertTrue((self.root/self.source).exists())
        self.assertFalse((self.root/self.note).exists())

    def test_recovery_stops_for_external_output_edit(self):
        plan=self.plan()
        with patch.object(Path,'rename',side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt): t.refine(self.root,plan)
        brain.atomic(self.root/self.note,'External edit')
        with self.assertRaises(ValueError): t.recover(self.root)
        self.assertEqual('External edit',(self.root/self.note).read_text())

    def test_archive_collision_keeps_previous_file_unread(self):
        p=self.root/'archive/thoughts/example.md'; brain.atomic(p,'Prior source')
        result=t.refine(self.root,self.plan())
        self.assertNotEqual('archive/thoughts/example.md',result['archived'][0])
        self.assertEqual('Prior source',p.read_text())

    def test_incoming_draft_links_repaired(self):
        p=self.root/'knowledge/domain/reference.md'
        brain.atomic(p,'# Context\n\n[Draft](../../thoughts/drafts/example.md)\n')
        t.refine(self.root,self.plan())
        self.assertIn('../../archive/thoughts/example.md',p.read_text())


if __name__=='__main__': unittest.main()
