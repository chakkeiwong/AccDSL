"""One selected source interpretation over the complete preserved source network."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'scripts'))
import temporal_measurement_constraints_v1 as temporal
PROFILE='SelectedDebtReadingNetwork/1'
PARENT='59733905148fc905fbcdad6a5115ba644f0e1067216debbcf4035fe158da6a22'
READING='9307f2a2f4f75e01d3f6e2157913059750342ccd18ddf98ce7988fac6066fec5'
OBS='a69f27d314a20d2f5dc69ae2bc795a7abf5a8c1ae49e695b29e1547109910752'
ROUNDING={'id':'displayed_million_nearest_ties_away_v1','status':'proposed',
 'meaning':'Each selected amount is rounded to the nearest displayed USD million; exact half ties round away from zero.',
 'mode':'nearest_ties_away_from_zero','quantum':'1/1','unit':'USD million'}
def digest(v):return sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def need(ok,reason):
 if not ok:raise ValueError(reason)
def prepare(parent,reading,rounding):
 need(digest(parent)==PARENT,'selected_parent_identity')
 common=dict(profile=PROFILE,source_parent=deepcopy(parent),parent_sha256=PARENT,
  source_admission=False,accounting_admission=False,actual_history='unknown',executable_opening=None,
  whole_statement_history_complete=False,scope='one_selected_reported_reading_and_full_supported_network')
 if reading is None:return {**common,'status':'unresolved','reason':'selected_reading_missing'}
 need(digest(reading)==READING,'selected_reading_identity')
 common.update(reading=deepcopy(reading),reading_sha256=READING)
 if rounding is None:return {**common,'status':'unresolved','reason':'rounding_premise_missing'}
 need(rounding==ROUNDING,'rounding_premise_mismatch')
 original=parent['definition'];before=original['observations'][OBS]
 need(before['interval'] is None,'original_interval_was_not_unknown')
 need(reading['displayed_value_usd_million']=='0/1' and reading['decimals']=='-6','reported_zero_accuracy')
 need(before['type']['time']==dict(kind='period',start='2023-10-01',end_exclusive='2024-09-29'),'measurement_period')
 need(before['type']['value_type']['scale']=='1000000/1','measurement_scale')
 definition=deepcopy(original);definition['observations'][OBS]['interval']={
  'lower':'-1/2','upper':'1/2','lower_inclusive':False,'upper_inclusive':False}
 definition['observations'][OBS]['interval_premise']={
  'id':'selected_reported_zero:'+READING,'status':'proposed',
  'meaning':'The separately selected issuance reading reports zero at million-dollar accuracy; under the explicitly retained nearest-million ties-away hypothesis its latent amount lies strictly between -1/2 and 1/2 USD million. Exact economic zero and nonnegative issuance are not assumed.'}
 need(definition['relations']==original['relations'],'equations_preserved')
 need(all(v==definition['observations'][k] for k,v in original['observations'].items() if k!=OBS),'other_measurements_preserved')
 return {**common,'status':'prepared','definition':definition,'rounding_hypothesis':deepcopy(rounding),
  'interpretation':dict(observation=OBS,original=deepcopy(before),selected=deepcopy(definition['observations'][OBS]),old_unresolved_measurements=deepcopy(parent['unresolved_measurements']))}
def assess(parent,reading,rounding,budget):
 try:
  result=prepare(parent,reading,rounding)
  if result['status']!='prepared':return result
  a=temporal.assess(result['definition'],budget)
  return {**result,'status':a['status'],'assessment':a,'budget':deepcopy(budget)}
 except (ValueError,KeyError,TypeError) as exc:
  return dict(profile=PROFILE,status='invalid',reason=str(exc),source_admission=False,accounting_admission=False,actual_history='unknown',executable_opening=None,whole_statement_history_complete=False)
