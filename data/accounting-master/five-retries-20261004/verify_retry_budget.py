"""Exercise configured retry boundaries in disposable roots, without model calls."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tests'))
from test_accounting_master import MasterTests, response
from accounting_master_support import atomic_json
from run_accounting_master import ACCEPTED, CATALOG


def exercise(kind, succeeds):
    case = MasterTests(methodName='runTest')
    case.setUp()
    try:
        limit = json.loads((ROOT / CATALOG).read_text())['limits']['max_repairs']
        assert limit == 5, limit
        case.catalog['limits']['max_repairs'] = limit
        atomic_json(case.root / CATALOG, case.catalog)
        executions = []
        plan_reviews = []

        def worker(role, phase, packet, folder, attempt):
            if role == 'review_plan':
                plan_reviews.append(attempt)
                if kind == 'planning' and (not succeeds or attempt < limit):
                    return response('REVISE', issues=['Injected unresolved plan finding'])
            if role in {'implement', 'repair'}:
                executions.append(attempt)
                repaired = kind == 'planning' or (succeeds and attempt == limit)
                return response('IMPLEMENTED', evidence=case.write_work(
                    phase, 'repaired' if repaired else 'broken'))
            return case.worker(role, phase, packet, folder, attempt)

        master = case.master(worker=worker)
        outcome = case.run_quiet(master, max_phases=1)
        state = master.state['phases']['P00']['status']
        if kind == 'execution':
            assert executions == list(range(6)), executions
            assert state == (ACCEPTED if succeeds else 'needs_repair'), state
        else:
            assert plan_reviews == list(range(6)), plan_reviews
            assert executions == ([0] if succeeds else []), executions
            assert state == (ACCEPTED if succeeds else 'needs_plan_repair'), state
        assert master.state['phases']['P01']['status'] == 'pending'
        return {'kind': kind, 'success_on_fifth_retry': succeeds,
                'execution_attempts': executions, 'plan_review_attempts': plan_reviews,
                'phase_status': state, 'run_outcome': outcome, 'passed': True}
    finally:
        case.doCleanups()


if __name__ == '__main__':
    results = [exercise(kind, success) for kind in ('execution', 'planning')
               for success in (True, False)]
    output = {'scope': 'Deterministic controller fault injection in temporary roots; no API calls.',
              'passed': all(r['passed'] for r in results), 'cases': results}
    atomic_json(Path(__file__).with_name('retry-boundary-checks.json'), output)
    print(json.dumps(output, indent=2))
