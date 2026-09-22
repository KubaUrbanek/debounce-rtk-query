#!/usr/bin/env python3
"""One-time, static, coverage-gated repository initialization. Standard library only."""
import argparse
import bisect
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import subprocess
import sys
import time

import brain

POLICY_VERSION = 1
CHUNK_CHARS = 12000
DIMENSIONS = ('domain', 'architecture', 'database', 'integrations')
CHECKS = ('coverage', 'domain', 'architecture', 'database', 'integrations', 'flows', 'links')
SKIP_DIRS = {'node_modules', 'vendor', '.venv', 'venv', '__pycache__', '.gradle',
             'target', 'dist', 'coverage', '.next', 'test', 'tests', '__tests__',
             'testfixtures', 'test-fixtures', '__mocks__', 'generated',
             'generated-sources', 'generated-test-sources', '.idea'}
SKIP_SUFFIXES = {'.class', '.pyc', '.jar', '.war', '.dll', '.exe', '.o', '.so',
                 '.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.woff', '.woff2',
                 '.ttf', '.mp4', '.mp3', '.zip', '.gz'}


def sha(value):
    return hashlib.sha256(value).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def stamp():
    return dt.datetime.now(brain.TZ).isoformat()


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        brain.fail(label + ' must be nonempty text')


def write_json(path, data):
    brain.atomic(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def units_for(path, oid, text, size=CHUNK_CHARS, lower=0, upper=None):
    upper = len(text) if upper is None else upper
    starts = [0] + [m.end() for m in re.finditer('\n', text)]
    units = []
    for start in range(lower, max(lower+1,upper), size):
        end = min(start+size,upper)
        units.append({'id':sha((path+'\0'+str(start)+'\0'+str(end)).encode())[:20],
                      'path':path,'oid':oid,'start':start,'end':end,
                      'start_line':bisect.bisect_right(starts,start),
                      'end_line':bisect.bisect_right(starts,max(start,end-1)),
                      'sha256':sha(text[start:end].encode())})
    return units


def exclusion(path, data=None):
    parts = PurePosixPath(path).parts
    lowered = [x.lower() for x in parts]
    for part in lowered[:-1]:
        if part in SKIP_DIRS:
            return 'Shared exclusion: tests, dependencies, generated files or artifacts (' + part + ')'
    name = parts[-1]
    if name in ('package-lock.json', 'pnpm-lock.yaml', 'yarn.lock', 'poetry.lock', 'uv.lock'):
        return 'Generated dependency lockfile; manifests remain in scope'
    if (re.search(r'(?:\.test|\.spec)\.[^.]+$', name, re.I)
            or re.fullmatch(r'test_.*\.py|.*_test\.py', name)
            or re.fullmatch(r'.*(?:Test|Tests|IT)\.java|.*Spec\.groovy', name)):
        return 'Test-code filename'
    if PurePosixPath(path).suffix.lower() in SKIP_SUFFIXES:
        return 'Binary asset or compiled artifact'
    if name.endswith(('.min.js', '.min.css', '.map')):
        return 'Generated/minified artifact'
    if data is not None:
        header = data[:2048].decode('utf-8', errors='ignore').lower()
        if re.search(r'(?:auto[- ]generated|automatically generated|@generated).*?(?:do not edit|\bfile\b)', header):
            return 'Explicit generated-file header'
    return None


class Bootstrap:
    def __init__(self, config, repo_id):
        self.config = config
        self.root = Path(config['brain_dir']).resolve()
        matches = [r for r in config['repositories'] if r['id'] == repo_id]
        if len(matches) != 1:
            brain.fail('Exactly one configured repository ID is required')
        self.repo = matches[0]
        self.home = self.root / '.state/bootstrap' / repo_id
        self.state_path = self.home / 'state.json'
        self.bare = self.home / 'snapshot.git'
        self.journal = self.root / '.state/bootstrap-publishing.json'

    def load(self):
        if not self.state_path.exists(): brain.fail('Run prepare first')
        return json.loads(self.state_path.read_text())

    def save(self, state):
        write_json(self.state_path, state)

    def editable(self, state):
        if (self.root/'.state/thoughts-publishing.json').exists(): brain.fail('Run thoughts recover first')
        if state['status'] == 'completed': brain.fail('This repo_id has already been initialized; use inbox updates')
        if state['status'] == 'blocked': brain.fail('Blocked: ' + state['blocker'] + '; wait for user, then unblock')
        if self.journal.exists(): brain.fail('Interrupted publication; run recover')

    def git(self, *args, retries=1):
        # The private bare repo avoids checkout filters, hooks and executing project code.
        env = dict(os.environ, GIT_TERMINAL_PROMPT='0')
        for attempt in range(retries):
            try:
                p = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '--git-dir', str(self.bare), *args],
                                   capture_output=True, timeout=180, env=env)
                if p.returncode == 0: return p.stdout
            except subprocess.TimeoutExpired:
                pass
            if attempt + 1 < retries: time.sleep(1 + attempt)
        raise RuntimeError('Git snapshot operation failed; check branch, network and access locally. No credentials logged.')

    def prepare(self, branch):
        if (self.root/'.state/thoughts-publishing.json').exists(): brain.fail('Run thoughts recover first')
        if self.state_path.exists():
            state = self.load(); self.editable(state)
            if state['branch'] != branch: brain.fail('Resume requires the originally selected branch')
        else:
            if self.journal.exists(): brain.fail('Recover the interrupted publication first')
            if not branch or branch.startswith('-'): brain.fail('Invalid branch')
            brain.run(['git', 'check-ref-format', 'refs/heads/' + branch])
            for other in (self.root / '.state/bootstrap').glob('*/state.json'):
                if json.loads(other.read_text())['status'] != 'completed':
                    brain.fail('Only one repository initialization may be in progress at a time')
            self.home.mkdir(parents=True, exist_ok=True)
            state = {'repo_id':self.repo['id'], 'branch':branch, 'commit':None,
                     'status':'preparing', 'created_at':stamp(), 'policy_version':POLICY_VERSION,
                     'files':[], 'chunks':[], 'workers':{}, 'reads':{}, 'results':{},
                     'draft':None, 'review':None, 'events':[]}
            self.save(state)
        try:
            if not self.bare.exists():
                brain.run(['git','-c','core.hooksPath=/dev/null','init','--bare',str(self.bare)])
            if not state['commit']:
                try:
                    commit = self.git('rev-parse','--verify','refs/bootstrap/snapshot^{commit}').decode().strip()
                except RuntimeError:
                    remote = brain.run(['git','-C',self.repo['path'],'remote','get-url',self.repo['remote']]).strip()
                    self.git('fetch','--no-tags','--depth=1',remote,'refs/heads/'+branch, retries=3)
                    commit = self.git('rev-parse','FETCH_HEAD^{commit}').decode().strip()
                    self.git('update-ref','refs/bootstrap/snapshot',commit)
                state['commit'] = commit
                self.save(state)  # pin before inventory; retries never fetch a newer branch
            if state['status'] == 'preparing':
                self.inventory(state)
                state['status'] = 'analyzing'
                self.save(state)
        except (ValueError, OSError, RuntimeError, subprocess.TimeoutExpired) as e:
            state['resume_status'] = state['status']; state['status'] = 'blocked'
            state['blocker'] = str(e); self.save(state); raise
        return self.status()

    def inventory(self, state):
        files, chunks = [], []
        listing = self.git('ls-tree','-r','-z','--full-tree',state['commit'])
        for row in listing.split(b'\0'):
            if not row: continue
            info, raw_path = row.split(b'\t',1)
            path = raw_path.decode('utf-8',errors='strict')
            mode, kind, oid = info.decode().split()
            entry = {'path':path,'oid':oid,'mode':mode,'status':'included','reason':None}
            why = exclusion(path)
            if why:
                entry.update(status='excluded',reason=why)
                files.append(entry); continue
            if kind != 'blob':
                entry.update(status='blocked',reason='Submodule is outside the selected repository snapshot')
                files.append(entry); continue
            data = self.git('cat-file','blob',oid)
            entry['sha256'] = sha(data)
            why = exclusion(path,data)
            if why:
                entry.update(status='excluded',reason=why); files.append(entry); continue
            try:
                text = data.decode('utf-8-sig')
                if '\0' in text: raise ValueError('NUL bytes')
            except (UnicodeDecodeError, ValueError):
                entry.update(status='blocked',reason='Non-UTF8/binary document requires an explicit text extraction, not silent exclusion')
                files.append(entry); continue
            if text.startswith('version https://git-lfs.github.com/spec/v1'):
                entry.update(status='blocked',reason='Git LFS pointer; actual document is not available in snapshot')
                files.append(entry); continue
            # Symlink blob text is its target; never dereference or leave the snapshot.
            entry['kind'] = 'symlink-target' if mode == '120000' else 'text'
            entry['line_count'] = len(text.splitlines()); entry['character_count'] = len(text)
            chunks.extend(units_for(path,oid,text))
            files.append(entry)
        state['files'], state['chunks'] = files,chunks
        state['manifest_hash'] = sha(canonical({'files':files,'chunks':chunks}).encode())

    def status(self):
        s = self.load()
        pending = [c for c in s['chunks'] if c['id'] not in s['results']]
        return {'repo_id':s['repo_id'],'branch':s['branch'],'commit':s['commit'],
                'status':s['status'],'blocker':s.get('blocker'),
                'max_parallel_agents':self.config.get('max_parallel_agents',4),
                'files':s['files'],'pending_chunks':pending,'completed_chunks':len(s['results']),
                'workers':s['workers'],'draft_hash':s.get('draft_hash'),
                'tasks':s.get('tasks',{}),
                'review':s['review'],'state_file':str(self.state_path)}

    def claim(self, worker, role):
        s=self.load(); self.editable(s); nonempty(worker,'worker')
        if role not in ('explorer','reviewer'): brain.fail('Invalid role')
        previous=s['workers'].get(worker)
        if previous and previous.get('retired'): brain.fail('Spawn a fresh agent for the next task')
        if any(t.get('worker')==worker and t['status']=='completed' for t in s.get('tasks',{}).values()):
            brain.fail('Completed task workers are retired; spawn a fresh agent')
        if previous and previous['role'] != role: brain.fail('Reviewer must be a different agent, never an explorer')
        if not previous or not previous['active']:
            if sum(w['active'] for w in s['workers'].values()) >= self.config.get('max_parallel_agents',4):
                brain.fail('Parallel agent limit reached; release a finished worker')
        s['workers'][worker]={'role':role,'active':True}; self.save(s)
        return {'worker':worker,'role':role}

    def worker(self,s,name,role=None):
        w=s['workers'].get(name)
        if not w or not w['active'] or (role and w['role']!=role): brain.fail('Claim an active worker of the required role first')
        return w

    def release(self, worker):
        s=self.load(); self.editable(s)
        self.worker(s,worker); s['workers'][worker]['active']=False
        for t in s.get('tasks',{}).values():
            if t.get('worker')==worker and t['status']=='running':
                t.setdefault('attempts',[]).append(worker)
                t['status']='pending'; t.pop('worker',None)
                s['workers'][worker]['retired']=True
        self.save(s)
        return {'released':worker}

    def read(self,worker,chunk):
        s=self.load(); self.editable(s); self.worker(s,worker)
        candidates=[c for c in s['chunks'] if c['id']==chunk]
        if not candidates: brain.fail('Unknown chunk')
        c=candidates[0]
        text=self.source_text(s,c)
        piece=text[c['start']:c['end']]
        if sha(piece.encode())!=c['sha256']: brain.fail('Snapshot range integrity failure')
        receipt=secrets.token_hex(16)
        s['reads'].setdefault(worker,{})[chunk]=receipt; self.save(s)
        return dict(c,content=piece,receipt=receipt,worker=worker,commit=s['commit'])

    def source_text(self,s,chunk):
        f=next(f for f in s['files'] if f['path']==chunk['path'])
        if f.get('extraction'):
            p=self.home/'extractions'/f['extraction']['file']
            data=p.read_bytes()
            if sha(data)!=f['extraction']['sha256']: brain.fail('Extracted text was modified')
            return data.decode('utf-8')
        return self.git('cat-file','blob',chunk['oid']).decode('utf-8-sig')

    def refresh_manifest(self,s):
        s['manifest_hash']=sha(canonical({'files':s['files'],'chunks':s['chunks']}).encode())
        s['draft']=None; s['review']=None; s.pop('draft_hash',None)
        for task in s.get('tasks',{}).values():
            if task['status']=='completed':
                task['status']='pending'; task.pop('worker',None); task.pop('result',None)

    def split(self,chunk,size):
        s=self.load(); self.editable(s)
        if size<1: brain.fail('size must be positive')
        matches=[c for c in s['chunks'] if c['id']==chunk]
        if not matches or chunk in s['results']: brain.fail('Only a pending chunk can be split')
        c=matches[0]
        if size>=c['end']-c['start']: brain.fail('Split size must be smaller than the chunk')
        text=self.source_text(s,c)
        children=units_for(c['path'],c['oid'],text,size,c['start'],c['end'])
        s['chunks']=[x for x in s['chunks'] if x['id']!=chunk]+children
        for reads in s['reads'].values(): reads.pop(chunk,None)
        self.refresh_manifest(s); self.save(s)
        return {'replaced_chunk':chunk,'new_chunks':children}

    def extract(self,path,text_file,method):
        s=self.load(); self.editable(s); nonempty(method,'extraction method')
        matches=[f for f in s['files'] if f['path']==path]
        if not matches or matches[0]['status']!='blocked' or 'Non-UTF8/binary' not in matches[0]['reason']:
            brain.fail('Extraction is only for blocked documents in this snapshot')
        text=Path(text_file).read_text(encoding='utf-8')
        if '\0' in text or not text.strip(): brain.fail('Provide nonempty UTF-8 extracted document content')
        f=matches[0]; filename=sha(path.encode())+'.txt'
        brain.atomic(self.home/'extractions'/filename,text)
        f.update(status='included',reason=None,kind='extracted-document',line_count=len(text.splitlines()),character_count=len(text),
                 extraction={'file':filename,'sha256':sha(text.encode()),'method':method,'source_sha256':f['sha256']})
        s['chunks'].extend(units_for(path,f['oid'],text))
        self.refresh_manifest(s); self.save(s)
        return {'extracted':path,'method':method,'source_sha256':f['sha256']}

    def submit(self,worker,result):
        s=self.load(); self.editable(s); self.worker(s,worker,'explorer')
        if not s.get('analysis_plan'): brain.fail('Run organize with a functional area plan before submitting analysis')
        chunk=result.get('chunk_id')
        if chunk not in {c['id'] for c in s['chunks']}: brain.fail('Unknown chunk')
        if not result.get('receipt') or s['reads'].get(worker,{}).get(chunk)!=result['receipt']:
            brain.fail('A matching read receipt is required before submission')
        findings=result.get('findings',[])
        if not isinstance(findings,list): brain.fail('findings must be a list')
        for f in findings:
            if f.get('kind') not in ('domain','technical','database','integration','architecture','documentation'):
                brain.fail('Unknown finding kind')
            nonempty(f.get('text'),'finding text')
        if not findings: nonempty(result.get('no_knowledge_reason'),'no_knowledge_reason')
        previous=s['results'].get(chunk)
        if previous:
            # Shared dependencies appear in multiple entry-point flows. Preserve old IDs;
            # append new observations rather than requiring a retired agent to return.
            combined=list(previous.get('findings',[]))
            for finding in findings:
                if finding not in combined: combined.append(finding)
            result=dict(result,findings=combined)
        s['results'][chunk]=dict(result,worker=worker)
        s['draft']=None; s['review']=None; s.pop('draft_hash',None)
        self.save(s); return {'recorded':chunk}

    def coverage(self,s):
        if not s['chunks']: brain.fail('No included source chunks; block and ask the user')
        blockers=[f['path']+': '+f['reason'] for f in s['files'] if f['status']=='blocked']
        missing=[c['id'] for c in s['chunks'] if c['id'] not in s['results']]
        if blockers or missing: brain.fail('Coverage incomplete: '+canonical({'blocked':blockers,'missing_chunks':missing}))
        for f in s['files']:
            if f['status']!='included': continue
            units=sorted((c for c in s['chunks'] if c['path']==f['path']),key=lambda c:c['start'])
            position=0
            for c in units:
                if c['start']!=position: brain.fail('Gap in file ranges: '+f['path'])
                position=c['end']
            if position!=f['character_count'] or not units: brain.fail('Incomplete file ranges')

    def evidence(self,s,items):
        if not isinstance(items,list) or not items: brain.fail('Evidence chunk IDs are required')
        if any(x not in s['results'] for x in items): brain.fail('Evidence references unprocessed chunks')

    def document_checks(self,s,plan):
        docs=plan.get('documents')
        if not isinstance(docs,list) or not docs: brain.fail('Draft requires documents')
        paths=set()
        for d in docs:
            p=brain.safe(self.root,d['path']); rel=p.relative_to(self.root)
            if rel.parts[0] not in ('knowledge','architecture') or p.suffix!='.md': brain.fail('Only knowledge/architecture Markdown outputs allowed')
            if rel.as_posix()!=d['path'] or d['path'] in paths: brain.fail('Duplicate/noncanonical document path')
            paths.add(d['path']); nonempty(d.get('content'),'document content')
            if '/.state/' in d['content']: brain.fail('Keep internal checkpoint links out of documentation')
            if p.exists():
                if sha(p.read_bytes())!=d.get('expected_sha256'): brain.fail('Reread changed existing document: '+d['path'])
            if rel.parts[0]=='architecture':
                m,_=brain.split_note(d['content'])
                if not p.exists() and m.get('status')!='proposed': brain.fail('New ADR must be proposed')
            # Every published statement document is tied to real analysis, internally.
            self.evidence(s,d.get('evidence_chunks'))
            if d.get('kind')=='database' and not rel.as_posix().startswith('knowledge/technical/'+s['repo_id']+'/database/'):
                brain.fail('Database documentation must use this repo database directory')
        if 'knowledge/essence.md' not in paths: brain.fail('Update the knowledge guide alongside initial documentation')
        if any(any(f['kind']=='database' for f in r.get('findings',[])) for r in s['results'].values()):
            if not any(d.get('kind')=='database' for d in docs): brain.fail('Database findings require separate database documentation')
        included={f['path'] for f in s['files'] if f['status']=='included'}
        summaries=plan.get('file_summaries',[])
        if len(summaries)!=len(included) or {x.get('path') for x in summaries}!=included:
            brain.fail('Exactly one consolidated summary per included file is required')
        for f in summaries:
            nonempty(f.get('summary'),'file summary')
            outputs=f.get('document_paths',[])
            if not outputs: nonempty(f.get('no_knowledge_reason'),'file no_knowledge_reason')
            if any(p not in paths for p in outputs): brain.fail('Unknown summary output document')
        dimensions=plan.get('dimensions',{})
        if set(dimensions)!=set(DIMENSIONS): brain.fail('All synthesis dimensions must be assessed')
        for d in dimensions.values():
            nonempty(d.get('assessment'),'dimension assessment'); self.evidence(s,d.get('evidence_chunks'))
        if not plan.get('flows'):
            nonempty(plan.get('no_flows_reason'),'no_flows_reason')
        flow_ids=set()
        for f in plan.get('flows',[]):
            nonempty(f.get('id'),'flow id'); nonempty(f.get('description'),'flow description')
            if f['id'] in flow_ids: brain.fail('Duplicate flow ID')
            flow_ids.add(f['id']); self.evidence(s,f.get('evidence_chunks'))
            if not isinstance(f.get('stages'),list) or not f['stages']: brain.fail('Flow stages required')
            for stage in f['stages']: nonempty(stage,'flow stage')
        self.depth_checks(s,plan,flow_ids)
        future={brain.safe(self.root,p) for p in paths}|{self.root/'index.md'}
        for d in docs:
            p=brain.safe(self.root,d['path'])
            for t in brain.targets(p,d['content']):
                if not t.is_relative_to(self.root) or t.is_relative_to(self.root/'.state') or (not t.exists() and t not in future):
                    brain.fail('Broken/outside proposed link: '+str(t))

    def findings(self,s):
        return {chunk+':'+str(i):dict(f,chunk_id=chunk)
                for chunk,r in s['results'].items() for i,f in enumerate(r.get('findings',[]))}

    def organize(self,plan):
        s=self.load(); self.editable(s)
        areas=plan.get('areas',[]); assigned=[]; ids=set()
        included={f['path'] for f in s['files'] if f['status']=='included'}
        if not areas: brain.fail('Plan requires cohesive functional areas')
        for a in areas:
            nonempty(a.get('id'),'area id')
            if a['id'] in ids: brain.fail('Duplicate planned area')
            ids.add(a['id'])
            for key in ('purpose','domain_questions','technical_questions'):
                nonempty(a.get(key),key)
            if not a.get('files') or not set(a['files'])<=included: brain.fail('Invalid area files')
            assigned.extend(a['files'])
        if set(assigned)!=included or len(assigned)!=len(included):
            brain.fail('Assign each included file one primary area; dependencies may be read across areas')
        nonempty(plan.get('cross_area_strategy'),'cross_area_strategy')
        tasks=plan.get('tasks',[])
        if not tasks: brain.fail('Entry-point flow and residual task queue required')
        queue={}; task_files=set()
        for t in tasks:
            nonempty(t.get('id'),'task id')
            if t['id'] in queue: brain.fail('Duplicate task id')
            if not t.get('files') or not set(t['files'])<=included: brain.fail('Task requires included files')
            task_files.update(t['files'])
            if t.get('kind')=='flow':
                ep=t.get('entry_point',{})
                if ep.get('path') not in t['files']: brain.fail('Entry point path must belong to task files')
                for key in ('symbol','trigger'): nonempty(ep.get(key),'entry point '+key)
            elif t.get('kind')=='residual': nonempty(t.get('reason'),'residual task reason')
            else: brain.fail('Task kind must be flow or residual')
            old=s.get('tasks',{}).get(t['id'])
            if old and old['spec']==t: queue[t['id']]=old
            else:
                if old and old['status']=='running': brain.fail('Release running task before changing its specification')
                queue[t['id']]={'spec':t,'status':'pending'}
        if task_files!=included: brain.fail('Flow and residual tasks together must cover all included files')
        if any(t['status']=='running' and k not in queue for k,t in s.get('tasks',{}).items()):
            brain.fail('Cannot remove running task')
        s['tasks']=queue
        s['analysis_plan']=plan; s['draft']=None; s['review']=None; s.pop('draft_hash',None)
        self.save(s)
        return {'areas':len(areas),'assigned_files':len(assigned),'tasks':len(queue)}

    def task_start(self,task,worker):
        s=self.load(); self.editable(s); self.worker(s,worker,'explorer')
        t=s.get('tasks',{}).get(task)
        if not t or t['status']!='pending': brain.fail('Select a pending task')
        if any(x.get('worker')==worker for x in s['tasks'].values()):
            brain.fail('Use a fresh worker identity for each task')
        t.update(status='running',worker=worker)
        self.save(s); return t

    def task_finish(self,task,worker,result):
        s=self.load(); self.editable(s); self.worker(s,worker,'explorer')
        t=s.get('tasks',{}).get(task)
        if not t or t['status']!='running' or t.get('worker')!=worker: brain.fail('Task is not owned by this active worker')
        nonempty(result.get('summary'),'task summary')
        self.evidence(s,result.get('evidence_chunks'))
        if not set(result['evidence_chunks'])<=set(s['reads'].get(worker,{})):
            brain.fail('Task evidence must be read by its own worker')
        required={c['id'] for c in s['chunks'] if c['path'] in t['spec']['files']}
        if not required<=set(result['evidence_chunks']): brain.fail('Task must account for all ranges of its assigned files')
        if t['spec']['kind']=='flow': nonempty(result.get('flow_id'),'flow_id')
        t.update(status='completed',result=result)
        s['workers'][worker]['active']=False
        s['workers'][worker]['retired']=True
        s['draft']=None; s['review']=None; s.pop('draft_hash',None)
        self.save(s)
        return {'completed':task,'retired_worker':worker,'action':'End actual subagent; spawn fresh worker for next pending task'}

    def depth_checks(self,s,plan,flow_ids):
        tasks=s.get('tasks',{})
        if not tasks or any(t['status']!='completed' for t in tasks.values()): brain.fail('Finish all queued exploration tasks before staging')
        for t in tasks.values():
            if t['spec']['kind']=='flow' and t['result']['flow_id'] not in flow_ids:
                brain.fail('A completed entry-point task is missing its published flow')
            if t['spec']['kind']=='flow':
                flow=next(f for f in plan['flows'] if f['id']==t['result']['flow_id'])
                if not set(t['result']['evidence_chunks'])<=set(flow['evidence_chunks']):
                    brain.fail('Published flow loses evidence from its entry-point task')
        docs={d['path']:d for d in plan['documents']}
        findings=self.findings(s)
        dispositions=plan.get('finding_dispositions',[])
        if len(dispositions)!=len(findings) or {d.get('finding_id') for d in dispositions}!=set(findings):
            brain.fail('Account for every finding in finding_dispositions; run findings for stable IDs')
        disposition_by_id={d['finding_id']:d for d in dispositions}
        for item in dispositions:
            f=findings[item['finding_id']]
            if item.get('disposition')=='documented':
                path=item.get('document_path'); excerpt=item.get('excerpt')
                nonempty(excerpt,'documented excerpt')
                if path not in docs or path=='knowledge/essence.md' or excerpt not in docs[path]['content']:
                    brain.fail('Finding must map to an exact excerpt in a detailed document, not the guide')
                if f['chunk_id'] not in docs[path]['evidence_chunks']: brain.fail('Document lacks finding evidence')
                if f['kind']=='domain' and not path.startswith('knowledge/domain/'):
                    brain.fail('Domain findings require domain documentation')
                if f['kind'] in ('technical','database','integration','architecture') and path.startswith('knowledge/domain/'):
                    brain.fail('Implementation findings belong in technical/architecture documentation, not domain prose')
                if f['kind']=='database' and docs[path].get('kind')!='database':
                    brain.fail('Database findings require a database document')
            elif item.get('disposition') in ('duplicate','superseded'):
                target=item.get('duplicate_of') if item['disposition']=='duplicate' else item.get('replaced_by')
                canonical_item=disposition_by_id.get(target,{})
                if target==item['finding_id'] or canonical_item.get('disposition')!='documented':
                    brain.fail('Duplicate/correction must point directly to a documented finding')
                nonempty(item.get('reason'),'duplicate/correction explanation')
            elif item.get('disposition')=='omitted':
                if f['kind']!='documentation': brain.fail('Behavioral/technical findings cannot be silently omitted')
                nonempty(item.get('reason'),'documentation-only omission explanation')
            else: brain.fail('Invalid finding disposition')
        dossiers=plan.get('area_dossiers',[])
        if not dossiers: brain.fail('Functional area dossiers are required')
        planned={a['id']:a for a in s.get('analysis_plan',{}).get('areas',[])}
        if {a.get('id') for a in dossiers}!=set(planned): brain.fail('Dossiers must match the recorded analysis plan')
        included={f['path'] for f in s['files'] if f['status']=='included'}
        covered=set(); ids=set()
        for a in dossiers:
            nonempty(a.get('id'),'area id')
            if a['id'] in ids: brain.fail('Duplicate area')
            ids.add(a['id'])
            files=a.get('files',[])
            if not files or not set(files)<=included: brain.fail('Area requires included file paths')
            if set(files)!=set(planned[a['id']]['files']): brain.fail('Dossier files differ from planned primary ownership')
            covered.update(files); self.evidence(s,a.get('evidence_chunks'))
            chunk_files={c['path'] for c in s['chunks'] if c['id'] in a['evidence_chunks']}
            if not set(files)<=chunk_files: brain.fail('Each area file requires evidence')
            for key in ('domain_assessment','technical_assessment','exceptions_and_unknowns'):
                nonempty(a.get(key),key)
            if not set(a.get('flow_ids',[]))<=flow_ids: brain.fail('Unknown area flow')
            if not a.get('flow_ids'): nonempty(a.get('no_flows_reason'),'area no_flows_reason')
        if covered!=included: brain.fail('Area dossiers omit included files')

    def stage(self,plan):
        s=self.load(); self.editable(s); self.coverage(s)
        self.document_checks(s,plan)
        s['draft']=plan
        s['draft_hash']=sha(canonical({'plan':plan,'results':s['results'],'manifest_hash':s['manifest_hash']}).encode())
        s['review']=None
        s['baseline']={str(p.relative_to(self.root)):sha(p.read_bytes()) for p in brain.active(self.root)}
        self.save(s)
        return {'draft_hash':s['draft_hash'],'documents':len(plan['documents']),'review_required':True}

    def review(self,worker,result):
        s=self.load(); self.editable(s); self.worker(s,worker,'reviewer'); self.coverage(s)
        if not s['draft'] or result.get('draft_hash')!=s.get('draft_hash'): brain.fail('Review must match the current draft')
        if not s['reads'].get(worker): brain.fail('Reviewer must independently inspect snapshot chunks')
        if result.get('verdict') not in ('approved','changes_requested'): brain.fail('Invalid review verdict')
        if set(result.get('checks',{}))!=set(CHECKS): brain.fail('All review dimensions are required')
        for check in result['checks'].values(): nonempty(check,'review evidence')
        issues=result.get('issues')
        if not isinstance(issues,list): brain.fail('issues must be a list')
        if result['verdict']=='approved' and issues: brain.fail('Open issues prohibit approval')
        if result['verdict']=='approved':
            read_ids=set(s['reads'].get(worker,{}))
            reviewed_files={c['path'] for c in s['chunks'] if c['id'] in read_ids}
            included={f['path'] for f in s['files'] if f['status']=='included'}
            if reviewed_files!=included: brain.fail('Reviewer must inspect every included file; sample chunks plus all relevant flow ranges')
            checks=result.get('document_checks',{})
            if set(checks)!={d['path'] for d in s['draft']['documents']}:
                brain.fail('Independent substantive check required for every document')
            for check in checks.values(): nonempty(check,'document review')
        if result['verdict']=='changes_requested' and not issues: brain.fail('List the requested corrections')
        s['review']=dict(result,worker=worker,reviewed_at=stamp()); self.save(s)
        return {'verdict':result['verdict']}

    def block(self,reason):
        s=self.load(); self.editable(s); nonempty(reason,'reason')
        s['resume_status']=s['status']; s['status']='blocked'; s['blocker']=reason
        s['events'].append({'event':'blocked','reason':reason,'at':stamp()}); self.save(s)
        return {'blocked':reason,'action':'Ask user; do not retry until they respond'}

    def unblock(self):
        s=self.load()
        if s['status']!='blocked': brain.fail('Not blocked')
        s['status']=s.pop('resume_status','analyzing'); s.pop('blocker',None)
        s['events'].append({'event':'user-unblocked','at':stamp()}); self.save(s)
        return {'status':s['status'],'commit':s['commit']}

    def recover(self):
        if not self.journal.exists(): return {'recovered':False}
        journal=json.loads(self.journal.read_text())
        if journal['repo_id']!=self.repo['id']: brain.fail('Recover the repository identified in the journal')
        s=self.load()
        if s['status']=='completed' and s.get('published_draft_hash')==journal['draft_hash']:
            self.journal.unlink(); return {'recovered':True,'already_completed':True}
        for name,backup in journal['files'].items():
            p=brain.safe(self.root,name)
            current=sha(p.read_bytes()) if p.exists() else None
            allowed=journal.get('allowed_hashes',{}).get(name,[])
            original=sha(backup.encode()) if backup is not None else None
            if current not in [original,*allowed]:
                brain.fail('Recovery blocked by an external edit: '+name+'; preserve it and ask the user before recovery')
        for name,backup in journal['files'].items():
            p=brain.safe(self.root,name)
            if backup is None:
                if p.exists(): p.unlink()
            else:
                brain.atomic(p,backup)
        self.journal.unlink()
        return {'recovered':True,'status':'draft retained; publication rolled back'}

    def publish(self):
        s=self.load(); self.editable(s); self.coverage(s)
        review=s.get('review') or {}
        if not s.get('draft') or review.get('verdict')!='approved' or review.get('draft_hash')!=s.get('draft_hash'):
            brain.fail('An independent approved review of the exact draft is required')
        # All files remain unpublished until every coverage/review gate has passed.
        self.document_checks(s,s['draft'])
        baseline={str(p.relative_to(self.root)):sha(p.read_bytes()) for p in brain.active(self.root)}
        if baseline!=s['baseline']: brain.fail('Knowledge changed since staging; restage and review again')
        targets=set(brain.active(self.root))|{self.root/'index.md'}|{brain.safe(self.root,d['path']) for d in s['draft']['documents']}
        backups={str(p.relative_to(self.root)):p.read_bytes().decode('utf-8') if p.exists() else None for p in targets}
        journal={'repo_id':s['repo_id'],'draft_hash':s['draft_hash'],'files':backups,'allowed_hashes':{}}
        write_json(self.journal,journal)
        def tracked_write(path,content):
            name=str(path.relative_to(self.root))
            journal['allowed_hashes'].setdefault(name,[]).append(sha(content.encode()))
            write_json(self.journal,journal)
            brain.atomic(path,content)
        try:
            for d in s['draft']['documents']: tracked_write(brain.safe(self.root,d['path']),d['content'])
            brain.graph(self.root,writer=tracked_write); brain.validate(self.root)
            s['status']='completed'; s['completed_at']=stamp(); s['published_draft_hash']=s['draft_hash']
            self.save(s)
        except Exception:
            # Ordinary errors roll back; a process kill leaves the journal for recover.
            self.recover(); raise
        self.journal.unlink()
        return {'completed':s['repo_id'],'commit':s['commit'],'documents':[d['path'] for d in s['draft']['documents']]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--config',default=str(Path.home()/'.config/second-brain/config.yaml'))
    p.add_argument('--repo',required=True)
    sub=p.add_subparsers(dest='command',required=True)
    cmd=sub.add_parser('prepare'); cmd.add_argument('--branch',required=True)
    sub.add_parser('status'); sub.add_parser('findings')
    cmd=sub.add_parser('organize'); cmd.add_argument('--plan',required=True)
    sub.add_parser('tasks')
    for name in ('task-start','task-finish'):
        cmd=sub.add_parser(name); cmd.add_argument('--task',required=True); cmd.add_argument('--worker',required=True)
        if name=='task-finish': cmd.add_argument('--result',required=True)
    cmd=sub.add_parser('claim'); cmd.add_argument('--worker',required=True); cmd.add_argument('--role',choices=['explorer','reviewer'],required=True)
    cmd=sub.add_parser('read'); cmd.add_argument('--worker',required=True); cmd.add_argument('--chunk',required=True)
    cmd=sub.add_parser('submit'); cmd.add_argument('--worker',required=True); cmd.add_argument('--result',required=True)
    cmd=sub.add_parser('split'); cmd.add_argument('--chunk',required=True); cmd.add_argument('--size',required=True,type=int)
    cmd=sub.add_parser('extract'); cmd.add_argument('--path',required=True); cmd.add_argument('--text-file',required=True); cmd.add_argument('--method',required=True)
    cmd=sub.add_parser('release'); cmd.add_argument('--worker',required=True)
    cmd=sub.add_parser('stage'); cmd.add_argument('--plan',required=True)
    cmd=sub.add_parser('review'); cmd.add_argument('--worker',required=True); cmd.add_argument('--result',required=True)
    cmd=sub.add_parser('block'); cmd.add_argument('--reason',required=True)
    sub.add_parser('unblock'); sub.add_parser('publish'); sub.add_parser('recover')
    a=p.parse_args(); c=brain.config(a.config); boot=Bootstrap(c,a.repo)
    with brain.lock(boot.root):
        if a.command=='prepare': result=boot.prepare(a.branch)
        elif a.command=='organize': result=boot.organize(json.loads(Path(a.plan).read_text()))
        elif a.command=='tasks': result=boot.load().get('tasks',{})
        elif a.command=='task-start': result=boot.task_start(a.task,a.worker)
        elif a.command=='task-finish': result=boot.task_finish(a.task,a.worker,json.loads(Path(a.result).read_text()))
        elif a.command=='findings': result=boot.findings(boot.load())
        elif a.command=='claim': result=boot.claim(a.worker,a.role)
        elif a.command=='read': result=boot.read(a.worker,a.chunk)
        elif a.command=='submit': result=boot.submit(a.worker,json.loads(Path(a.result).read_text()))
        elif a.command=='split': result=boot.split(a.chunk,a.size)
        elif a.command=='extract': result=boot.extract(a.path,a.text_file,a.method)
        elif a.command=='release': result=boot.release(a.worker)
        elif a.command=='stage': result=boot.stage(json.loads(Path(a.plan).read_text()))
        elif a.command=='review': result=boot.review(a.worker,json.loads(Path(a.result).read_text()))
        elif a.command=='block': result=boot.block(a.reason)
        else: result=getattr(boot,a.command)()
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    try: main()
    except (ValueError, KeyError, OSError, RuntimeError, subprocess.TimeoutExpired) as e:
        raise SystemExit('ERROR: '+str(e))
