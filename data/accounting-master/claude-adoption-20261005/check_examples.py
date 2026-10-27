#!/usr/bin/env python3
"""Bounded arithmetic/graph oracle for authored proposal examples, not a runtime.

The journal totals are checked against independent closing-balance equations.
Source checks establish retained bytes/locators, not accounting applicability.
"""
from collections import defaultdict, deque
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
START = time.monotonic()
checks = []
inputs = {}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    path = ROOT / name
    inputs[name] = digest(path)
    return json.loads(path.read_text())


def check(name, actual, expected):
    checks.append(dict(id=name, passed=actual == expected,
                       actual=actual, expected=expected))


def net(lines):
    balances = defaultdict(F)
    for account, debit, credit in lines:
        if F(debit) < 0 or F(credit) < 0 or (F(debit) and F(credit)):
            raise ValueError('Invalid journal leg: ' + repr((account, debit, credit)))
        balances[account] += F(debit) - F(credit)
    return balances


def balanced(name, lines):
    check(name + ' journal balance', sum(net(lines).values(), F()), F())


standards = read('docs/design/proposal/methods/standards-fixtures-v1.json')
extraction = read('docs/design/proposal/architecture/extraction-fixtures-v1.json')
sources = read('docs/design/proposal/methods/standards-source-register-v1.json')

for c in standards['acquisitions']:
    if c['id'] == 'A03':
        check('A03 unresolved observable valuation',
              (c['observable_valuation_evidence'], c['expected'], c['journal']),
              (None, 'TREATMENT_UNRESOLVED', []))
        continue
    asset = F(c['fair_value']) + (F(c['cost']) if c['category'] == 'amortised_cost' else 0)
    expense = F(c['cost']) if c['category'] == 'FVTPL' else F()
    b = net(c['journal'])
    check(c['id'] + ' independent asset/expense/cash',
          [b['asset'], b['expense'], b['cash']],
          [asset, expense, -F(c['price']) - F(c['cost'])])
    balanced(c['id'], c['journal'])

for c in standards['interest']:
    rate, years, factor = (F(c[k]) for k in ('annual_effective_rate', 'years', 'exact_factor'))
    check(c['id'] + ' positive-base factor identity',
          factor > 0 and factor ** years.denominator == (1 + rate) ** years.numerator, True)
    interest = F(c['opening']) * (factor - 1)
    check(c['id'] + ' interest and closing', [interest, F(c['opening']) + interest - F(c['end_cash_flow'])],
          [F(c['interest']), F(c['closing'])])
    b = net(c['journal'])
    check(c['id'] + ' accrual journal', [b['asset'], b['interest_revenue']], [interest, -interest])
    balanced(c['id'], c['journal'])
check('inconsistent simple interest negative control', F(100) * F(21, 100) * F(1, 2) - 10, F(1, 2))

for c in standards['credit_impaired']:
    if c['kind'] == 'poci':
        base, kind = F(c['amortised_cost']), 'credit_adjusted_eir'
    else:
        base, kind = F(c['gross']) - F(c['allowance']), 'applicable_eir'
    check(c['id'] + ' stated rate/base arithmetic',
          [kind, base * F(c['rate'])], [c['rate_kind'], F(c['expected_interest'])])

for c in standards['revenue_sequences']:
    cumulative = dict(revenue=F(), billing=F(), collection=F())
    all_lines = []
    for index, event in enumerate(c['events']):
        cumulative[event['kind']] = F(event['cumulative'])
        r, b, p = (cumulative[k] for k in ('revenue', 'billing', 'collection'))
        check(f'{c["id"]}/{index} within stated facts', 0 <= r <= 100 and 0 <= p <= b <= 100, True)
        balanced(f'{c["id"]}/{index}', event['journal'])
        all_lines.extend(event['journal'])
        posted = net(all_lines)
        # Derive balances from cumulative facts, independently of event posting rules.
        actual = [posted['receivable'], posted['contract_asset'], -posted['contract_liability'],
                  -posted['revenue'], posted['cash']]
        expected = [b - p, max(r - b, 0), max(b - r, 0), r, p]
        check(f'{c["id"]}/{index} independent closing balances', actual, expected)
    check(c['id'] + ' saved final balances',
          {k: -posted[k] if k in {'revenue', 'contract_liability'} else posted[k] for k in c['expected']},
          {k: F(v) for k, v in c['expected'].items()})
failure = standards['revenue_scope_failure']
check('R04 collection exceeds unpaid billing', F(failure['requested_collection_increment']) >
      F(failure['cumulative_billings']) - F(failure['cumulative_collections']), True)
check('R04 specified rejection without posting',
      [failure['expected'], failure['journal'], failure['state_changed']],
      ['OUTSIDE_EXAMPLE_SCOPE', [], False])

prior = F()
cost_lines = []
for c in standards['cost_sequence']['events']:
    cumulative = F(c['cumulative_cost'])
    delta = cumulative - prior
    b = net(c['journal'])
    check(c['id'] + ' incremental cost',
          [F(c['expected_delta']), b['cost_expense'], -b['service_payable']], [delta] * 3)
    balanced(c['id'], c['journal'])
    cost_lines.extend(c['journal'])
    prior = cumulative
check('cumulative expense is not summed snapshots', net(cost_lines)['cost_expense'],
      F(standards['cost_sequence']['expected_total_expense']))

for c in standards['receipt_cases']:
    before = deepcopy(c)
    if c['saved_event'] == c['request_event']:
        decision = 'RETURN_ORIGINAL_RECEIPT' if c['saved_payload'] == c['request_payload'] else 'EVENT_ID_CONFLICT'
    elif c['request_payload']['opening_version'] != c['current_version']:
        decision = 'STALE_OPENING_STATE'
    else:
        decision = 'NEW_REQUEST'
    check(c['id'] + ' specified receipt decision', decision, c['expected'])
    check(c['id'] + ' no additional posting specified',
          [F(c['additional_expense']), c['state_changed'], c == before], [F(), False, True])

for c in standards['negative_controls']:
    imbalance = sum(net(c['journal']).values(), F())
    check(c['id'] + ' exposes defect', imbalance, F(c['expected_debits_minus_credits']))
    check(c['id'] + ' does not balance', imbalance != 0, True)

x1, x2 = extraction['identity_cases']
left, right = x1['readings']
check('X01 equal numbers distinct context',
      left['value'] == right['value'] and any(left[k] != right[k] for k in ('basis', 'perimeter', 'vintage')), True)
check('X01 preserve assertions', [x1['expected_occurrences'], x1['expected_assertions'], x1['semantic_equivalence']], [2, 2, False])
check('X02 explicit alias retains occurrences',
      [len(set(x2['occurrences'])), x2['expected_assertions'], x2['independent_information_items'], bool(x2['equivalence_evidence'])],
      [2, 1, 1, True])
c = extraction['context_correction']
check('X03 correction can preserve number',
      c['old']['value'] == c['new']['value'] and c['old']['period'] != c['new']['period']
      and c['new']['supersedes'] == c['old']['id'] and c['source_changed'] is False, True)
c = extraction['time_case']
possession = c['byte_receipt_verified'] and datetime.fromisoformat(c['ingestion_receipt']) <= datetime.fromisoformat(c['system_as_of'])
check('X04 possession without invented public time', [c['publication'], possession], [None, True])
check('X04 separate claim outcomes', c['expected'], dict(archival='AVAILABLE_WITH_HISTORICAL_ADMISSIBILITY_UNESTABLISHED',
      system_as_of='POSSESSION_SUPPORTED', investor_information='UNRESOLVED_PUBLIC_AVAILABILITY'))


def reachable(edges, start, goal):
    todo, seen = [start], set()
    while todo:
        node = todo.pop()
        if node == goal:
            return True
        if node not in seen:
            seen.add(node)
            todo.extend(b for a, b in edges if a == node)
    return False


for c in extraction['traversal_cases']:
    before = deepcopy(c)
    expanded = list(c.get('resume_expanded', []))
    queue = deque(c.get('resume_frontier', c['roots']))
    edges = [row[:2] for row in c.get('resume_edges', [])]
    remaining = c['max_expansions']
    while queue and remaining:
        node = queue.popleft()
        if node in expanded:
            continue
        expanded.append(node)
        remaining -= 1
        for target in c['graph'][node]:
            edges.append([node, target])
            if target not in expanded and target not in queue:
                queue.append(target)
    known = set(c['roots'])
    discovered, dispositions = [], []
    for source, target in edges:
        kind = 'cycle_closed' if reachable(discovered, target, source) else (
            'duplicate_verified' if target in known else 'resolved')
        if target not in expanded:
            kind = 'resource_exhausted'
        dispositions.append([source, target, kind])
        discovered.append([source, target])
        known.add(target)
    check(c['id'] + ' complete specified traversal state',
          [expanded, list(queue), dispositions, bool(queue)],
          [c['expected_expanded'], c['expected_frontier'], c['expected_edges'], c['expected_unknown_extent']])
    check(c['id'] + ' original receipt preserved and closure unclaimed', [c == before, c['claim_package_closed']], [True, False])

c = extraction['source_support']
check('X08 location does not establish reading',
      [c['locator_resolves'], F(c['source_numeric_reading']) != F(c['proposed_numeric_reading']), c['accepted'], c['proposal_retained']],
      [True, True, False, True])
c = extraction['infeasibility']
check('X09 retain competing explanations', set(c['remaining_explanations']),
      {'extraction', 'source_conflict', 'mapping', 'model_scope', 'assumption'})
check('X09 no source alteration', c['automatic_source_edit'], False)
c = extraction['rounding_overlap']
check('X10 overlap exists without identity evidence',
      [max(F(c['left_interval'][0]), F(c['right_interval'][0])) <= min(F(c['left_interval'][1]), F(c['right_interval'][1])),
       c['same_assertion_evidence'], c['semantic_equivalence']], [True, None, False])

for source in sources['sources']:
    for kind in ('pdf', 'text'):
        ref = source[kind]
        actual = digest(ROOT / ref['path'])
        inputs[ref['path']] = actual
        check(source['id'] + ' ' + kind + ' retained bytes', actual, ref['sha256'])
    text = (ROOT / source['text']['path']).read_text()
    lines = text.split('\n')
    for anchor in source['inspected']:
        index = anchor['text_line'] - 1
        line = lines[index].lstrip('\f').strip()
        label = anchor['paragraph']
        token = ('This compiled Standard applies' if label == 'cover' else
                 'Comparison with IFRS' if label == 'IFRS comparison' else
                 '(b)' if label == '5.4.1(b)' else label.split('–')[0].split('(')[0])
        page = 1 + '\n'.join(lines[:index + 1]).count('\f')
        check(source['id'] + '/' + label + ' retained locator', [line.startswith(token), page],
              [True, anchor['physical_pdf_page']])
    period = standards['case_context']['annual_period_start']
    window = source['application_window']
    check(source['id'] + ' illustrative period within stated compilation',
          window['annual_period_start_inclusive'] <= period < window['annual_period_start_exclusive'], True)

baseline = read('data/accounting-master/claude-adoption-20261005/baseline.json')
changed = [name for name, sha in baseline['external_sources'].items() if digest(ROOT / name) != sha]
check('all original Claude review files retained', changed, [])
for name in ('docs/design/proposal/architecture/extraction-contract-v1.md',
             'docs/design/proposal/methods/standards-mapping-v1.md',
             'docs/plans/accounting-claude-adoption-plan-20261005.md',
             'docs/design/proposal/architecture/evidence-contract-v3.md',
             'docs/design/proposal/architecture/time-contract-v2.md'):
    inputs[name] = digest(ROOT / name)
inputs[str(Path(__file__).resolve().relative_to(ROOT))] = digest(Path(__file__))
git = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, capture_output=True)
report = dict(
    schema_version='accdsl.claude_adoption.diagnostic.v1',
    question='Do the repaired illustrative journals, identity and traversal examples match their stated semantics?',
    passed=all(c['passed'] for c in checks), tests=len(checks), checks=checks, inputs=inputs,
    scope='Deterministic specification oracle only; no product accounting/extraction/persistence implementation tested.',
    source_boundary='Hashes and locators checked automatically; source applicability and deductions inspected separately.',
    manifest=dict(command='python3 ' + str(Path(__file__).resolve()), git_commit=git.stdout.strip() if git.returncode == 0 else 'unavailable',
        working_tree='dirty; exact diagnostic inputs pinned above', environment=platform.python_implementation() + ' ' + platform.python_version(),
        cpu_gpu='CPU standard library only; no GPU/framework import or device detection', seeds='N/A: deterministic',
        data_version=standards['schema_version'] + '; ' + extraction['schema_version'],
        plan='docs/plans/accounting-claude-adoption-plan-20261005.md',
        result=str((OUT / 'diagnostics.json').relative_to(ROOT)),
        finished_at=datetime.now(timezone.utc).isoformat(), wall_seconds=time.monotonic() - START))
def encode(value):
    return sorted(value) if isinstance(value, set) else str(value)
(OUT / 'diagnostics.json').write_text(json.dumps(report, indent=2, ensure_ascii=False, default=encode) + '\n')
print(json.dumps(dict(passed=report['passed'], checks=len(checks), failures=[c['id'] for c in checks if not c['passed']],
                     report=report['manifest']['result'])))
sys.exit(0 if report['passed'] else 1)
