#!/usr/bin/env python3
"""Check exact source anchors and design deductions without importing Arelle."""
import ast
import hashlib
import json
import time
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
start=time.monotonic()
d=json.loads((OUT/'adapter-dossier.json').read_text())
checks=[]


def check(label,ok):
    checks.append({'check':label,'passed':bool(ok)})


for key,a in d['source_anchors'].items():
    p=ROOT/a['path'];t=p.read_text()
    check(key+' source hash',hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'])
    quote=t[slice(*a['span'])] if 'span' in a else ''.join(t.splitlines(keepends=True)[a['first_line']-1:a['last_line']])
    check(key+' exact inspected quote',quote==a['quote'])
    check(key+' quote hash',hashlib.sha256(quote.encode()).hexdigest()==a['quote_sha256'])
expected='return success and not (options.validationExitCode and (hasValidationErrors or self.errors))'
check('inspected controller expression',d['source_anchors']['run_return']['quote'].strip()==expected)
expression=ast.parse(expected[len('return '):],mode='eval')
# Isolated evaluation of the exact inspected expression, not Arelle execution.
for enabled,errors,expected_bool in [(False,True,True),(True,True,False),(True,False,True)]:
    value=eval(compile(expression,'<inspected-return>','eval'),{'__builtins__':{}},
               {'success':True,'options':SimpleNamespace(validationExitCode=enabled),
                'hasValidationErrors':errors,'self':SimpleNamespace(errors=[])})
    check(f'return expression enabled={enabled} errors={errors}',value==expected_bool)
uri='https://xbrl.fasb.org/us-gaap/2024/elts/us-gaap-2024.xsd'
mapping=d['proposed_input']['uri_map'];check('actual required URI retained',uri in mapping)
removed={k:v for k,v in mapping.items() if k!=uri}
check('missing dependency fixture does not produce valid map',uri not in removed)
g=json.loads((OUT/'graph-final.json').read_text())
nodes={n['uri']:n for n in g['nodes']}
check('wrong namespace fixture is distinct',nodes[uri]['target_namespace']!=nodes['https://xbrl.fasb.org/srt/2024/elts/srt-2024.xsd']['target_namespace'])
check('explicit error-sensitive offline options',d['proposed_runtime_options']['validationExitCode'] is True and d['proposed_runtime_options']['internetConnectivity']=='offline')
check('structured logging explicitly selected',d['proposed_runtime_options']['logFile']=='logToStructuredMessage')
check('no exact dependency lock claimed',d['proposed_environment']['exact_dependency_lock'] is None)
check('whole proposal remains negative',d['acceptance']['whole_proposal']=='not_ready')
result={'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),
        'checks':checks,'wall_seconds':time.monotonic()-start,
        'scope':'Exact source anchors and isolated expression/fixture deductions; no Arelle import/runtime/interface validation.'}
(OUT/'dossier-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:result[k] for k in ['passed','failed','wall_seconds']})
assert result['failed']==0,[c for c in checks if not c['passed']]
