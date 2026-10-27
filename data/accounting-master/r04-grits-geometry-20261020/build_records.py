"""One-time geometry documentary records and exact examples."""
import hashlib
import json
from pathlib import Path
import shlex
from compare import calculate

UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]
BASE=UNIT.parent


def bind(p):
    return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}


def write(name,value):
    with (UNIT/name).open('x') as handle:
        json.dump(value,handle,indent=2);handle.write('\n')


def main():
    assert not (UNIT/'source-ledger.json').exists(),'one-time construction'
    acquisitions=[]
    for stem in ('01-environment','02-bbox','03-project','04-rect-docs','05-historical-tree','06-historical-rect'):
        receipt=UNIT/'sources'/(stem+'.receipt.json');r=json.loads(receipt.read_text())
        header=UNIT/'sources'/(stem+'.headers');body=ROOT/r['filename_effective']
        invocation=UNIT/'sources'/(stem+'.invocation.json')
        if invocation.exists():
            command=json.loads(invocation.read_text())['argv']
        else:
            command=['curl','--silent','--show-error','--location','--connect-timeout','10','--max-time','35',
                '--max-filesize','2097152','--proto','=https','--proto-redir','=https','--dump-header',str(header.relative_to(ROOT)),
                '--output',str(body.relative_to(ROOT)),'--write-out','%{json}\\n',r['url']]
        acquisitions.append({'url':r['url'],'effective_url':r['url_effective'],'status':r['http_code'],
            'bytes':r['size_download'],'curl_seconds':r['time_total'],'command':shlex.join(command),
            'body':bind(body),'headers':bind(header),'receipt':bind(receipt)})
    blob_bindings=[]
    for local,tree,source in (
        ('01-environment.body',BASE/'r04-grits-theory-20261020/sources/04-tree.json','environment.yml'),
        ('02-bbox.body',BASE/'r04-pubtablesv2-20261019/sources/04-tree.json','grits/bbox.py'),
        ('03-project.body',BASE/'r04-pubtablesv2-20261019/sources/04-tree.json','pyproject.toml'),
        ('06-historical-rect.body',UNIT/'sources/05-historical-tree.body','docs/rect.rst')):
        blob_bindings.append({'tree':str(tree.relative_to(ROOT)),'source_path':source,
                              'local_path':str((UNIT/'sources'/local).relative_to(ROOT))})
    needles={
        UNIT/'sources/01-environment.body': [('python-recipe','python==3.10.9'),('pymupdf-recipe','PyMuPDF==1.21.1')],
        UNIT/'sources/02-bbox.body': [
            ('coordinate-convention','left-to-right x-axis and the top-to-bottom y-axis'),
            ('ordered-boxes','assumes that x0 <= x1 and y0 <= y1'),
            ('x-check','if self.x0 > self.x1:'),('y-check','if self.y0 > self.y1:'),
            ('bbox-area','return self.width * self.height'),
            ('horizontal-overlap','return min(source.x1, target.x1) - max(source.x0, target.x0)'),
            ('vertical-overlap','return min(source.y1, target.y1) - max(source.y0, target.y0)'),
            ('intersection-area','return get_horizontal_overlap(source, target) * get_vertical_overlap(source, target)')],
        UNIT/'sources/03-project.body': [('python-range','requires-python = ">=3.10"'),
            ('pylcs-range','"pylcs>=0.1.1"'),('numpy-range','"numpy>=1.26"'),('scipy-range','"scipy>=1.15,<2"')],
        UNIT/'sources/04-rect-docs.txt': [('current-enclosure','The smallest rectangle containing the current one and'),
            ('current-doc-scope','This documentation covers all versions up to 2.0.'),
            ('current-date','Last updated on 19. Oct 2026')],
        UNIT/'sources/06-historical-rect.body': [
            ('historical-version-change','**(Changed in v1.19.0)**'),
            ('historical-open','**Rectangles are (semi-) open:**'),
            ('historical-copy','the constructor creates a **new copy**'),
            ('historical-intersection','The intersection (common rectangular area, largest rectangle contained in both)'),
            ('historical-enclosure','The smallest rectangle containing the current one and *r* is calculated'),
            ('historical-area','Calculate the area of the rectangle and, with no parameter, equals *abs(rect)*.'),
            ('historical-width','Equals ``max(x1 - x0, 0)``.')],
        BASE/'r04-grits-theory-20261020/sources/05-metric.py': [('original-denominator','union = Rect(bbox1).include_rect(bbox2)'),
            ('original-ratio','return intersection.get_area() / union.get_area()')],
        BASE/'r04-pubtablesv2-20261019/sources/05-metric.py': [('current-union','union = area_1 + area_2 - intersection'),
            ('current-ratio','return intersection / union'),('current-zero','if intersection == 0:')],
    }
    passages=[]
    for path,rows in needles.items():
        lines=path.read_text().splitlines()
        for identifier,quote in rows:
            hits=[i for i,line in enumerate(lines,1) if quote in line];assert hits,(identifier,quote)
            # Current-doc overview contains a distinct small-rectangle sentence;
            # use the occurrence following include_rect's detailed entry.
            line=hits[0]
            if identifier=='current-enclosure':line=next(i for i in hits if i>500)
            passages.append({'id':identifier,'path':str(path.relative_to(ROOT)),'line':line,'quote':quote})
    witness=calculate()
    write('source-ledger.json',{'date_local':'2026-10-20','acquisitions':acquisitions,
        'blob_bindings':blob_bindings,'passages':passages,
        'historical_dependency':{'tag':'1.21.1','tree_sha':'0f01aafb9514be278b301c0f1b00d88209b01ac6',
            'document_blob':'83849346d6ccbd981ce3080654903292b0ea59e5','commit_sha':'not resolved'},
        'reading':'Full three small code/config files and historical rect.rst; selected current-doc API/coordinate/version spans',
        'installed_behavior':'not checked; no acquired code executed'})
    write('witnesses.json',witness)
    write('source-support-ledger.json',{'classification':'IMPLEMENTATION_OR_SOFTWARE','date':'2026-10-20',
        'sources':[{'title':'PyMuPDF1.21.1 rectangle documentation','authors':'PyMuPDF project','local':bind(UNIT/'sources/06-historical-rect.body'),
                    'publication_status':'Repository documentation at tag/tree/blob, not paper or installed binary'},
                   {'title':'Kensho GriTS bbox helper and project metadata','authors':'Kensho Technologies','local':bind(UNIT/'sources/02-bbox.body'),
                    'publication_status':'Pinned current source'}],
        'paper_context':'GriTS v3 Sections3.3-3.5 already technically read in predecessor; no new paper acquisition',
        'retraction_quarantine':'No status warning observed in inspected docs; independent correction search not performed',
        'technical_sections':['include_rect','intersect','get_area','coordinate conventions','complete bbox helper','dependency recipes'],
        'allowed':['documented enclosure semantics','source formula distinction','exact finite-coordinate deduction'],
        'forbidden':['historical installed identity','published score correction','current dependency set validated','licence clearance']})
    write('citation-venue-ledger.json',{'date':'2026-10-20','citation_count':'not available','citation_source':'not queried for software API documents',
        'venue':'official repository/API documentation','venue_metric':'not available','caveat':'Repository ownership does not certify runtime or historical scores.'})
    write('backward-snowball-ledger.json',{'scope':'Concrete dependency/source links, no new academic bibliography',
        'entries':[{'target':'PyMuPDF1.21.1','classification':'IMPLEMENTATION_OR_SOFTWARE','action':'Exact-tag API document acquired; implementation/native core uninspected'},
                   {'target':'pylcs>=0.1.1','classification':'IMPLEMENTATION_OR_SOFTWARE','action':'Next bounded source inquiry for string semantics'},
                   {'target':'NumPy/SciPy/lxml','classification':'IMPLEMENTATION_OR_SOFTWARE','action':'Version ranges recorded; runtime/transitive identities remain uninspected'},
                   {'target':'GriTS original paper','classification':'DIRECT_METHOD','action':'Reuse completed technical reading, do not repeat'}]})
    write('forward-snowball-ledger.json',{'new_query':'None in bounded dependency inquiry','retained_followups':['Kensho GriTS','PubTables-v2','POTATR'],
        'status':'Specific retained source chain only; no comprehensive citing-work search or coverage claim'})
    write('claim-support-ledger.json',{'candidate':'3.44','manuscript_changed':False,'entries':[
        {'claim':'Original documented recipe computes IoU','verdict':'wrong relative to stated set-union target',
         'support':['historical-enclosure','original-denominator','original-ratio'],'deduction':'intersection/enclosure differs from intersection/union for selected valid boxes',
         'limit':'Static source plus exact-version API contract; installed implementation not executed'},
        {'claim':'Current selected formula is set-union IoU for finite ordered boxes','class':'PROJECT_DERIVATION',
         'support':['intersection-area','current-union','current-ratio'],'limit':'Valid coordinate domain; no general nonfinite-input/runtime claim'},
        {'claim':'Topology as well as location can differ','class':'PROJECT_DERIVATION','support':'Vertical/horizontal relative3-cell-span witness yields1/9 versus1/5'},
        {'claim':'Historical benchmark impact','class':'SOURCE_GAP_BLOCKER','support':'Exact historical data/executable/runtime identity unavailable'}]})
    write('omission-risk-ledger.json',{'entries':[
        {'gap':'PyMuPDF native implementation/installed correspondence','status':'uninspected','risk':'Documentation is a contract, not binary evidence'},
        {'gap':'pylcs exact source and Unicode semantics','status':'next source inquiry','risk':'New wrapper delegates to a dependency with only a lower version bound'},
        {'gap':'Nonfinite/malformed coordinate validation','status':'open implementation obligation','risk':'Axis-order checks alone do not enforce finite inputs'},
        {'gap':'Historical benchmark revision and score impact','status':'open','risk':'Source mismatch cannot numerically correct unacquired evaluations'}],
        'survey_status':'Additive dependency evidence; no comprehensive literature closure'})
    print(json.dumps({'constructed':True,'anchors':len(passages),'cases':len(witness['cases']),
        'strict_cases':[{k:v for k,v in r.items() if k in ('name','iou','intersection_over_enclosure')} for r in witness['cases'] if r['strict_difference']]}))


if __name__=='__main__':main()
