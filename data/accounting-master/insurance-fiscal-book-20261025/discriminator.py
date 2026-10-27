"""Diagnose naive fiscal carry without altering accepted cumulative methods."""
from pathlib import Path
from copy import deepcopy
import importlib.util
import json
import sys
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
import insurance_loss_book_v1 as base
spec=importlib.util.spec_from_file_location('insurance_fiscal_probe_examples',ROOT/'data/accounting-master/insurance-loss-book-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
q=ex.fixture();compiled,_,_=base.build(q);before=deepcopy(compiled)
compiled['opening']['period']['end_exclusive']='2026-01-01'
retained=next(a for a,v in q['opening']['accounts'].items() if v['classification']=='equity')
policies={p:{'kind':'preserve','provenance':'Explicit hypothetical calendar-year memory preservation'} for p in q['opening']['memory_types']}
def carry(year):
    return {'kind':'carry','id':'close.'+str(year),'cutoff':str(year)+'-12-31',
        'equity_movements':[],'notes':[{'id':'completion','label':'Event population','status':'unresolved','reason':'Hypothetical observation only; omitted events unknown'}],
        'retained_account':retained,'next_end_exclusive':str(year+2)+'-01-01','memory_policies':deepcopy(policies)}
compiled['commands']=[carry(2025)]+before['commands'][:4]+[carry(2026)]+before['commands'][4:]+[carry(2027)]
r=base.program.run(compiled)
assert r['status']=='stopped_provisional',r.get('reason')
assert len(r['trace'])==6
assert r['stop']['command']['method_key']=='insurance.4'
current=r['current']
assert current['period']=={'start':'2027-01-01','end_exclusive':'2028-01-01'}
assert current['memory']['insurance']['next_step']=='3/1'
assert current['memory']['insurance']['loss_component']=='11/1'
assert current['balances'][q['roles']['finance_expense']]=='0/1'
path=HERE/'naive-carry.json';assert not path.exists()
path.write_text(json.dumps({'request':compiled,'result':r},ensure_ascii=False,separators=(',',':'))+'\n')
print(json.dumps({'expected_failure':True,'successful_prefix':len(r['trace']),
    'stopped_method':r['stop']['command']['method_key'],'reason':r['stop']['reason'],
    'finance_expense_actual':'0/1','finance_expense_expected_by_old_method':'10/1',
    'repair':'Rebase only temporary-balance pre/postconditions after carry; preserve dated journals and memory'}))
