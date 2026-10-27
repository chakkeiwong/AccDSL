from pathlib import Path
from copy import deepcopy
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import shared_book_statements_v1 as report
spec=importlib.util.spec_from_file_location('report_execution_examples',ROOT/'data/accounting-master/shared-book-successor-20261024/examples.py')
execution=importlib.util.module_from_spec(spec);spec.loader.exec_module(execution)

def cases():
    out=[]
    for row in execution.cases():
        valid_opening=row['case'] not in ['unknown_lease_membership','unsupported_fx','invalid_lease_allocation','empty_invalid_prefix']
        expected='recorded_prefix' if valid_opening else {'unknown_lease_membership':'unresolved','unsupported_fx':'unsupported'}.get(row['case'],'invalid')
        out.append({'case':row['case'],'request':report.request(row['opening'],row['events']),'expected_status':expected})
    s=execution.opening();s['balances']['revenue']='-1/1';s['balances']['original_equity']='21/1'
    out.append({'case':'opening_income_not_closed','request':report.request(s,[]),'expected_status':'unsupported'})
    s=execution.opening();s['seen']=['old']
    out.append({'case':'opening_history_not_empty','request':report.request(s,[]),'expected_status':'unsupported'})
    x=deepcopy(out[0]);x['case']='stale_opening_digest';x['request']['opening_sha256']='0'*64;x['expected_status']='invalid';out.append(x)
    x=deepcopy(out[0]);x['case']='arbitrary_closing_state';x['request']['closing']={};x['expected_status']='invalid';out.append(x)
    return out
