"""Read-only operational correction: archive-backed schema has no separate receipt."""
import sys
sys.dont_write_bytecode=True
from check import *

evidence=load(OUT/'declarations.json')
checks=validate(evidence)
corruptions=negatives(evidence)
findings={'checks':checks,'negative_cases':corruptions,
          'declared_types':[{k:r[k] for k in ['fact_id','original_token','declared_type','terminal_builtin']} for r in evidence['rows']]}
require(findings==load(OUT/'checks.json'),'REPLAY_CHANGED')
manifest=load(OUT/'run-manifest.json')
nulls=sum(row is None for row in manifest['protected_inputs'])
require(nulls==1,'UNEXPECTED_NULL_COUNT')
missing=[row for row in evidence['schemas'] if row['acquisition_receipt'] is None]
require(len(missing)==1 and missing[0]['source']['path']=='data/accounting-master/taxonomy-reuse-20261007/archive/aapl-20240928.xsd','UNEXPECTED_ABSENT_RECEIPT')
rows=[r for r in manifest['protected_inputs']+manifest['artifacts'] if r is not None]
for row in rows:require(binding(ROOT/row['path'])==row,'PROTECTED:'+row['path'])
require(binding(ROOT/missing[0]['source']['path'])==missing[0]['source'],'ARCHIVE_SOURCE_HASH')
print(json.dumps({'replay':'pass','checks':len(checks),'corruptions_rejected':len(corruptions),'verified_bindings':len(rows),
                  'absent_separate_receipt':'issuer archive schema; exact source hash verified','original_recording_preserved':True}))
