#!/usr/bin/env python3
"""Read an accounting worker's remaining host-monotonic budget without edits."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import time


def worker_budget(seconds, boot_id, *, editable=False, latest_deadline=float('inf')):
    if not boot_id or not math.isfinite(seconds) or seconds <= 0:
        raise ValueError('A positive worker allowance and current boot identity are required')
    started = time.monotonic()
    # Keep the full admission requirement. End editable work earlier so the
    # response cutoff is separate from the nominal worker allowance.
    margin = min(60, seconds / 15) if editable else 0
    finishing = min(240, seconds * 4 / 15) if editable else min(120, seconds / 5)
    responding = min(60, seconds / 15) if editable else min(30, seconds / 10)
    nominal_deadline = min(started + seconds, latest_deadline)
    deadline = nominal_deadline - margin
    return {
        'schema_version': 'accdsl.worker-budget.v1', 'clock': 'time.monotonic',
        'boot_id': boot_id, 'started_monotonic': started,
        'nominal_deadline_monotonic': nominal_deadline,
        'save_check_deadline_monotonic': deadline - finishing,
        'response_start_monotonic': deadline - responding,
        'deadline_monotonic': deadline, 'worker_limit_seconds': seconds,
        'exit_margin_seconds': margin,
        'reserve_for_checks_and_response_seconds': finishing,
    }


def budget_status(budget, *, boot_id, instant=None):
    if (budget.get('schema_version') != 'accdsl.worker-budget.v1'
            or budget.get('clock') != 'time.monotonic'
            or not boot_id or budget.get('boot_id') != boot_id):
        raise ValueError('Worker budget has an invalid clock or different host boot; no time estimate is usable')
    names = ('started_monotonic', 'save_check_deadline_monotonic',
             'response_start_monotonic', 'deadline_monotonic', 'nominal_deadline_monotonic')
    bounds = [budget.get(name) for name in names]
    if (any(type(x) not in (int, float) or not math.isfinite(x) for x in bounds)
            or bounds != sorted(bounds) or bounds[0] >= bounds[-1]):
        raise ValueError('Invalid monotonic worker deadline ordering')
    current = time.monotonic() if instant is None else instant
    if not math.isfinite(current) or current < bounds[0]:
        raise ValueError('Worker clock predates this budget; no time estimate is usable')
    started, finish, respond, deadline, _ = bounds
    stage = ('expired' if current >= deadline else 'respond' if current >= respond
             else 'finish' if current >= finish else 'work')
    instructions = {
        'work': 'Work on one bounded subsection; save it before starting another.',
        'finish': 'Stop new research and drafting. Save current work, run bounded checks, update progress, then respond.',
        'respond': 'Return the structured response now. Use PARTIAL with exact next_actions for incomplete phase work.',
        'expired': 'The response cutoff has passed. Saved files do not establish a completed worker response.',
    }
    return {'clock': 'time.monotonic', 'stage': stage,
            'elapsed_seconds': round(current - started, 3),
            'remaining_seconds': round(max(0, deadline - current), 3),
            'seconds_to_save_and_check': round(max(0, finish - current), 3),
            'seconds_to_response': round(max(0, respond - current), 3),
            'instruction': instructions[stage]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('budget_file', type=Path)
    args = parser.parse_args()
    try:
        budget = json.loads(args.budget_file.read_text())
        boot_id = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        if not isinstance(budget, dict):
            raise ValueError('Worker budget must be an object')
        print(json.dumps(budget_status(budget, boot_id=boot_id)))
    except (OSError, ValueError) as error:
        parser.exit(2, str(error) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
