"""Record individual original-failure comparisons without replacing the map."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
BASE='data/accounting-master/unified-program-20261028/failure-map.json'
REL='data/accounting-master/company-state-relationship-dependencies-20261028/'
ASSET='data/accounting-master/company-state-asset-cohort-dependencies-20261028/'
GUARD='data/accounting-master/continuous-guards-20261026/attempt-02/'
CERT='data/accounting-master/symbolic-method-certificate-20261026/attempt-01/'

def main():
    out=HERE/'failure-dispositions.json'
    if out.exists():raise FileExistsError(out)
    originals=json.loads((ROOT/BASE).read_text())['rows']
    by_id={r['original_row']['id']:r['original_row'] for r in originals}
    specs=[
        ('SIM-F004','partial_related_control',
         'Unknown control transfer and useful life are retained as unresolved; no missing-guarantee case was executed in this continuation.',
         [REL+'attempt-01/verification.json',ASSET+'attempt-01/verification.json'],
         'Execute the original omitted guarantee field through an applicable guarantee method, preserving the unresolved amount and structural omission.'),
        ('SIM-F005','partial_related_control',
         'The same aggregate journals/reports admit different claim allocations. The original fixed/floating debt and interest discriminator is not this claim case.',
         [REL+'attempt-01/inspection.json',REL+'attempt-01/controls.json'],
         'Locate or execute the original fixed/floating joint-history case and compare its actual observation set before claiming that row covered.'),
        ('SIM-F019','partial_related_control',
         'The policy probe preserves its exact parent, first-year history and every non-target input. It is a deterministic paired-path comparison, not a study across heterogeneous worlds.',
         [REL+'policy-attempt-02/verification.json',REL+'policy-repair-01.md'],
         'Pair the same policies across each retained joint history using one declared information set; preserve the full conditional outcome table.'),
        ('SIM-F043','original_discriminator_executed_scoped',
         'The exact Machine20 case now executes: identical first-close reports and carrying value20, then next charges10 and20 under supplied lives2 and1. All native years complete.',
         [ASSET+'failure-attempt-01/verification.json',ASSET+'failure-attempt-01/results.json',ASSET+'failure-attempt-01/original-row.json'],
         'Retain this native annual-method evidence; broader asset methods, industry applicability and package acceptance remain open.'),
        ('SIM-F066','partial_related_control',
         'Year-qualified event IDs and the saved policy-parent hash are checked. The original refinancing and tax/ownership-cache invalidation case was not executed here.',
         [REL+'attempt-01/verification.json',REL+'policy-attempt-01/failure.json',REL+'policy-attempt-02/verification.json'],
         'Trace the original refinancing operation through tax and ownership cache dependencies; reject stale identities and compare the complete rebuilt path.'),
        ('X07','no_additional_original_case_coverage',
         'Synthetic relationship/asset records explicitly retain unknown identities and no actual-source admission. No partial actual issuer claim disclosure was passed through method admission here.',
         [REL+'result.md',ASSET+'result.md'],
         'Bind one source-backed partial population to method admission and prove that missing counterparties/instruments and unknown completeness survive the join.'),
        ('X20','retained_scoped_evidence_reinspected',
         'The original retained continuous-guards result explicitly checks refusal_retains_due and forgotten_payable_is_wrong. New trade over-settlement is related, not a replacement for accrued-interest preservation.',
         [GUARD+'verification.json',GUARD+'checks.json',GUARD+'controls.json'],
         'Retain the exact original accrued-payable evidence; extend to additional payment/default methods only under their own declared inputs and source support.'),
        ('X32','retained_scoped_evidence_reinspected',
         'The retained symbolic certificate refuses wrong bindings, parameter substitution and unused parameters. The new policy-parent rejection checks a related path identity, not all parameter occurrences.',
         [CERT+'verification.json',CERT+'controls.json',REL+'policy-attempt-01/failure.json'],
         'Use the exact symbolic occurrence certificate for its selected profile; inspect new method declarations separately before broader composition.')
    ]
    rows=[];evidence={BASE}
    for id,status,comparison,paths,next_action in specs:
        for p in paths:
            assert (ROOT/p).is_file();evidence.add(p)
        rows.append(dict(id=id,original_row=deepcopy(by_id[id]),disposition=status,
                         comparison=comparison,evidence=paths,next_action=next_action,
                         original_status_unchanged=True,broad_package_closed=False))
    assert len(rows)==8 and len(originals)==201
    check=json.loads((ROOT/(ASSET+'failure-attempt-01/verification.json')).read_text())
    assert check['status']=='pass' and check['original_failure']=='SIM-F043'
    assert json.loads((ROOT/(ASSET+'failure-attempt-01/original-row.json')).read_text())==by_id['SIM-F043']
    guard=json.loads((ROOT/(GUARD+'checks.json')).read_text())
    assert any(c['name']=='refusal_retains_due' and c['pass'] for c in guard)
    gcontrol=json.loads((ROOT/(GUARD+'controls.json')).read_text())
    assert any(c['name']=='forgotten_payable_is_wrong' and c['discriminates'] for c in gcontrol)
    cert=json.loads((ROOT/(CERT+'controls.json')).read_text())
    names=['wrong_binding','extra_parameter','parameter_substitution','literalized_parameter_loss']
    assert all(any(c['name']==name and c['refused'] for c in cert) for name in names)
    payload=dict(date='2026-10-28',scope='Eight individually inspected rows; remaining193 not dispositioned by this continuation',
                 original_population=201,reviewed_rows=8,original_statuses_preserved=True,rows=rows)
    out.write_text(json.dumps(payload,indent=2)+chr(10))
    lines=['# Original failure dispositions after population construction','',
           '28 October 2026. Eight original rows inspected individually;193 others remain outside this continuation. Original statuses and all201 rows are unchanged.','',
           '| Original row | Current comparison | Residual / next action |','| --- | --- | --- |']
    for row in rows:lines.append('| '+row['id']+' | '+row['comparison']+' | '+row['next_action']+' |')
    lines.extend(['','SIM-F043 now has its exact original numerical discriminator in the native annual profile. The broader packages remain open. Related checks are explicitly distinguished from original-case coverage. No stochastic ranking or release acceptance follows.','',
        'Post-review risk: similar wording can conceal different targets. The preserved original rows and exact comparisons prevent new claim or cohort tests being substituted for guarantee, refinancing, source-admission or parameter-certificate obligations.'])
    (HERE/'failure-dispositions.md').write_text(chr(10).join(lines)+chr(10))
    evidence.update([str(Path(__file__).relative_to(ROOT)),'docs/plans/company-state-failure-dispositions-20261028.md'])
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],environment=sys.version,cpu_gpu='CPU documentary inspection; no accelerator imports',
        random_seeds='N/A nonstochastic',wall_time='Documentary review; no performance claim',
        utc=datetime.now(timezone.utc).isoformat(),
        plan_file='docs/plans/company-state-failure-dispositions-20261028.md',
        result_file=str((HERE/'failure-dispositions.md').relative_to(ROOT)),
        source_hashes={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(evidence)})
    (HERE/'failure-dispositions-manifest.json').write_text(json.dumps(manifest,indent=2)+chr(10))
    print(json.dumps(dict(original_rows=201,individually_reviewed=8,unreviewed_in_this_pass=193,original_conditions_preserved=True)))

if __name__=='__main__':main()
