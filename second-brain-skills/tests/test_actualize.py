import copy
import json
from pathlib import Path
from unittest.mock import patch
import unittest
import test_bootstrap as fixture
import brain
import bootstrap
from actualize import Actualize

class ActualizeTests(unittest.TestCase):
    setUp=fixture.BootstrapTests.setUp
    git=fixture.BootstrapTests.git
    analyze=fixture.BootstrapTests.analyze
    def start(self, legacy=False):
        self.c['repositories'][0]['branch']='develop-main'
        if legacy:
            s=self.b.load(); s['status']='completed'; self.b.save(s)
        else:
            self.b.state_path.unlink()
        self.b=Actualize(self.c,'orders')
        return self.b.prepare()
    def change(self,path='src/app.py',text='def submit():\n    return "rejected"\n'):
        brain.atomic(self.repo/path,text); self.git('add','.'); self.git('commit','-m','Change')
        return self.git('rev-parse','HEAD')
    def scope(self):
        s=self.b.load()
        self.b.impact({'mode':'full','reason':'Examine all flow impacts in this fixture',
            'deletions':[{'path':x['path'],'assessment':'Removed behavior requires documentation cleanup'} for x in s['changes'] if x['status']=='D']})
    def plan(self):
        p=fixture.BootstrapTests.plan(self)
        p['change_assessment']='Current return result and schema assessed together.'
        p['change_dispositions']=[{'path':x['path'],'assessment':'Checked before and after scope.'} for x in self.b.load()['changes']]
        for d in p['documents']:
            target=self.root/d['path']
            if target.exists(): d['expected_sha256']=bootstrap.sha(target.read_bytes())
        return p
    def approve(self):
        self.b.claim('independent','reviewer')
        for c in self.b.load()['chunks']: self.b.read('independent',c['id'])
        self.b.review('independent',{'draft_hash':self.b.load()['draft_hash'],'verdict':'approved','issues':[],
            'checks':{k:'Checked fixture '+k for k in bootstrap.CHECKS},
            'document_checks':{d['path']:'Compared source and proposed content' for d in self.b.load()['draft']['documents']},
            'impact_check':'All fixture flows covered','deletion_check':'Checked removed paths','cross_repository_check':'No other repository modified'})
    def finish(self):
        self.scope(); self.analyze(); self.b.stage(self.plan()); self.approve(); return self.b.publish()
    def test_initial_and_incremental_checkpoint(self):
        self.start(); first=self.b.load()['commit']; self.finish()
        self.assertEqual(first,self.b.load()['checkpoint'])
        second=self.change(); state=self.b.prepare()
        self.assertEqual(first,state['baseline_commit']); self.assertEqual([second],state['commits'])
        self.assertEqual(first,state['checkpoint']); self.finish()
        self.assertEqual(second,self.b.load()['checkpoint'])
        before=self.b.state_path.read_bytes()
        self.assertTrue(self.b.prepare()['no_changes']); self.assertEqual(before,self.b.state_path.read_bytes())
    def test_import_completed_bootstrap_excludes_its_commit(self):
        old=self.git('rev-parse','HEAD'); new=self.change()
        state=self.start(legacy=True)
        self.assertEqual(old,state['baseline_commit']); self.assertEqual([new],state['commits'])
        self.assertTrue(self.b.legacy.exists())
    def test_import_same_tip_requires_no_analysis(self):
        state=self.start(legacy=True)
        self.assertTrue(state['no_changes']); self.assertEqual('completed',state['status'])
    def test_missing_legacy_commit_asks(self):
        s=self.b.load(); s.update(status='completed',commit=None); self.b.save(s)
        self.c['repositories'][0]['branch']='develop-main'; self.b=Actualize(self.c,'orders')
        self.assertEqual('awaiting_baseline',self.b.prepare()['status'])
        self.b.baseline(self.git('rev-parse','HEAD'))
        self.assertEqual([],self.b.load()['changes'])
    def test_rewritten_history_requires_valid_user_baseline(self):
        self.start(); self.finish(); old=self.b.load()['checkpoint']
        self.git('checkout','--orphan','rewritten'); self.git('commit','-m','New root'); self.git('branch','-M','develop-main')
        self.assertEqual('awaiting_baseline',self.b.prepare()['status'])
        with self.assertRaises(ValueError): self.b.baseline(old)
        new=self.git('rev-parse','HEAD'); self.b.baseline(new)
        self.assertEqual(new,self.b.load()['baseline_commit']); self.assertEqual(old,self.b.load()['checkpoint'])
    def test_resume_keeps_pinned_target(self):
        self.start(); pinned=self.b.load()['commit']; self.scope(); self.analyze()
        results=copy.deepcopy(self.b.load()['results']); self.change()
        self.b.prepare()
        self.assertEqual(pinned,self.b.load()['commit']); self.assertEqual(results,self.b.load()['results'])
    def test_changed_file_cannot_be_outside_scope(self):
        self.start(); self.finish(); self.change(); self.b.prepare()
        with self.assertRaisesRegex(ValueError,'every changed'):
            self.b.impact({'mode':'affected','reason':'Bad omission','files':['README.md'],'unaffected':[]})
    def test_affected_scope_and_expand(self):
        self.start(); self.finish(); self.change(); self.b.prepare()
        self.b.impact({'mode':'affected','reason':'App is the changed behavior','files':['src/app.py'],
            'dependency_analysis':'No storage call exists; standalone return function',
            'unaffected':[{'path':p,'reason':'No dependency on changed return'} for p in ['README.md','db/schema.sql']], 'deletions':[]})
        self.assertEqual({'src/app.py'},{c['path'] for c in self.b.load()['chunks']})
        self.b.expand(['db/schema.sql'])
        self.assertEqual({'src/app.py','db/schema.sql'},{c['path'] for c in self.b.load()['chunks']})
    def test_failed_publication_rolls_back_checkpoint_and_documents(self):
        self.start(); self.finish(); old=self.b.load()['checkpoint']; previous=(self.root/'knowledge/essence.md').read_bytes()
        self.change(); self.b.prepare(); self.scope(); self.analyze(); self.b.stage(self.plan()); self.approve()
        with patch.object(brain,'validate',side_effect=ValueError('Injected validation failure')):
            with self.assertRaises(ValueError): self.b.publish()
        self.assertEqual(old,self.b.load()['checkpoint']); self.assertEqual(previous,(self.root/'knowledge/essence.md').read_bytes())
        self.assertFalse(self.b.journal.exists())
    def test_deleted_topic_and_links_and_thoughts_preservation(self):
        self.start(); self.finish(); self.change(); self.b.prepare(); self.scope(); self.analyze()
        obsolete=self.root/'knowledge/domain/obsolete.md'; brain.atomic(obsolete,'# Removed feature\n')
        referring=self.root/'knowledge/domain/still-valid.md'; brain.atomic(referring,'# Other feature\n\n[Former](obsolete.md)\n')
        thought=self.root/'thoughts/notes/ideas.md'; brain.atomic(thought,'# Unchanged thoughts\n')
        p=self.plan(); p['delete_documents']=[{'path':'knowledge/domain/obsolete.md','expected_sha256':bootstrap.sha(obsolete.read_bytes()),'reason':'No longer implemented','other_repository_check':'No other variants in this note'}]
        self.b.stage(p); self.approve(); self.b.publish()
        self.assertFalse(obsolete.exists()); self.assertNotIn('(obsolete.md)',referring.read_text())
        self.assertEqual('# Unchanged thoughts\n',thought.read_text()); brain.validate(self.root)
    def test_delete_adr_rejected(self):
        self.start(); self.scope(); self.analyze(); p=self.plan()
        p['delete_documents']=[{'path':'architecture/orders/ADR.md'}]
        with self.assertRaisesRegex(ValueError,'preserve ADR'): self.b.stage(p)
    def test_reserved_deletion_path_rejected_before_read(self):
        self.start(); self.scope(); self.analyze(); p=self.plan()
        p['delete_documents']=[{'path':'knowledge/domain/archive/old.md'}]
        with self.assertRaisesRegex(ValueError,'Reserved path'): self.b.stage(p)
    def test_deleted_document_restored_after_failed_publication(self):
        self.start(); self.finish(); old=self.b.load()['checkpoint']
        self.change(); self.b.prepare(); self.scope(); self.analyze()
        target=self.root/'knowledge/domain/old.md'; brain.atomic(target,'# Previous behavior\n')
        p=self.plan(); p['delete_documents']=[{'path':'knowledge/domain/old.md',
            'expected_sha256':bootstrap.sha(target.read_bytes()),'reason':'Removed feature',
            'other_repository_check':'No other project relies on it'}]
        self.b.stage(p); self.approve()
        with patch.object(brain,'validate',side_effect=ValueError('Injected failure after deletion')):
            with self.assertRaises(ValueError): self.b.publish()
        self.assertEqual('# Previous behavior\n',target.read_text())
        self.assertEqual(old,self.b.load()['checkpoint'])
    def test_diff_reads_before_and_after_without_local_worktree(self):
        self.start(); self.finish(); self.change(); self.b.prepare()
        brain.atomic(self.repo/'src/app.py','uncommitted text\n')
        diff=self.b.diff('src/app.py')['content']
        self.assertIn('-    return "accepted"',diff)
        self.assertIn('+    return "rejected"',diff)
        self.assertNotIn('uncommitted',diff)
    def test_empty_scope_has_review_before_checkpoint(self):
        self.start(); self.finish(); old=self.b.load()['checkpoint']
        self.change('tests/test_app.py','assert True\n'); new=self.git('rev-parse','HEAD'); self.b.prepare()
        included=[f['path'] for f in self.b.load()['files'] if f['status']=='included']
        self.b.impact({'mode':'affected','files':[],'reason':'Only excluded tests changed','dependency_analysis':'No production file changes',
            'unaffected':[{'path':p,'reason':'Unchanged production source'} for p in included],'deletions':[]})
        p={'documents':[],'empty_scope_assessment':'Only tests changed; existing knowledge is current',
           'change_assessment':'No production changes','change_dispositions':[{'path':'tests/test_app.py','assessment':'Test-only excluded source'}]}
        self.b.stage(p)
        with self.assertRaises(ValueError): self.b.publish()
        self.assertEqual(old,self.b.load()['checkpoint']); self.approve(); self.b.publish()
        self.assertEqual(new,self.b.load()['checkpoint'])
    def test_cross_workflow_journal_blocks_write(self):
        self.start(); brain.atomic(self.b.journal,'{}')
        with self.assertRaisesRegex(ValueError,'recover'):
            brain.publish(self.c,{'stage':'knowledge','documents':[],'human_review_complete':True})

if __name__=='__main__': unittest.main()
