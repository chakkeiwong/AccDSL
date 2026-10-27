from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import state_decision_schedule_v1 as scheduler
spec=importlib.util.spec_from_file_location('scheduled_decision_examples',ROOT/'data/accounting-master/state-decision-events-20261025/examples.py')
decision_examples=importlib.util.module_from_spec(spec);spec.loader.exec_module(decision_examples)

def start():return decision_examples.start()
def root(state,kind='every_days',enabled=True):
    request=decision_examples.request(state,demand='1/1',enabled=enabled)
    template={key:deepcopy(request[key]) for key in ['model','bindings','output_map','event']}
    del template['event']['id'];del template['event']['date']
    calendar={'kind':'every_days','start':'2027-01-02','end_exclusive':'2027-01-05','step_days':1} if kind=='every_days' else {'kind':'explicit_dates','dates':['2027-01-02','2027-01-03','2027-01-04']}
    return {'profile':scheduler.PROFILE,'id':'stock-calendar','expected_state_sha256':scheduler.digest(state),
            'context':deepcopy(request['context']),'scenario':deepcopy(request['scenario']),
            'schedules':[{'id':'daily-sale','priority':10,'calendar':calendar,'template':template}]}
