#!/usr/bin/env python3
"""Read a worker budget and report concrete progress without writing any files."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import time

from accounting_master_support import digest, load_json, local_path
from accounting_worker_supervision import (CLOCK_SCHEMA, CONTROL_SCHEMA, PROGRESS_SCHEMA,
                                           MAX_RECORD_BYTES, scoped_inventory, inventory_hash)


def worker_budget(seconds, boot_id, *, editable=False, latest_deadline=float('inf'),
                  monitored=False):
    if not boot_id or not math.isfinite(seconds) or seconds <= 0:
        raise ValueError('A positive worker allowance and current boot identity are required')
    started = time.monotonic()
    nominal_deadline = min(started + seconds, latest_deadline)
    if monitored:
        # Real workers use the same policy; only short fault-injection windows
        # scale it. A read-only review gets the same five-minute observation
        # interval as an editable worker, despite its shorter nominal budget.
        scale = seconds / 900 if seconds < 180 else 1
        policy = {'poll_seconds': min(1, seconds / 50),
                  'stagnation_seconds': 300 * scale, 'grace_seconds': 180 * scale,
                  'finish_seconds': 180 * scale, 'respond_seconds': 60 * scale,
                  'grant_seconds': 120 * scale, 'maximum_extension_seconds': 300 * scale}
        return {'schema_version': 'accdsl.worker-budget.v2', 'clock': 'time.monotonic',
                'boot_id': boot_id, 'started_monotonic': started,
                'nominal_deadline_monotonic': nominal_deadline,
                'save_check_deadline_monotonic': nominal_deadline - policy['finish_seconds'],
                'response_start_monotonic': nominal_deadline - policy['respond_seconds'],
                'deadline_monotonic': min(nominal_deadline + policy['maximum_extension_seconds'], latest_deadline),
                'worker_limit_seconds': seconds, 'exit_margin_seconds': 0,
                'reserve_for_checks_and_response_seconds': policy['finish_seconds'],
                'supervision_policy': policy}
    # Historical callers and packet-only probes retain their original clock.
    margin = min(60, seconds / 15) if editable else 0
    finishing = min(240, seconds * 4 / 15) if editable else min(120, seconds / 5)
    responding = min(60, seconds / 15) if editable else min(30, seconds / 10)
    deadline = nominal_deadline - margin
    return {'schema_version': 'accdsl.worker-budget.v1', 'clock': 'time.monotonic',
            'boot_id': boot_id, 'started_monotonic': started,
            'nominal_deadline_monotonic': nominal_deadline,
            'save_check_deadline_monotonic': deadline - finishing,
            'response_start_monotonic': deadline - responding,
            'deadline_monotonic': deadline, 'worker_limit_seconds': seconds,
            'exit_margin_seconds': margin,
            'reserve_for_checks_and_response_seconds': finishing}


def budget_status(budget, *, boot_id, instant=None):
    version = budget.get('schema_version')
    if (version not in {'accdsl.worker-budget.v1', 'accdsl.worker-budget.v2'}
            or budget.get('clock') != 'time.monotonic'
            or not boot_id or budget.get('boot_id') != boot_id):
        raise ValueError('Worker budget has an invalid clock or different host boot; no time estimate is usable')
    names = ['started_monotonic', 'save_check_deadline_monotonic', 'response_start_monotonic']
    names += (['nominal_deadline_monotonic', 'deadline_monotonic'] if version.endswith('v2') else
              ['deadline_monotonic', 'nominal_deadline_monotonic'])
    bounds = [budget.get(name) for name in names]
    if (any(type(x) not in (int, float) or not math.isfinite(x) for x in bounds)
            or bounds != sorted(bounds) or bounds[0] >= bounds[-1]):
        raise ValueError('Invalid monotonic worker deadline ordering')
    current = time.monotonic() if instant is None else instant
    if not math.isfinite(current) or current < bounds[0]:
        raise ValueError('Worker clock predates this budget; no time estimate is usable')
    started, finish, respond = bounds[:3]
    deadline = budget['deadline_monotonic']
    control = None
    if version.endswith('v2'):
        deadline = budget['nominal_deadline_monotonic']
        if budget.get('control_file'):
            control = load_json(local_path(Path(budget['root_directory']), budget['control_file']))
            if (not isinstance(control, dict) or control.get('schema_version') != CONTROL_SCHEMA
                    or control.get('worker_id') != budget.get('worker_id')
                    or type(control.get('sequence')) is not int or control['sequence'] < 0
                    or control.get('stage') not in {'work', 'checkpoint', 'finish', 'respond'}):
                raise ValueError('Invalid worker control record')
            deadline = control.get('effective_deadline_monotonic')
            if (type(deadline) not in (int, float) or not math.isfinite(deadline)
                    or not bounds[3] <= deadline <= bounds[4]):
                raise ValueError('Worker control deadline is outside its immutable budget')
    stage = ('expired' if current >= deadline else 'respond' if current >= respond
             else 'finish' if current >= finish else 'work')
    if control and stage != 'expired':
        if control['stage'] == 'checkpoint':
            stage = 'checkpoint'
        elif control['stage'] in {'finish', 'respond'}:
            stage = control['stage']
    instructions = {
        'work': 'Work on one bounded subsection; report concrete progress and save before starting another.',
        'checkpoint': 'Report new concrete progress or save a PARTIAL checkpoint and return now. Clock acknowledgement alone does not resolve stagnation.',
        'finish': 'Stop new research and drafting. Save current work, run bounded checks, save a PARTIAL checkpoint if editable, then respond.',
        'respond': 'Return the structured response now. Use PARTIAL with exact next_actions for incomplete phase work.',
        'expired': 'The worker window has ended. Saved files alone do not establish a completed response.',
    }
    result = {'clock': 'time.monotonic', 'stage': stage,
              'elapsed_seconds': round(current - started, 3),
              'remaining_seconds': round(max(0, deadline - current), 3),
              'seconds_to_save_and_check': round(max(0, finish - current), 3),
              'seconds_to_response': round(max(0, respond - current), 3),
              'instruction': instructions[stage]}
    if version.endswith('v2'):
        result.update(schema_version=CLOCK_SCHEMA, worker_id=budget.get('worker_id'),
                      reported_monotonic=current,
                      supervision_ack_sequence=control['sequence'] if control else 0,
                      supervision_reason=control['reason'] if control else 'initial',
                      ack_deadline_monotonic=control.get('ack_deadline_monotonic') if control else None,
                      hard_remaining_seconds=round(max(0, bounds[4] - current), 3))
    return result


def progress_report(budget, status, *, kind, summary, next_action, evidence,
                    locator='', checkpoint=None):
    if budget.get('schema_version') != 'accdsl.worker-budget.v2' or not budget.get('worker_id'):
        raise ValueError('Progress reports require a bound monitored budget')
    root = Path(budget['root_directory'])
    values = [{'path': name, 'sha256': digest(local_path(root, name)), 'locator': locator} for name in evidence]
    result = {**status, 'schema_version': PROGRESS_SCHEMA, 'sequence': time.monotonic_ns(),
              'kind': kind, 'summary': summary, 'next_action': next_action, 'evidence': values}
    if checkpoint is not None:
        result['checkpoint_response'] = checkpoint
        result['scoped_sha256'] = inventory_hash(scoped_inventory(root, budget['write_scope']))
        result['checkpoint_evidence'] = {name: digest(local_path(root, name)) for name in checkpoint['evidence']}
    if len(json.dumps(result).encode()) > MAX_RECORD_BYTES // 2:
        raise ValueError('Progress report exceeds bounded channel size')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('budget_file', type=Path)
    parser.add_argument('--kind', choices=['milestone', 'finding', 'checkpoint'])
    parser.add_argument('--summary', default='')
    parser.add_argument('--next-action', default='')
    parser.add_argument('--evidence', nargs='+', default=[])
    parser.add_argument('--locator', default='')
    parser.add_argument('--checkpoint-json', help='Complete PARTIAL response JSON; printed to supervisor, never written by helper')
    args = parser.parse_args()
    try:
        budget = load_json(args.budget_file)
        boot_id = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        if not isinstance(budget, dict):
            raise ValueError('Worker budget must be an object')
        status = budget_status(budget, boot_id=boot_id)
        if args.kind:
            if not args.summary.strip() or not args.next_action.strip() or not args.evidence:
                raise ValueError('Report requires --summary, --next-action and --evidence')
            checkpoint = json.loads(args.checkpoint_json) if args.checkpoint_json else None
            if args.kind == 'checkpoint' and (not isinstance(checkpoint, dict) or checkpoint.get('verdict') != 'PARTIAL'):
                raise ValueError('Checkpoint requires a complete PARTIAL response via --checkpoint-json')
            if args.kind != 'checkpoint' and checkpoint is not None:
                raise ValueError('Only checkpoint reports accept a checkpoint response')
            status = progress_report(budget, status, kind=args.kind, summary=args.summary,
                                     next_action=args.next_action, evidence=args.evidence,
                                     locator=args.locator, checkpoint=checkpoint)
        print(json.dumps(status, ensure_ascii=False))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, str(error) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
