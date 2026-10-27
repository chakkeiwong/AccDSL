"""Bound ordered author regression; rendering never supplies a reading judgment."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import fitz

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
NEXT=ROOT/'docs/design/proposal/manuscript-readability-20261017'
READ=OUT/'regression'
LEDGER=READ/'ledger.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')

def init():
    assert not READ.exists()
    checks=json.loads((OUT/'candidate-checks.json').read_text())
    assert checks['failures']==0
    pdf=ROOT/checks['pdf'];assert sha(pdf)==checks['pdf_sha256']
    READ.mkdir();(READ/'rendered').mkdir();(READ/'segments').mkdir()
    spec=importlib.util.spec_from_file_location('inv',ROOT/'data/accounting-master/continuous-reading-20261017/reading_inventory.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.BASE=NEXT;m.PDF=pdf;m.EXPECTED=checks['pdf_sha256'];m.OUT=READ;m.LEDGER=READ/'structure.json'
    m.initialize()
    structure=json.loads(m.LEDGER.read_text());structure['nodes'][0]['title']='AccDSL Version3.42'
    structure['baseline_diagnosis']=dict(path='data/accounting-master/continuous-reading-20261017/structure-ledger.json',sha256=sha(ROOT/'data/accounting-master/continuous-reading-20261017/structure-ledger.json'))
    save(m.LEDGER,structure)
    chapters=[]
    b=[x for x in checks['bookmarks'] if x[0]==1]
    for i,row in enumerate(b):
        end=b[i+1][2]-1 if i+1<len(b) else 381
        chapters.append(dict(index=i+1,title=row[1],pages=[row[2],end],status='pending',judgment=None))
    save(LEDGER,dict(candidate_pdf=checks['pdf'],pdf_sha256=checks['pdf_sha256'],page_count=checks['pages'],
        baseline_diagnosis=structure['baseline_diagnosis'],sources=checks['source_hashes'],
        rendered={},segments=[],chapter_regressions=chapters,cumulative_regressions=[],
        document_regression=None,defect_dispositions={f'R07-D{i:03}':'implemented; final regression pending' for i in range(1,8)},
        status='author_regression_in_progress',independent_reader='pending',human_acceptance='pending'))
    print('Initialized successor regression; all reading judgments remain pending.')

def render(start,end):
    d=json.loads(LEDGER.read_text());pdf=ROOT/d['candidate_pdf'];assert sha(pdf)==d['pdf_sha256']
    assert 1<=start<=end<=d['page_count'] and end-start<6
    with fitz.open(pdf) as doc:
        for p in range(start,end+1):
            key=str(p);target=READ/'rendered'/f'page-{p:03}.png'
            if key in d['rendered']:
                assert sha(target)==d['rendered'][key]['sha256'];continue
            assert not target.exists()
            doc[p-1].get_pixmap(matrix=fitz.Matrix(110/72,110/72),alpha=False).save(target)
            d['rendered'][key]=dict(path=str(target.relative_to(ROOT)),sha256=sha(target))
    save(LEDGER,d);print(f'Rendered{start}–{end}; no reading inferred.')

def record(path):
    d=json.loads(LEDGER.read_text());p=ROOT/path;s=json.loads(p.read_text())
    first,last=s['pages'];assert last-first<6
    previous=json.loads((ROOT/d['segments'][-1]['path']).read_text()) if d['segments'] else None
    assert first==(previous['pages'][1]+1 if previous else 1)
    if previous:assert s['entry_state']==previous['exit_state']
    assert s['exit_state'].strip() and s['findings']
    assert all(str(i) in d['rendered'] for i in range(first,last+1))
    structure_path=READ/'structure.json';structure=json.loads(structure_path.read_text())
    nodes={n['id']:n for n in structure['nodes']}
    for node_id,judgment in s.get('node_judgments',{}).items():
        assert node_id in nodes and judgment['physical_pages'][1]<=last
        nodes[node_id].update(judgment=judgment,physical_pages=judgment['physical_pages'],reading_status='author_read')
        if nodes[node_id]['kind']=='equation':nodes[node_id]['exposition_role']=judgment['equation']['exposition_role']
    for page in range(first,last+1):
        structure['pages'][page-1]['reading_status']='author_read'
        structure['pages'][page-1]['render']=dict(d['rendered'][str(page)],dpi=110)
    for chapter in s.get('chapter_regressions',[]):
        row=d['chapter_regressions'][chapter['index']-1]
        assert row['pages'][1]<=last and row['status']=='pending'
        row.update(status='author_regressed',judgment=chapter['judgment'],segment=str(p.relative_to(ROOT)))
    for cumulative in s.get('cumulative_regressions',[]):
        assert cumulative['through_chapter']%2==0
        assert all(x['status']=='author_regressed' for x in d['chapter_regressions'][:cumulative['through_chapter']])
        d['cumulative_regressions'].append(dict(cumulative,segment=str(p.relative_to(ROOT))))
    structure['ordered_segments'].append(str(p.relative_to(ROOT)))
    structure.setdefault('segment_sha256',{})[str(p.relative_to(ROOT))]=sha(p)
    d['segments'].append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p)))
    if 'document_regression' in s:
        d['document_regression']=dict(judgment=s['document_regression'],segment=str(p.relative_to(ROOT)))
    d['defect_dispositions'].update(s.get('defect_dispositions',{}))
    segments={r['path']:json.loads((ROOT/r['path']).read_text()) for r in d['segments']}
    check_records(d,structure,segments)
    save(structure_path,structure)
    save(LEDGER,d);print(f'Recorded ordered successor reading through{last}; acceptance pending.')

REQUIRED_JUDGMENT = ('entry_belief','open_question','parent_contribution',
    'belief_update','exit_question','removal_verdict','swap_verdict',
    'entry_verdict','exit_verdict','promise_verdict','distinct_contribution_verdict')
EQUATION_FIELDS = ('exposition_role','symbols_units_domain','assumptions_timing',
    'source_and_equality','interpretation','transition')
LATER_EQUATION_FIELDS = ('exposition_role','role','symbols_and_units',
    'assumptions_and_domain','derivation_and_status','interpretation_and_transition',
    'source_and_code_boundary')

def check_records(d, structure, segments, complete=False):
    """Check bound reading records; successful partial validation is not closure."""
    nodes={n['id']:n for n in structure['nodes']}
    assert len(nodes)==len(structure['nodes']), 'Duplicate structural node'
    assert d['page_count']==structure['page_count']==len(structure['pages'])
    assert d['pdf_sha256']==structure['pdf_sha256'], 'Candidate identity mismatch'
    paths=[row['path'] for row in d['segments']]
    assert len(paths)==len(set(paths)), 'Duplicate segment'
    assert paths==structure['ordered_segments']==list(segments), 'Segment inventories differ'
    assert structure['segment_sha256']=={r['path']:r['sha256'] for r in d['segments']}
    authored={}; chapter_rows={}; prefixes=[]; document=None; defects={}
    previous=0; exit_state=None
    for path,s in segments.items():
        a,b=s['pages'];assert a==previous+1 and a<=b<a+6 and b<=d['page_count']
        if previous:assert s['entry_state']==exit_state, 'Reading continuity broken'
        assert isinstance(s.get('findings'),list) and s['findings']
        assert all(isinstance(x,str) and x.strip() for x in s['findings'])
        assert isinstance(s.get('exit_state'),str) and s['exit_state'].strip()
        for key,j in s.get('node_judgments',{}).items():
            assert key in nodes and key not in authored, ('Unknown/repeated judgment',key)
            assert 1<=j['physical_pages'][0]<=j['physical_pages'][1]<=b, ('Unread unit',key)
            authored[key]=j
        for row in s.get('chapter_regressions',[]):
            i=row['index'];assert 1<=i<=len(d['chapter_regressions']) and i not in chapter_rows
            assert d['chapter_regressions'][i-1]['pages'][1]<=b, 'Unread chapter'
            assert all(k in chapter_rows for k in range(1,i)), 'Chapter order broken'
            assert isinstance(row['judgment'],str) and row['judgment'].strip()
            chapter_rows[i]=dict(row,segment=path)
        for row in s.get('cumulative_regressions',[]):
            i=row['through_chapter'];assert i in range(2,17,2)
            assert all(k in chapter_rows for k in range(1,i+1)), 'Unread cumulative prefix'
            assert isinstance(row.get('judgment'),str) and row['judgment'].strip()
            prefixes.append(dict(row,segment=path))
        if 'document_regression' in s:
            assert b==d['page_count'] and document is None, 'Premature/repeated document review'
            assert isinstance(s['document_regression'],str) and s['document_regression'].strip()
            document=dict(judgment=s['document_regression'],segment=path)
        if 'defect_dispositions' in s:
            assert b==d['page_count'], 'Premature final defect disposition'
            defects.update(s['defect_dispositions'])
        previous=b;exit_state=s['exit_state']
    texts={}
    for key,node in nodes.items():
        parent=node['parent'];assert parent is None or parent in nodes, ('Missing parent',key)
        visited={key};ancestor=parent
        while ancestor is not None:
            assert ancestor not in visited, ('Hierarchy cycle',key)
            visited.add(ancestor);ancestor=nodes[ancestor]['parent']
        j=node.get('judgment')
        if j is None:
            assert node['reading_status']=='pending' and key not in authored
            continue
        assert node['reading_status']=='author_read' and authored.get(key)==j, ('Unbound judgment',key)
        assert j['physical_pages']==node['physical_pages']
        for field in REQUIRED_JUDGMENT:
            value=j.get(field);assert isinstance(value,str) and value.strip(), (key,field)
            texts.setdefault(value.strip(),set()).add(key)
        if node['kind']=='equation':
            eq=j.get('equation',{});fields=LATER_EQUATION_FIELDS if 'symbols_and_units' in eq else EQUATION_FIELDS
            for field in fields:assert isinstance(eq.get(field),str) and eq[field].strip(), (key,field)
            assert node['exposition_role']==eq['exposition_role']
        if parent and nodes[parent].get('judgment'):
            lo,hi=nodes[parent]['physical_pages'];a,b=node['physical_pages']
            assert lo<=a<=b<=hi, ('Page containment',key)
    assert not any(len(ids)>2 for ids in texts.values()), 'Repeated judgment across unrelated units'
    for i,page in enumerate(structure['pages'],1):
        assert page['page']==i
        assert page['reading_status']==('author_read' if i<=previous else 'pending')
        if i<=previous:
            assert page['render']['path']==d['rendered'][str(i)]['path']
            assert page['render']['sha256']==d['rendered'][str(i)]['sha256']
    for i,row in enumerate(d['chapter_regressions'],1):
        assert row['index']==i
        if i in chapter_rows:
            binding=chapter_rows[i]
            assert row['status']=='author_regressed' and row['judgment']==binding['judgment']
            assert row['segment']==binding['segment']
        else:assert row['status']=='pending' and row['judgment'] is None
    assert prefixes==d['cumulative_regressions'], 'Unbound cumulative judgment'
    ends=[r['through_chapter'] for r in prefixes]
    assert ends==sorted(set(ends)), 'Repeated/out-of-order cumulative judgment'
    assert document==d['document_regression'], 'Unbound document judgment'
    assert set(d['defect_dispositions'])=={f'R07-D{i:03}' for i in range(1,8)}
    for key,value in d['defect_dispositions'].items():
        assert value==defects.get(key,'implemented; final regression pending'), 'Unbound defect disposition'
    for obj in (d,structure):assert obj['independent_reader']==obj['human_acceptance']=='pending'
    if complete:
        assert previous==d['page_count'], 'Unread pages remain'
        assert len(authored)==len(nodes), 'Missing structural judgments'
        assert len(chapter_rows)==len(d['chapter_regressions']), 'Missing chapter judgments'
        assert ends==list(range(2,17,2)), 'Missing cumulative prefixes'
        assert document is not None, 'Missing whole-document judgment'
        assert set(defects)==set(d['defect_dispositions']), 'Missing final defect dispositions'
        for value in defects.values():
            assert isinstance(value,dict) and value.get('status')=='author_regressed'
            assert isinstance(value.get('judgment'),str) and value['judgment'].strip()
    return dict(read_pages=previous,total_pages=d['page_count'],judged_nodes=len(authored),
        total_nodes=len(nodes),chapters=len(chapter_rows),prefixes=ends,complete=complete)

def validate(complete=False):
    d=json.loads(LEDGER.read_text());structure=json.loads((READ/'structure.json').read_text())
    assert sha(ROOT/d['candidate_pdf'])==d['pdf_sha256']
    for s in d['sources']:assert sha(NEXT/s['path'])==s['sha256']
    for s in structure['sources']:
        assert sha(ROOT/s['path'])==sha(ROOT/s['protected_copy'])==s['sha256']
    for s in json.loads((OUT/'additional-source-lock.json').read_text())['files']:
        assert sha(NEXT/s['path'])==sha(ROOT/s['predecessor_copy'])==s['sha256']
    assert d['baseline_diagnosis']==structure['baseline_diagnosis']
    assert sha(ROOT/d['baseline_diagnosis']['path'])==d['baseline_diagnosis']['sha256']
    segments={}
    for row in d['segments']:
        p=ROOT/row['path'];assert sha(p)==row['sha256'];segments[row['path']]=json.loads(p.read_text())
    for page in structure['pages']:assert sha(ROOT/page['text_path'])==page['text_sha256']
    for row in d['rendered'].values():assert sha(ROOT/row['path'])==row['sha256']
    result=check_records(d,structure,segments,complete)
    print(json.dumps(result));return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['init','render','record','validate','validate_complete']);p.add_argument('args',nargs='*');a=p.parse_args()
    if a.action=='init':init()
    elif a.action=='render':render(*map(int,a.args))
    elif a.action=='record':record(a.args[0])
    else:validate(a.action=='validate_complete')
