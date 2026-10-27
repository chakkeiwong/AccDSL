"""A separately named documentary successor, never a frozen-profile mutation."""
from pathlib import Path
from datetime import date
import importlib.util,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
EXACT=HERE.parent/'exact-information-time-20261026'
sys.path.insert(0,str(EXACT))
import projection
ATT=HERE.parent/'extended-method-exchanges-20261015/bank-assessment/attempt-03'
sys.path.insert(0,str(ATT/'inputs'))
spec=importlib.util.spec_from_file_location('exact_bank_native',ATT/'inputs/verify_exchanges.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native);native.ROOT=ROOT
PROFILE='ExactBankInformation/1'

def exact(value):
    try:return projection.instant(value)
    except projection.Unsupported as exc:raise native.Refusal('exact_time_unsupported:'+str(exc))
    except (ValueError,TypeError,OverflowError) as exc:raise native.Refusal('exact_time_invalid:'+str(exc))

class Auditor(native.Auditor):
    def information(self,root,view_ref):
        view=self.body(view_ref)
        allowed={native.enc(ref) for ref in view['evidence_refs']}
        cutoff,system=exact(view['decision_at']),exact(view['system_asof'])
        cutoff_day=date.fromordinal(int(cutoff//86400)+1)
        for digest in self.closure([root]):
            record=self.reg[digest]
            if record['kind']!='Evidence':continue
            ref={'kind':'Evidence','schema':record['schema'],'digest':digest}
            evidence=record['body']
            native.need(native.enc(ref) in allowed,'evidence_not_in_view')
            native.need(exact(evidence['available_at'])<=cutoff,'later_information')
            native.need(exact(evidence['ingested_at'])<=system,'later_ingestion')
            native.need(native.day(evidence['measurement_asof'])<=cutoff_day,'future_measurement')
