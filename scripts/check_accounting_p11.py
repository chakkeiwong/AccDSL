"""Reproduce P11 deterministic conformance and honest availability evidence."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
from fractions import Fraction as F
from decimal import Decimal, ROUND_HALF_EVEN

os.environ['CUDA_VISIBLE_DEVICES']='-1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import accounting_integrations_v1 as adapters
import demo_debt_execution_v1 as debt
import core0_ir_v1 as ir

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',required=True)
    output=Path(parser.parse_args().output_dir);output.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    protected=['docs/design/fixtures/demo-debt-package.json','docs/design/fixtures/borrowing.acc',
               'scripts/core0_ir_v1.py','scripts/core0_frontends_v1.py','tests/test_accounting_p03.py',
               'docs/design/spec/core-ir.schema.json','scripts/run_accounting_master.py',
               'scripts/accounting_master_support.py','scripts/accounting_master_catalog.json',
               'scripts/accounting_master_response.schema.json','tests/test_accounting_master.py',
               'docs/plans/accounting-master-program.md']
    initial={p:adapters.sha(ROOT/p) for p in protected}
    inventory_file='data/accounting-master/runs/20261003T055003-956101b1/P11/phase-entry-inventory.json'
    phase_entry=json.loads((ROOT/inventory_file).read_text())
    entry_mismatches=[p for p in protected if phase_entry.get(p)!=initial[p]]
    if entry_mismatches:raise ValueError('protected inputs changed since phase entry: '+repr(entry_mismatches))
    records=adapters.collect()
    for row in records['adapters']:adapters.validate_record(row)
    cases=[]
    for name,options,x,branch in [('fixed',{},F(1),'allFixed'),('floating',{},F(0),'allFloating'),
        ('interior',{'interior':True},F(1,4),'conditioned'),
        ('changed_principal_stress',{'principal':150,'stress':'0.08'},F(0),'allFloating'),
        ('renamed',{'renamed':True},F(0),'floating'),('insufficient_cash',{'cash':4},F(1),'allFixed')]:
        source,typed,bindings,textual,constructed=debt.matched_case(**options)
        assignment={'share' if options.get('renamed') else 'alpha':x}
        left=debt.execute(textual,bindings,assignments=assignment,alternative=branch)
        right=debt.execute(constructed,bindings,assignments=assignment,alternative=branch)
        if left!=right:raise ValueError('frontend execution mismatch')
        p=Decimal(str(options.get('principal',100)))
        alpha=Decimal(x.numerator)/Decimal(x.denominator)
        rate=Decimal(options.get('stress','0.07'))
        interest=(p*(alpha*Decimal('0.05')+(1-alpha)*rate)).quantize(Decimal('0.01'),rounding=ROUND_HALF_EVEN)
        cash=Decimal(str(options.get('cash',p-5)))
        settled=cash>=interest
        payment=interest if settled else Decimal(0)
        oracle={'interest':str(interest),'cash':str(cash-payment),'debt':str(p),
                'equity':str(cash-p-payment),'profit':str(-payment)}
        for key,value in oracle.items():
            actual=left[key] if key=='interest' else left['reports'][key]
            if F(actual)!=F(value):raise ValueError('independent arithmetic mismatch: '+key)
        if left['status']!=('Completed' if settled else 'Defaulted'):
            raise ValueError('settlement status mismatch')
        cases.append({'name':name,'inputs':options,'dsl_source':source,'typed_program':ir.binding_projection(typed),
                      'bindings':ir.binding_projection(bindings),'semantic_ir_sha256':debt.digest(ir.semantic_projection(textual)),
                      'same_semantics':True,'same_execution':True,'oracle_passed':True,
                      'independent_decimal_oracle':oracle,'dsl_result':left,'typed_result':right})
    checks=[]
    for test in ('test_accounting_p11.py','test_accounting_p03.py'):
        check=adapters.capture([sys.executable,'-B','-m','unittest','discover','-s','tests','-p',test,'-v'])
        checks.append(check)
    unchanged=initial=={p:adapters.sha(ROOT/p) for p in protected}
    git=adapters.capture(['git','rev-parse','HEAD'])
    git_root=adapters.capture(['git','rev-parse','--show-toplevel'])
    project_git=(git['exit_code']==0 and git_root['exit_code']==0 and
                 Path(git_root['stdout'].strip()).resolve()==ROOT)
    changed=['scripts/accounting_integrations_v1.py','scripts/demo_debt_execution_v1.py',
             'scripts/check_accounting_p11.py','tests/test_accounting_p11.py']
    changed += [str(p.relative_to(ROOT)) for p in sorted(debt.FIXTURES.iterdir()) if p.is_file()]
    manifest={'created_at':datetime.now(timezone.utc).isoformat(),'git_commit':git['stdout'].strip() if project_git else None,
        'git_probe':git,'git_root_probe':git_root,'git_provenance':'project repository' if project_git else 'No project Git provenance; any ancestor repository hash is not attributed to AccDSL.',
        'command':[sys.executable,'-B',*sys.argv], 'interpreter':sys.executable,'python':sys.version,
        'environment':os.environ.get('CONDA_DEFAULT_ENV'),'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1 intentionally hides GPU devices',
        'seeds':'N/A deterministic','data_version':'P11 synthetic fixtures; hashes below',
        'plan_file':'data/accounting-master/runs/20261003T055003-956101b1/P11/approved-plan.json',
        'result_file':str(output/'result.md'),'artifacts':[str(output/'integrations.json'),str(output/'result.md')],
        'changed_source_files':changed,'file_hashes':{p:adapters.sha(ROOT/p) for p in changed},
        'protected_input_hashes':initial,'protected_inputs_unchanged':unchanged,
        'phase_entry_inventory':inventory_file,'phase_entry_hashes_match':not entry_mismatches,
        'wall_seconds':time.monotonic()-started}
    result={'schema_version':'accdsl.p11.integrations.v1',**records,'matched_frontends':cases,'checks':checks,'manifest':manifest,
        'external_integrations_completed':sum(r['status']=='Passed' for r in records['adapters']),
        'engineering_checks_passed':unchanged and all(c['exit_code']==0 and not c['timeout'] for c in checks),
        'accounting_validity':'not established','forecast_validity':'not evaluated','human_acceptance':'pending',
        'human_authoring_superiority':'no study; no inference',
        'residuals':['External integrations unavailable in this environment.',
            'Inline scale and PDF physical page locations are not exercised.',
            'ACTUS service and Ledger/hledger wire translators are not implemented; no selected backend substitution.',
            'G2/G9 and wider MC01–MC35/G1–G18 obligations remain open.']}
    (output/'integrations.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'engineering_checks_passed':result['engineering_checks_passed'],
                     'external_integrations_completed':result['external_integrations_completed'],
                     'frontend_cases':len(cases),'artifact':str(output/'integrations.json')}))
    return 0 if result['engineering_checks_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
