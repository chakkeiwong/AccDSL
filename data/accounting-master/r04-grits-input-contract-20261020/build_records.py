"""One-time construction of source and proposed-profile evidence."""
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

os.environ['CUDA_VISIBLE_DEVICES']='-1'
sys.dont_write_bytecode=True
U=Path(__file__).resolve().parent
R=U.parents[2]

def write(name,value):
    with (U/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2);f.write('\n')

def bind(p):return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

def main():
    assert not (U/'source-ledger.json').exists(),'one-time construction'
    s=importlib.util.spec_from_file_location('local_input_comparison',U/'compare.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    anchors=[]
    for name,p,start,end,meaning in [
        ('cell_fields',m.CONVERSION,10,40,'Declared cell types and direct from_dict defaults; no validation method.'),
        ('html_types',m.CONVERSION,81,153,'HTML conversion extracts joined text, but no location box; selected converter path.'),
        ('grid_extent_overwrite',m.CONVERSION,156,179,'Max index extents, default fill and direct assignment overwrite.'),
        ('content_location_defaults',m.CONVERSION,182,205,'Empty content and zero-box defaults; explicit None is assigned unchanged.'),
        ('topology_span',m.CONVERSION,208,250,'Min/max span boxes; holes receive unit-box default.'),
        ('bbox_guard',m.BBOX,33,54,'Only reversed-axis checks in BBox constructor.'),
        ('bbox_area',m.BBOX,61,74,'Widths/heights/products unguarded by finiteness or numeric-range checks.'),
        ('bbox_overlap',m.BBOX,77,111,'Overlap comparisons and products.'),
        ('ragged_guard',m.METRIC,246,260,'Explicit equal-row-length validation exists.'),
        ('metric_input_shape',m.METRIC,274,319,'Pair grid shape, reward invocation and shortcut setup.'),
        ('metric_reward_storage',m.METRIC,320,370,'Reward values enter lookup/alignments; no range/finiteness guard in this path.'),
        ('text_reward',m.METRIC,399,415,'Type annotation and equality shortcut, no text-domain runtime guard.'),
        ('iou_arithmetic',m.METRIC,418,436,'Zero-intersection shortcut, sum-minus-intersection union and division.'),
        ('box_grid_conversion',m.METRIC,439,455,'BBox and area construction before array conversion.'),
        ('location_entry',m.METRIC,477,496,'Location arrays enter factored metric.'),
        ('content_entry',m.METRIC,535,551,'Object array preserves supplied text values.'),
        ('per_metric_accumulation',m.METRIC,785,804,'Appends after per-metric call; no shared transaction.'),
        ('evaluator_defaults',m.METRIC,908,940,'Default con/top; explicit grid-by-metric loop.'),
        ('html_rejections',m.METRIC,966,1008,'Bare string, location HTML and failed parse are explicitly rejected.'),
        ('cell_list_entry',m.METRIC,1016,1045,'Flat-list rejection then sequential per-metric conversion/evaluation.'),
    ]:
        anchors.append({'id':name,**bind(p),'first_line':start,'last_line':end,
            'excerpt':'\n'.join(p.read_text().splitlines()[start-1:end]),'supports':meaning})
    retained=[m.METRIC,m.CONVERSION,m.BBOX,
        R/'data/accounting-master/r04-pubtablesv2-20261019/source-ledger.json',
        R/'data/accounting-master/r04-grits-geometry-20261020/source-ledger.json',
        R/'data/accounting-master/r04-pybind-strings-20261020/completion.json']
    write('source-ledger.json',{'date':'2026-10-20','constructed_utc':datetime.now(timezone.utc).isoformat(),
        'new_acquisitions':0,'repository':'kensho-technologies/grits',
        'commit':'8a281a3e2fd4cfa600d1c1f70f33b5eccc6294f1','bindings':[bind(p) for p in retained],
        'anchors':anchors,'read_scope':'Listed source spans only; no library execution.'})
    write('geometry-examples.json',m.geometry_examples())
    write('input-fixtures.json',m.input_fixtures())
    write('contract.json',{'status':'proposed_optional_profile','default_selected':False,
        'document':bind(U/'adapter-contract.md'),'budgets':'unselected','normalization':'unselected',
        'input_text':'built-in scalar-valid str; explicit absent/empty distinction',
        'topology':'declared extents, nonempty contiguous nonnegative distinct spans, disjoint occupancy',
        'location':'same declared frame; finite ordered coordinates AND valid representable derived geometry',
        'failure_scores_assigned':False,'commit_policy':'stage metric-specific outcomes, then one idempotent sample commit',
        'failure_states':['input_unresolved','invalid_text','invalid_span','overlapping_cells','incompatible_frame',
            'location_unavailable','numeric_range_failure','budget_unset','budget_exceeded','evaluation_failure','result_invalid'],
        'whole_rows_closed':0})
    write('claim-support-ledger.json',{'summary':m.SUMMARY,'claims':[
        {'claim':'Shape/parser checks exist, but do not validate all cell/geometry domains.','class':'IMPLEMENTATION_EVIDENCE',
         'anchors':['ragged_guard','html_rejections','cell_list_entry','cell_fields','bbox_guard']},
        {'claim':'Finite endpoint checks alone cannot establish valid floating IoU.','class':'PROJECT_DERIVATION',
         'anchors':['bbox_area','iou_arithmetic'],'evidence':'geometry-examples.json'},
        {'claim':'Missing text/holes and overlaps require explicit adapter dispositions.','class':'PROJECT_DERIVATION',
         'anchors':['cell_fields','grid_extent_overwrite','content_location_defaults','topology_span']},
        {'claim':'Multi-metric partial accumulation is possible when earlier metric succeeds and later metric raises.','class':'IMPLEMENTATION_EVIDENCE',
         'anchors':['per_metric_accumulation','cell_list_entry'],'scope':'conditional control-flow observation, not integration execution'},
        {'claim':'Proposed stricter profile remains optional and incomplete as a runtime.','class':'PROJECT_DERIVATION',
         'evidence':'adapter-contract.md','scope':'selected conformance illustrations only'},
    ]})
    write('source-support-ledger.json',{'classification':'IMPLEMENTATION_OR_SOFTWARE','source':'Retained pinned Kensho metric/conversion/BBox',
        'identity':'source-ledger.json','read_scope':'20 source spans listed there','publication_status':'official software source',
        'retraction_status':'N/A software; version/current-head correspondence bounded by retained commit',
        'allowed':'selected source contracts and conditional local arithmetic implications',
        'forbidden':'installed behavior, empirical failure rates, historical benchmark changes, accounting validity'})
    write('citation-venue-ledger.json',{'scope':'No new paper or citation query','citation_count':'not available; not queried',
        'venue_metric':'not applicable','criterion':'Primary source and exact local arithmetic, not popularity.'})
    write('backward-snowball-ledger.json',{'route':['selected metric entry points','conversion dataclass/grid builders','BBox and IoU helpers','prior pybind/string evidence'],
        'scope':'Previously acquired source; no new academic references','uninspected':'Native dependency runtime and external callers'})
    write('forward-snowball-ledger.json',{'query':'No new forward-citation search in this source inquiry',
        'new_ready_lead':'Meaning of multi-table upper bound when upper scores are summed only on the lower-score-selected assignment',
        'action':'Separate predeclared mathematical/source inquiry; no global-bound claim yet'})
    write('omission-risk-ledger.json',{'items':[
        {'gap':'Actual producer/caller validation','status':'unverified','risk':'A stronger external validator could exclude malformed examples'},
        {'gap':'Installed numerical behavior','status':'held','risk':'Local scalar arithmetic does not establish NumPy/SciPy execution'},
        {'gap':'Resource budgets and safe numeric representation','status':'unselected','risk':'No readiness/default promotion'},
        {'gap':'Global assignment upper bound','status':'requires inspection','risk':'Pairwise upper bounds may have only fixed-assignment meaning'},
        {'gap':'Financial and disclosure completeness','status':'open','risk':'Any table score remains insufficient for accounting correctness'},
    ]})
    print(json.dumps({'constructed':True,'anchors':len(anchors),'geometry_cases':9,'input_fixtures':14,'new_acquisitions':0}))

if __name__=='__main__':main()
