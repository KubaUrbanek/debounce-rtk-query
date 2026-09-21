import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('brain', Path(__file__).parents[1]/'runtime/brain.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'brain'
        self.root.mkdir()
        self.c = {'brain_dir': str(self.root), 'author_emails':['me@test.local'],
                  'repositories':[{'id':'one','path':str(Path(self.tmp.name)/'repo'),
                    'gitlab_host':'git.example','gitlab_project':'team/one','remote':'origin'}]}

    def source(self, name='event.md', daily='true', date=None):
        p = self.root/'inbox'/name
        b.atomic(p,b.note_text({'date':date or b.today(),'include_in_daily':daily,'type':'meeting','repositories':'one'},
                              '\n# Meeting\n\nExplicit decision.\n'))
        return p

    def process(self, stage, n, text='Outcome'):
        docs=[]
        if stage=='daily':
            path='personal/'+b.today()+'-daily.md'
            content='# Daily summary — '+dt.date.fromisoformat(b.today()).strftime('%d %m %Y')+'\n\n'+text
            content+='\n\n[Source](../'+n['path']+')\n'
        else:
            path='knowledge/domain/topic.md'
            content='# Topic\n\n'+text+'\n\n[Source](../../'+n['path']+')\n'
        d={'path':path,'content':content}
        if (self.root/path).exists():
            d['expected_sha256']=hashlib.sha256((self.root/path).read_bytes()).hexdigest()
        docs.append(d)
        return b.publish(self.c,{'stage':stage,'human_review_complete':True,
            'documents':docs,'processed':[{'path':n['path'],'hash':n['hash']}]})

    def test_two_stages_archive_in_either_order(self):
        self.source()
        n=b.inventory(self.c,'knowledge')[0]
        self.process('knowledge',n)
        self.assertTrue((self.root/'inbox/event.md').exists())
        n=b.inventory(self.c,'daily')[0]
        self.process('daily',n)
        self.assertTrue((self.root/'archive/event.md').exists())
        self.assertFalse((self.root/'inbox/event.md').exists())
        b.validate(self.root)
        self.assertIn('../archive/event.md',(self.root/'personal'/ (b.today()+'-daily.md')).read_text())

    def test_daily_first_and_content_change_invalidates_knowledge(self):
        self.source()
        self.process('daily',b.inventory(self.c,'daily')[0])
        p=self.root/'inbox/event.md'
        b.atomic(p,p.read_text().replace('Explicit decision.','Revised decision.'))
        n=b.inventory(self.c,'knowledge')[0]
        self.process('knowledge',n)
        self.assertTrue(p.exists())
        self.assertTrue(b.inventory(self.c,'daily')[0]['needs_processing'])
        self.process('daily',b.inventory(self.c,'daily')[0])
        self.assertFalse(p.exists())

    def test_invalid_date_stays_and_is_excluded_from_daily(self):
        self.source(date='2026-02-30')
        self.assertFalse(b.inventory(self.c,'daily')[0]['needs_processing'])
        self.process('knowledge',b.inventory(self.c,'knowledge')[0])
        self.assertTrue((self.root/'inbox/event.md').exists())

    def test_nondurable_source_archives_without_topic(self):
        self.source(daily='false')
        n=b.inventory(self.c,'knowledge')[0]
        b.publish(self.c,{'stage':'knowledge','human_review_complete':True,
            'documents':[],'processed':[{'path':n['path'],'hash':n['hash']}]})
        self.assertTrue((self.root/'archive/event.md').exists())

    def test_late_note_eligible_for_today(self):
        self.source(date='2020-01-01')
        self.assertTrue(b.inventory(self.c,'daily')[0]['needs_processing'])

    def test_source_hash_guard(self):
        p=self.source(); n=b.inventory(self.c,'knowledge')[0]
        b.atomic(p,p.read_text()+'Changed\n')
        with self.assertRaises(ValueError): self.process('knowledge',n)

    def test_graph_updates_do_not_invalidate_content(self):
        self.source(); old=b.inventory(self.c,'knowledge')[0]['hash']
        b.graph(self.root); b.graph(self.root)
        self.assertEqual(old,b.inventory(self.c,'knowledge')[0]['hash'])

    def test_archive_is_not_read(self):
        p=self.root/'archive/secret.md'; b.atomic(p,'Secret')
        original=Path.read_text
        def guarded(path,*args,**kwargs):
            if path.is_relative_to(self.root/'archive'): raise AssertionError('Archive read!')
            return original(path,*args,**kwargs)
        with patch.object(Path,'read_text',guarded):
            b.graph(self.root); b.validate(self.root); b.inventory(self.c,'knowledge')

    def test_restore_preserves_identity_and_rewrites_links(self):
        src=self.root/'archive/2026-09-18-system.md'
        b.atomic(src,'# Original report\n')
        note=self.root/'knowledge/topic.md'
        b.atomic(note,'# Topic\n\n[Source](../archive/2026-09-18-system.md)\n')
        dst=self.root/'inbox/2026-09-18-system.md'
        b.move(self.root,src,dst)
        self.assertFalse(src.exists())
        self.assertEqual('# Original report\n',dst.read_text())
        self.assertIn('../inbox/2026-09-18-system.md',note.read_text())

    def test_new_accepted_adr_rejected(self):
        content=b.note_text({'status':'accepted'},'\n# Decision\n')
        with self.assertRaises(ValueError):
            b.publish(self.c,{'stage':'knowledge','human_review_complete':True,
                'documents':[{'path':'architecture/one/ADR-test.md','content':content}]})

    def test_existing_report_requires_read_hash(self):
        p=self.root/'personal'/(b.today()+'-daily.md')
        content='# Daily summary — '+dt.date.fromisoformat(b.today()).strftime('%d %m %Y')+'\n'
        b.atomic(p,content)
        with self.assertRaises(ValueError):
            b.publish(self.c,{'stage':'daily','documents':[{'path':str(p.relative_to(self.root)),'content':content}]})

    def test_system_merged_timestamp_and_target_filter(self):
        sample=[
            {'iid':1,'merged_at':'2026-09-17T22:01:00Z','target_branch':'develop-v2','title':'Earlier commit merged today'},
            {'iid':2,'merged_at':'2026-09-18T22:00:00Z','target_branch':'develop'},
            {'iid':3,'merged_at':'2026-09-18T10:00:00Z','target_branch':'main'}]
        def api(repo,url):
            if '/diffs?' in url: return [{'diff':'change'}]
            if url.endswith('/1'): return {'changes_count':'1','diff_refs':{'base_sha':'a','head_sha':'b'}}
            return sample
        with patch.object(b,'api',api), patch.object(b,'today',return_value='2026-09-20'):
            result=b.collect_system(self.c,'2026-09-18')
        self.assertEqual([1],[m['iid'] for m in result['repositories'][0]['merge_requests']])
        self.assertEqual([],result['errors'])

    def test_partial_fetch_not_empty_success(self):
        with patch.object(b,'api',side_effect=RuntimeError('unavailable')):
            result=b.collect_system(self.c,b.today())
        self.assertFalse(result['activity']); self.assertTrue(result['errors'])

    def test_pagination(self):
        with patch.object(b,'api',side_effect=[[{'x':1}]*100,[{'x':2}]]):
            self.assertEqual(101,len(list(b.pages(self.c['repositories'][0],'endpoint'))))

    def test_dst_days(self):
        start,end=b.bounds('2026-03-29')
        self.assertEqual(23*3600,end.timestamp()-start.timestamp())
        start,end=b.bounds('2026-10-25')
        self.assertEqual(25*3600,end.timestamp()-start.timestamp())

    def test_yaml_config(self):
        p=Path(self.tmp.name)/'config.yaml'
        text=(Path(__file__).parents[1]/'config.example.yaml').read_text()
        b.atomic(p,text)
        self.assertEqual('case-service',b.config(p)['repositories'][0]['id'])
        b.atomic(p,text.replace('version: 2','version: 2\nversion: 2'))
        with self.assertRaises(ValueError): b.config(p)

    def test_real_local_commits_author_date_and_dedup(self):
        repo=Path(self.c['repositories'][0]['path']); repo.mkdir()
        def git(*args,env=None):
            return subprocess.run(['git','-C',str(repo),*args],check=True,capture_output=True,text=True,env=env).stdout
        git('init'); git('config','user.name','Me'); git('config','user.email','me@test.local')
        b.atomic(repo/'file.txt','one\n'); git('add','file.txt')
        import os
        env=dict(os.environ,GIT_AUTHOR_DATE=b.today()+'T12:00:00+02:00',GIT_COMMITTER_DATE='2020-01-01T12:00:00+00:00')
        git('commit','-m','Experiment',env=env); git('branch','experiment')
        result=b.collect_personal(self.c)
        self.assertEqual(1,len(result['repositories'][0]['commits']))
        self.assertIn('Experiment',result['repositories'][0]['patches'])
        self.assertTrue(result['errors'])  # no origin; local collection still works

    def test_broken_links_prevent_markers(self):
        self.source(); n=b.inventory(self.c,'knowledge')[0]
        with self.assertRaises(ValueError): self.process('knowledge',n,'[Broken](missing.md)')
        self.assertNotIn('knowledge_hash',b.inventory(self.c,'knowledge')[0]['metadata'])


if __name__=='__main__': unittest.main()
