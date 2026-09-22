#!/usr/bin/env python3
"""Pinned, incremental source-to-knowledge synchronization; Python standard library."""
import argparse
import copy
import json
from pathlib import Path
import re
import subprocess
import brain
from bootstrap import Bootstrap, canonical, sha, stamp, write_json, nonempty, exclusion


class Actualize(Bootstrap):
    def __init__(self, config, repo_id):
        super().__init__(config, repo_id)
        self.legacy = self.state_path
        self.home = self.root / '.state/actualize' / repo_id
        self.state_path = self.home / 'state.json'
        self.bare = self.home / 'snapshot.git'
        self.journal = self.root / '.state/actualize-publishing.json'

    def editable(self, state):
        for name in ('bootstrap','thoughts'):
            if (self.root/('.state/'+name+'-publishing.json')).exists():
                brain.fail('Recover interrupted '+name+' publication first')
        if state['status'] == 'awaiting_baseline':
            brain.fail('Ask the user for an already documented commit; run baseline --commit SHA')
        super().editable(state)

    def save(self, state):
        # Publication completion and checkpoint live in one atomically replaced file.
        if state.get('status') == 'completed':
            state['checkpoint'] = state['commit']
            state['checkpoint_branch'] = state['branch']
        super().save(state)

    def valid_ancestor(self, commit, target):
        if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-fA-F]{40}|[0-9a-fA-F]{64}', commit):
            return False
        try:
            self.git('cat-file', '-e', commit + '^{commit}')
            self.git('merge-base', '--is-ancestor', commit, target)
            return True
        except RuntimeError:
            return False

    def prepare(self):
        branch = self.repo.get('branch')
        if not branch: brain.fail('Add branch to this repository in YAML; never guess it')
        if branch.startswith('-'): brain.fail('Invalid branch')
        brain.run(['git', 'check-ref-format', 'refs/heads/' + branch])
        for journal in ('actualize', 'bootstrap', 'thoughts'):
            if (self.root / ('.state/' + journal + '-publishing.json')).exists():
                brain.fail('Recover interrupted ' + journal + ' publication first')
        previous = self.load() if self.state_path.exists() else None
        if previous and previous['status'] != 'completed':
            if previous['branch'] != branch: brain.fail('Restore the original configured branch to resume this run')
            self.editable(previous)
            if previous['status'] == 'preparing': self.prepare_inventory(previous)
            return self.status()
        for other in (self.root / '.state/actualize').glob('*/state.json'):
            if other != self.state_path and json.loads(other.read_text())['status'] != 'completed':
                brain.fail('Finish or resolve the other repository run first')
        checkpoint = previous.get('checkpoint') if previous else None
        checkpoint_branch = previous.get('checkpoint_branch') if previous else branch
        legacy_problem = None
        if not previous and self.legacy.exists():
            try:
                legacy = json.loads(self.legacy.read_text())
                if legacy.get('status') != 'completed':
                    brain.fail('Old bootstrap is not completed; finish it before importing its checkpoint')
                if legacy.get('repo_id') != self.repo['id']: brain.fail('Legacy repository identity mismatch')
                checkpoint = legacy.get('commit')
                checkpoint_branch = legacy.get('branch')
                if not checkpoint: legacy_problem = 'Completed bootstrap has no commit'
            except (json.JSONDecodeError, UnicodeError):
                legacy_problem = 'Cannot read old bootstrap state; ask for the documented commit'
        self.home.mkdir(parents=True, exist_ok=True)
        if not self.bare.exists(): brain.run(['git', '-c', 'core.hooksPath=/dev/null', 'init', '--bare', str(self.bare)])
        remote = brain.run(['git', '-C', self.repo['path'], 'remote', 'get-url', self.repo['remote']]).strip()
        # Full ancestry is necessary to validate arbitrary checkpoints; no checkout/build.
        self.git('fetch', '--no-tags', remote, '+refs/heads/' + branch + ':refs/actualize/remote', retries=3)
        target = self.git('rev-parse', 'refs/actualize/remote^{commit}').decode().strip()
        if previous and checkpoint == target and checkpoint_branch == branch:
            return dict(self.status(), no_changes=True)
        if previous:
            write_json(self.home / 'runs' / (previous['commit'] + '.json'), previous)
        state = {'repo_id':self.repo['id'], 'branch':branch, 'commit':target,
                 'checkpoint':checkpoint, 'checkpoint_branch':checkpoint_branch,
                 'baseline_commit':checkpoint, 'status':'preparing', 'created_at':stamp(),
                 'policy_version':1, 'files':[], 'chunks':[], 'workers':{}, 'reads':{},
                 'results':{}, 'draft':None, 'review':None, 'events':[],
                 'previous_flows': (previous or {}).get('draft',{}).get('flows',[]) if (previous or {}).get('draft') else [],
                 'previous_tasks':(previous or {}).get('analysis_plan',{}).get('tasks',[])}
        if legacy_problem or checkpoint_branch != branch or (checkpoint and not self.valid_ancestor(checkpoint,target)):
            state['status'] = 'awaiting_baseline'
            state['blocker'] = legacy_problem or 'Baseline is missing from branch history or configured branch changed'
            self.save(state)
            return self.status()
        self.save(state)
        if checkpoint == target and checkpoint_branch == branch:
            state['status']='completed'
            state['completed_at']=stamp()
            self.save(state)
            return dict(self.status(),no_changes=True)
        self.prepare_inventory(state)
        return self.status()

    def prepare_inventory(self, state):
        try:
            self.inventory(state)
            state['full_files'] = copy.deepcopy(state['files'])
            state['full_chunks'] = copy.deepcopy(state['chunks'])
            base = state.get('baseline_commit')
            if base:
                # No rename heuristic: deletion + addition is explicit and cannot hide a removal.
                raw = self.git('diff', '--name-status', '--no-renames', '-z', base, state['commit']).decode().split('\0')
                state['changes'] = [{'status':raw[i], 'path':raw[i+1]} for i in range(0,len(raw)-1,2)]
                state['commits'] = self.git('rev-list', '--reverse', base + '..' + state['commit']).decode().splitlines()
            else:
                state['changes'] = [{'status':'A','path':f['path']} for f in state['files']]
                state['commits'] = []  # initial analysis is a snapshot, not a historical replay
            state['status'] = 'analyzing'
            self.refresh_manifest(state)
            self.save(state)
        except (ValueError, RuntimeError, OSError) as e:
            state.update(status='blocked',resume_status='preparing',blocker=str(e))
            self.save(state)
            raise

    def baseline(self, commit):
        s = self.load()
        if s['status'] != 'awaiting_baseline': brain.fail('Replacement baseline is only accepted after a baseline question')
        if not self.valid_ancestor(commit,s['commit']): brain.fail('Provide a full existing ancestor commit SHA of the pinned target')
        s['baseline_commit'] = commit.lower()
        s['events'].append({'event':'user-baseline','commit':commit.lower(),'at':stamp()})
        s.pop('blocker',None); s['status']='preparing'; self.save(s)
        self.prepare_inventory(s)
        return self.status()

    def status(self):
        result = super().status(); s = self.load()
        result.update(checkpoint=s.get('checkpoint'), baseline_commit=s.get('baseline_commit'),
                      changes=s.get('changes',[]), commits=s.get('commits',[]),
                      scope=s.get('impact'), previous_tasks=s.get('previous_tasks',[]))
        return result

    def inspect(self, path, revision='target', start=0, size=12000):
        s=self.load(); self.editable(s)
        if revision not in ('target','baseline'): brain.fail('Invalid revision')
        if start<0 or size<1 or size>24000: brain.fail('Invalid read range')
        commit=s['commit'] if revision=='target' else s.get('baseline_commit')
        if not commit: brain.fail('No baseline on initial analysis')
        # cat-file reads a blob, including a symlink target; never follows filesystem links.
        text=self.git('cat-file','blob',commit+':'+path).decode('utf-8-sig')
        if '\0' in text: brain.fail('Binary source requires explicit extraction')
        return {'path':path,'revision':revision,'commit':commit,'start':start,
                'end':min(len(text),start+size),'total_characters':len(text),'content':text[start:start+size]}

    def diff(self, path, start=0, size=12000):
        s=self.load(); self.editable(s)
        if start<0 or size<1 or size>24000: brain.fail('Invalid diff range')
        if not s.get('baseline_commit'): brain.fail('Initial analysis uses source snapshot, not history')
        if path not in {x['path'] for x in s['changes']}: brain.fail('Select a changed path')
        text=self.git('diff','--no-ext-diff','--no-textconv','--no-renames',s['baseline_commit'],s['commit'],'--',':(literal)'+path).decode('utf-8',errors='replace')
        return {'path':path,'start':start,'end':min(len(text),start+size),'total_characters':len(text),'content':text[start:start+size]}

    def impact(self, plan):
        s=self.load(); self.editable(s)
        if s['results'] or s.get('analysis_plan'): brain.fail('Choose scope before organize; use expand afterward')
        full={f['path']:f for f in s['full_files']}
        included={p for p,f in full.items() if f['status']!='excluded'}
        nonempty(plan.get('reason'),'impact reasoning')
        selected=set(plan.get('files',[]))
        if plan.get('mode')=='full': selected=included
        elif plan.get('mode')!='affected': brain.fail('Impact mode must be full or affected')
        if not s.get('baseline_commit') and selected!=included: brain.fail('Initial analysis must cover the full snapshot')
        required={x['path'] for x in s['changes'] if x['path'] in included}
        if not required<=selected or not selected<=included: brain.fail('Scope must include every changed in-scope target file')
        omissions=plan.get('unaffected',[])
        if plan['mode']=='affected':
            if {x.get('path') for x in omissions} != included-selected: brain.fail('Explain every file outside the impact scope')
            for x in omissions: nonempty(x.get('reason'),'unaffected explanation')
            nonempty(plan.get('dependency_analysis'),'dependency analysis')
        removed={x['path'] for x in s['changes'] if x['status']=='D'}
        assessments=plan.get('deletions',[])
        if {x.get('path') for x in assessments} != removed: brain.fail('Assess every removed source path')
        for x in assessments: nonempty(x.get('assessment'),'removed source impact')
        s['impact']=dict(plan,files=sorted(selected))
        s['files']=[dict(f,status='out-of-scope',reason='See impact assessment') if f['path'] not in selected and f['status']!='excluded' else f for f in copy.deepcopy(s['full_files'])]
        s['chunks']=[c for c in copy.deepcopy(s['full_chunks']) if c['path'] in selected]
        self.refresh_manifest(s); self.save(s); return self.status()

    def expand(self, paths):
        s=self.load(); self.editable(s)
        if not s.get('impact'): brain.fail('Record impact first')
        valid={f['path'] for f in s['full_files'] if f['status']!='excluded'}
        if not set(paths)<=valid: brain.fail('Unknown expansion path')
        current={f['path'] for f in s['files'] if f['status'] in ('included','blocked')}
        add=set(paths)-current
        s['files']=[copy.deepcopy(next(f for f in s['full_files'] if f['path']==old['path'])) if old['path'] in add else old for old in s['files']]
        s['chunks'].extend(copy.deepcopy(c) for c in s['full_chunks'] if c['path'] in add)
        s['impact']['files']=sorted(current|add)
        s['impact']['unaffected']=[x for x in s['impact'].get('unaffected',[]) if x['path'] not in add]
        self.refresh_manifest(s); self.save(s); return self.status()

    def coverage(self,s):
        if not s.get('impact'): brain.fail('Record the impact plan before publication')
        if not s['chunks']:
            if any(f['status'] in ('included','blocked') for f in s['files']): brain.fail('Missing source chunks')
            # Empty scope is valid only when no target source is required, e.g. all source deleted.
            return
        super().coverage(s)

    def document_checks(self,s,plan):
        for d in plan.get('documents',[]) + plan.get('delete_documents',[]):
            if set(Path(d['path']).parts)&{'archive','thoughts','.state','.git'}:
                brain.fail('Reserved path is outside publication or deletion scope')
        self.coverage(s)
        if s['chunks']:
            super().document_checks(s,plan)
        else:
            nonempty(plan.get('empty_scope_assessment'),'empty scope assessment')
            if plan.get('finding_dispositions') or plan.get('flows'): brain.fail('Empty scope cannot assert source findings or flows')
        nonempty(plan.get('change_assessment'),'cumulative change assessment')
        changes={x['path'] for x in s['changes']}
        if {x.get('path') for x in plan.get('change_dispositions',[])}!=changes:
            brain.fail('Account for every changed path, including deletions and exclusions')
        for x in plan['change_dispositions']:
            nonempty(x.get('assessment'),'change disposition')
        documents=plan.get('documents',[])
        paths=set()
        for d in documents:
            p=brain.safe(self.root,d['path'])
            if set(Path(d['path']).parts)&{'archive','thoughts','.state','.git'}: brain.fail('Reserved path is outside publication scope')
            if p.suffix!='.md' or not (d['path'].startswith('knowledge/') or d['path'].startswith('architecture/')):
                brain.fail('Only knowledge and architecture outputs')
            if p.relative_to(self.root).as_posix()!=d['path'] or d['path'] in paths: brain.fail('Duplicate or noncanonical path')
            paths.add(d['path']); nonempty(d.get('content'),'document content')
            if p.exists() and sha(p.read_bytes())!=d.get('expected_sha256'): brain.fail('Existing document changed')
            if d['path'].startswith('architecture/') and not p.exists() and brain.split_note(d['content'])[0].get('status')!='proposed':
                brain.fail('New ADR must be proposed')
            if d['path'].startswith('knowledge/technical/') and not (d['path'].startswith('knowledge/technical/'+self.repo['id']+'/') or d['path'].startswith('knowledge/technical/shared/')):
                brain.fail('Do not update another repository technical documentation')
        deleted=set()
        for d in plan.get('delete_documents',[]):
            p=brain.safe(self.root,d['path'])
            if set(Path(d['path']).parts)&{'archive','thoughts','.state','.git'}: brain.fail('Reserved path is outside deletion scope')
            if not d['path'].startswith('knowledge/') or d['path']=='knowledge/essence.md' or p.suffix!='.md':
                brain.fail('Delete only obsolete knowledge topics; preserve ADR history and essence')
            if p.relative_to(self.root).as_posix()!=d['path'] or d['path'] in deleted or d['path'] in paths: brain.fail('Invalid deletion path')
            if d['path'].startswith('knowledge/technical/') and not (d['path'].startswith('knowledge/technical/'+self.repo['id']+'/') or d['path'].startswith('knowledge/technical/shared/')):
                brain.fail('Do not delete another repository technical documentation')
            if not p.is_file() or sha(p.read_bytes())!=d.get('expected_sha256'): brain.fail('Reread deleted document')
            nonempty(d.get('reason'),'deletion reason'); nonempty(d.get('other_repository_check'),'other repository preservation check')
            deleted.add(d['path'])
        outputs={brain.safe(self.root,d['path']):d['content'] for d in documents}
        removed={brain.safe(self.root,p) for p in deleted}
        for p in set(brain.active(self.root))|set(outputs):
            if p in removed: continue
            content=outputs.get(p) if p in outputs else p.read_text()
            for target in brain.targets(p,content):
                if target in removed: continue # publisher removes obsolete links, retaining their text
                if not target.is_relative_to(self.root) or target.is_relative_to(self.root/'.state') or (not target.exists() and target not in outputs):
                    brain.fail('Broken proposed link: '+str(target))

    def review(self,worker,result):
        s=self.load()
        if result.get('verdict')=='approved':
            for key in ('impact_check','deletion_check','cross_repository_check'):
                nonempty(result.get(key),key)
        if s['chunks']: return super().review(worker,result)
        self.editable(s); self.worker(s,worker,'reviewer')
        if not s.get('draft') or result.get('draft_hash')!=s.get('draft_hash'): brain.fail('Review must match draft')
        if result.get('verdict') not in ('approved','changes_requested'): brain.fail('Invalid verdict')
        if not isinstance(result.get('issues'),list) or (result['verdict']=='approved' and result['issues']): brain.fail('Review issues invalid')
        if set(result.get('document_checks',{}))!={d['path'] for d in s['draft']['documents']}: brain.fail('Review every output')
        for v in result['document_checks'].values(): nonempty(v,'document check')
        s['review']=dict(result,worker=worker,reviewed_at=stamp()); self.save(s)
        return {'verdict':result['verdict']}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--config',default=str(Path.home()/'.config/second-brain/config.yaml'))
    p.add_argument('--repo',required=True)
    p.add_argument('command',choices=['prepare','status','baseline','inspect','diff','impact','expand','organize','tasks','findings','claim','release','read','submit','task-start','task-finish','split','extract','stage','review','publish','recover','block','unblock'])
    for arg in ('commit','path','plan','worker','role','chunk','result','task','text-file','method','reason'):
        p.add_argument('--'+arg)
    p.add_argument('--revision',default='target',choices=['target','baseline'])
    p.add_argument('--start',type=int,default=0); p.add_argument('--size',type=int,default=12000)
    a=p.parse_args(); b=Actualize(brain.config(a.config),a.repo)
    def data(name):
        value=getattr(a,name)
        if not value: brain.fail('--'+name+' is required')
        return json.loads(Path(value).read_text())
    with brain.lock(b.root):
        c=a.command
        if c=='baseline': result=b.baseline(a.commit)
        elif c=='inspect': result=b.inspect(a.path,a.revision,a.start,a.size)
        elif c=='diff': result=b.diff(a.path,a.start,a.size)
        elif c=='impact': result=b.impact(data('plan'))
        elif c=='expand': result=b.expand(data('plan')['files'])
        elif c in ('organize','stage'): result=getattr(b,c)(data('plan'))
        elif c in ('submit','review'): result=getattr(b,c)(a.worker,data('result'))
        elif c=='task-start': result=b.task_start(a.task,a.worker)
        elif c=='task-finish': result=b.task_finish(a.task,a.worker,data('result'))
        elif c=='claim': result=b.claim(a.worker,a.role)
        elif c=='release': result=b.release(a.worker)
        elif c=='read': result=b.read(a.worker,a.chunk)
        elif c=='split': result=b.split(a.chunk,a.size)
        elif c=='extract': result=b.extract(a.path,a.text_file,a.method)
        elif c=='findings': result=b.findings(b.load())
        elif c=='tasks': result=b.load().get('tasks',{})
        elif c=='block': result=b.block(a.reason)
        else: result=getattr(b,c)()
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    try: main()
    except (ValueError,KeyError,OSError,RuntimeError,TypeError,subprocess.TimeoutExpired) as e:
        raise SystemExit('ERROR: '+str(e))
