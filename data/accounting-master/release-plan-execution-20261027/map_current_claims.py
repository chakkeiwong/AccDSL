from pathlib import Path
from fractions import Fraction as F
import json,hashlib
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;T=R/'docs/design/proposal/manuscript-release-prep-v552r1-20261027';S=R/'data/accounting-master/literature-closure-20261026/claim-support.json';B=chr(92)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def loc(file,heading=None):
 p=T/file;lines=p.read_text().splitlines()
 if heading is None:return {'file':file,'line_start':1,'line_end':len(lines),'sha256':sha(p)}
 start=next(i for i,l in enumerate(lines) if l==B+'section{'+heading+'}')
 end=next((i for i in range(start+1,len(lines)) if lines[i].startswith(B+'section{')),len(lines))
 return {'file':file,'heading':heading,'line_start':start+1,'line_end':end,'sha256':sha(p)}
def sim(file,heading=None):return loc('simulation/'+file,heading)
m={
'C01':[sim('01-observations.tex','A rate shock exposes the missing information'),sim('lit-19-literature-9.tex')],
'C02':[sim('08-compression.tex','A sufficient probabilistic condition'),sim('08-compression.tex','Finite-horizon proof'),sim('08a-finite-quotient.tex')],
'C03':[sim('lit-09-approximation-10.tex'),sim('08-compression.tex','Equal totals are insufficient')],
'C04':[sim('lit-09-approximation-4.tex','A quantitative boundary argument'),sim('lit-09-approximation-4.tex','A common-policy regret argument')],
'C05':[sim('lit-09-approximation-4.tex','When sampled paths disclose their own futures')],
'C06':[sim('03-learning.tex','Set-valued evidence updates'),sim('lit-03-learning-1.tex'),sim('lit-03-learning-11.tex')],
'C07':[sim('05-debt.tex','The one-period pricing equation'),sim('05-debt.tex','The convention problem in the supplied note'),sim('05-debt.tex','An exact positive-recovery diagnostic')],
'C08':[sim('lit-05-debt-12.tex'),sim('lit-26-finite-finance-8.tex','Two creditors, policy consistency and financing refusal')],
'C09':[sim('05-debt.tex','Recovery needs its own definition'),sim('06-equity.tex','A simple cash issue'),sim('06-equity.tex','Conversion joins debt and equity')],
'C10':[sim('lit-19-literature-6.tex','Disclosure selection and the observation likelihood')],
'C11':[sim('lit-19-literature-6.tex','When silence has an equilibrium interpretation')],
'C12':[sim('lit-19-literature-6.tex','What changes under an intervention')],
'C13':[sim('19-literature.tex','Contract algorithms')],
'C14':[sim('11-numerics.tex','A residual can target the wrong expectation'),sim('11-numerics.tex','A small objective counterexample'),sim('11-numerics.tex','Partial and total derivatives')],
'C15':[sim('24-evaluation.tex','Forecast origins and leakage'),sim('24-evaluation.tex','Probabilistic forecasts'),sim('24-evaluation.tex','Policy evaluation')],
'C16':[sim('lit-03-learning-2.tex')],
'C17':[sim('lit-25-interactions-7.tex','A complete rate, covenant and ownership path')],
'C18':[sim('lit-08-compression-3.tex')],
'C19':[sim('lit-11-numerics-5.tex','Causal generators and feasible policy transfer')],
'C20':[sim('lit-11-numerics-5.tex','Controlled transition laws and off-policy support')],
'C21':[sim('lit-09-approximation-4.tex','A finite coupling method for discrete decisions')],
'C22':[sim('lit-26-finite-finance-8.tex','Why positive surplus can still end in liquidation')],
'C23':[sim('lit-03-learning-1.tex')],
'C24':[sim('lit-26-finite-finance-8.tex','Two creditors, policy consistency and financing refusal')],
'C25':[sim('lit-25-interactions-7.tex','Executing promises, carrying amounts and ownership')],
'C26':[sim('lit-11-numerics-5.tex','Controlled transition laws and off-policy support')],
'C_PMMCMC_AUX':[sim('inference-exchange.tex','Changing particles without changing the target')]
}
notes={
'C07':'The historical ledger reports accumulated proceeds minus payoff = -44/101; the current chapter reports payoff minus accumulated proceeds = +44/101. These are opposite residual conventions, not contradictory pricing results. Publisher correction/edition status remains unresolved.',
'C13':'Current passage preserves the matched-version/runtime limitation; the retained 24 hand-derived checks remain an external evidence route, not new runtime conformance.',
'C14':'Current passages state the objective identity and partial/total derivative distinction. Pinned notebook-specific criticism remains in the separate technical record; it is not automatically a claim about risky-debt code.',
'C15':'The current chapter presents an evaluation protocol, not executed empirical policy identification. Transfer of original support must retain that distinction.',
'C19':'Current passage explicitly limits the counterexample to the retained version and transfer-class assumptions. This navigation review does not newly establish a journal erratum or re-read the source theorem.',
'C_PMMCMC_AUX':'The current inference chapter explains auxiliary-state retention and a distinct representation-exchange example (one-step 65/112). The historical refreshing-current stationary example (10/19) remains in pmcmc-dependency.md; these must not be merged as one numerical result.'
}
rows=[];original=json.loads(S.read_text())['records']
assert set(m)=={x['id'] for x in original}
for row in original:
 rows.append({'id':row['id'],'original_record':row,'original_ledger':str(S.relative_to(R)),'original_pointer':'/records/'+str(original.index(row)),'original_ledger_sha256':sha(S),'current_locations':m[row['id']],'mapping_status':'current_argument_locations_inspected; inherited technical support requires final implication/edition acceptance','scope_note':notes.get(row['id'],'Preserve source assumptions and local-derivation scope in the original record. Location mapping is not a new technical-source or independent accounting acceptance.')})
checks=[]
def ck(n,a,b):checks.append({'check':n,'actual':str(a),'expected':str(b),'pass':a==b})
p=F(1880,21);wrong=F(9000,101);rf=F(21,20);payoff=F(94)
ck('correct_proceeds_break_even',p*rf,payoff);ck('historical_residual',wrong*rf-payoff,F(-44,101));ck('current_residual',payoff-wrong*rf,F(44,101));ck('residual_sign_relation',(wrong*rf-payoff)+(payoff-wrong*rf),F(0))
ck('safe_junior_proceeds',F(60)/rf,F(400,7));ck('risk_junior_proceeds',F(40)/rf,F(800,21));ck('incentive_quote_shortfall',F(400,7)-F(800,21),F(400,21));ck('risk_subscription',F(60)-F(800,21),F(460,21))
ck('finite_coupling_bound',12*(1-F(19,20)**3),F(3423,2000))
# Exact invariant/mismatch consequences for the two distinct auxiliary-state examples.
P=[[F(0),F(0),F(1)],[F(0),F(1,3),F(2,3)],[F(1,4),F(1,2),F(1,4)]];pi=[F(1,8),F(3,8),F(1,2)]
for j in range(3):ck('retained_aux_stationarity_'+str(j),sum(pi[i]*P[i][j] for i in range(3)),pi[j])
ck('refreshed_current_stationary_type1',F(5,6)/(F(5,6)+F(3,4)),F(10,19))
ck('exchange_wrong_joint_one_step',F(1,4)+F(1,4)*F(4,7)+F(1,2)*F(3,8),F(65,112))
result={'date':'2026-10-27','candidate':str(T.relative_to(R)),'rows':rows,'checks':checks,'passed':all(c['pass'] for c in checks),'status':'27 inherited claims have precise current argument routes; 14 exact local arithmetic checks; technical source rereading and release acceptance not closed'}
(H/'current-claim-map.json').write_text(json.dumps(result,indent=2)+chr(10))
lines=['# Current locations of consequential simulation claims','','The 27 claims from the literature-closure supplement now point to exact current source ranges. Each retains its old evidence, technical limits and origin. This review checks the integration and stated local arithmetic, not every primary theorem or edition.','','| Claim | Current location | Scope |','|---|---|---|']
for r in rows:lines.append('| '+r['id']+' | '+'; '.join(x['file']+':'+str(x['line_start']) for x in r['current_locations'])+' | '+r['scope_note']+' |')
lines+=['','The debt residual changes sign because the subtraction order changes; both conventions expose the same nonzero mismatch. The particle examples concern different operations and retain separate numerical results. All '+str(len(checks))+' independent exact arithmetic checks pass. Current source-to-claim acceptance and broader source-route review remain open.']
(H/'current-claim-map.md').write_text(chr(10).join(lines)+chr(10));print(json.dumps({'claims':len(rows),'checks':len(checks),'passed':result['passed']}))
