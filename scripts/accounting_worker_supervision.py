#!/usr/bin/env python3
"""Cooperative progress supervision; scheduling evidence never accepts work."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import time

from accounting_master_support import digest, load_json, local_path

PROGRESS_SCHEMA = 'accdsl.worker-progress.v1'
CONTROL_SCHEMA = 'accdsl.worker-control.v1'
CLOCK_SCHEMA = 'accdsl.worker-clock.v2'
MAX_RECORD_BYTES = 1024 * 1024


def inventory_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def in_scope(name, scope):
    return any(name.startswith(s) if s.endswith('/') else name == s for s in scope)


def scoped_inventory(root, scope):
    """Include new/deleted files and all file types in the declared write scope."""
    result = {}
    for name in scope:
        base = local_path(root, name.rstrip('/'))
        paths = base.rglob('*') if base.is_dir() else [base]
        for path in paths:
            if path.is_symlink():
                raise ValueError('Scoped symlink cannot be checkpointed: ' + str(path))
            if path.is_file():
                result[str(path.relative_to(root))] = digest(path)
    return result


def substantive(name):
    path = Path(name)
    if name.startswith('data/accounting-master/') and not name.startswith('data/accounting-master/deliverables/'):
        return False
    return (path.name != 'progress.md' and not path.name.endswith(('.log', '.jsonl', '.budget.json',
            '.supervision.json', '.checkpoint.json', '.process.json', '.control.json')))


def readonly_support(root, name):
    """Context may accompany a located source; it never supplies novelty."""
    if Path(name).name == 'progress.md':
        return (not name.startswith('data/accounting-master/')
                or name.startswith('data/accounting-master/deliverables/'))
    match = re.fullmatch(
        r'data/accounting-master/runs/[0-9]{8}T[0-9]{6}-[0-9a-f]{8}/'
        r'(P[0-9]{2})/(?:preflight|execution-[0-9]+)/checks\.checker\.json', name)
    if not match:
        return False
    path = local_path(root, name)
    if path.stat().st_size > MAX_RECORD_BYTES:
        return False
    record = load_json(path)
    # Both passing and failing checks can explain a finding. This only admits
    # structured proposal-check context, not the checker as phase acceptance.
    return (isinstance(record, dict)
            and record.get('schema_version') == 'accdsl.proposal.check.v1'
            and record.get('phase') == match[1]
            and type(record.get('passed')) is bool
            and isinstance(record.get('checks'), list) and bool(record['checks'])
            and all(isinstance(row, dict) and isinstance(row.get('id'), str)
                    and row['id'].strip() and type(row.get('passed')) is bool
                    for row in record['checks'])
            and type(record.get('tests')) is int and record['tests'] == len(record['checks'])
            and isinstance(record.get('errors'), list)
            and all(isinstance(error, str) for error in record['errors']))


class ProgressMonitor:
    """One worker, one monotonic budget, incremental completed-tool events.

    The worker reads supervisor instructions with its clock helper. A blocked
    provider call cannot receive them until it returns. Silence is therefore a
    bounded operational stop, never a conclusion about the proposal's quality.
    """

    def __init__(self, *, root, log, budget, before_inventory, publish_control,
                 publish_record, save_checkpoint, clock=None):
        self.root, self.log, self.budget = root, log, budget
        self.clock = clock or time.monotonic
        self.publish_control = publish_control
        self.publish_record = publish_record
        self.save_checkpoint = save_checkpoint
        self.worker_id = budget['worker_id']
        self.soft_deadline = budget['nominal_deadline_monotonic']
        self.hard_deadline = budget['deadline_monotonic']
        self.deadline = self.soft_deadline
        self.policy = budget['supervision_policy']
        self.started = budget['started_monotonic']
        self.last_progress = self.started
        self.last_report_sequence = 0
        self.ack = 0
        self.progress_count = 0
        self.last_grant_count = 0
        self.seen_hashes = set(before_inventory.values())
        self.seen_findings = set()
        self.events = []
        self.checkpoint = None
        self.offset = 0
        self.partial = b''
        self.discard_line = False
        self.last_poll = float('-inf')
        self.stop_reason = None
        self.control = {'schema_version': CONTROL_SCHEMA, 'worker_id': self.worker_id,
                        'sequence': 0, 'stage': 'work', 'reason': 'worker_started',
                        'requested_monotonic': self.started, 'ack_deadline_monotonic': None,
                        'effective_deadline_monotonic': self.deadline}
        self.publish_control(self.control)
        self.publish_record(self.summary())

    def effective_deadline(self):
        if self.control['stage'] == 'checkpoint':
            return min(self.deadline, self.control['ack_deadline_monotonic'])
        return self.deadline

    def _event(self, kind, instant, **fields):
        self.events.append({'kind': kind, 'monotonic': instant, **fields})
        self.events = self.events[-128:]

    def _issue(self, stage, reason, instant):
        self.control = {**self.control, 'sequence': self.control['sequence'] + 1,
                        'stage': stage, 'reason': reason, 'requested_monotonic': instant,
                        'ack_deadline_monotonic': (min(self.deadline, instant + self.policy['grace_seconds'])
                                                  if stage != 'work' else None),
                        'effective_deadline_monotonic': self.deadline}
        self.publish_control(self.control)
        self._event('instruction', instant, stage=stage, reason=reason, sequence=self.control['sequence'])

    def _acknowledge(self, value, instant):
        sequence = value.get('supervision_ack_sequence')
        ack_deadline = self.control['ack_deadline_monotonic']
        reported = value['reported_monotonic']
        if (type(sequence) is int and self.ack < sequence == self.control['sequence']
                and reported >= self.control['requested_monotonic']
                and (ack_deadline is None or reported <= ack_deadline)):
            self.ack = sequence
            self._event('acknowledgement', instant, sequence=sequence)

    def _report(self, value, instant):
        sequence = value.get('sequence')
        if type(sequence) is not int or sequence <= self.last_report_sequence:
            return
        self.last_report_sequence = sequence
        kind = value.get('kind')
        editable = self.budget['role'] in {'implement', 'repair'}
        if kind not in ({'milestone', 'checkpoint'} if editable else {'finding'}):
            raise ValueError('Report kind does not match worker role')
        for key in ('summary', 'next_action'):
            if not isinstance(value.get(key), str) or not value[key].strip() or len(value[key]) > 2000:
                raise ValueError('Report needs a bounded concrete ' + key)
        evidence = value.get('evidence')
        if not isinstance(evidence, list) or not 1 <= len(evidence) <= 32:
            raise ValueError('Report requires 1 to 32 concrete evidence files')
        checked, supporting, located = {}, {}, set()
        for item in evidence:
            if not isinstance(item, dict) or set(item) != {'path', 'sha256', 'locator'}:
                raise ValueError('Invalid progress evidence entry')
            name = item['path']
            path = local_path(self.root, name)
            if (name != str(path.relative_to(self.root))
                    or not path.is_file() or digest(path) != item['sha256']):
                raise ValueError('Missing, operational or changed progress evidence: ' + name)
            if not isinstance(item['locator'], str) or len(item['locator']) > 1000:
                raise ValueError('Invalid evidence locator')
            if editable and not in_scope(name, self.budget['write_scope']):
                raise ValueError('Saved progress is outside the phase write scope')
            if not editable and not item['locator'].strip():
                raise ValueError('A read-only finding needs a source locator')
            if substantive(name):
                checked[name] = item['sha256']
                located.add((name, item['sha256'], item['locator']))
            elif not editable and readonly_support(self.root, name):
                supporting[name] = item['sha256']
            else:
                raise ValueError('Operational or unsupported progress evidence: ' + name)
        if not checked:
            raise ValueError('A finding requires substantive evidence; supporting context alone is not progress')
        if editable:
            novel = bool(set(checked.values()) - self.seen_hashes)
        else:
            # Changing context, check output or the next action cannot turn an
            # old source-backed conclusion into progress.
            fingerprint = (' '.join(value['summary'].lower().split()),
                           tuple(sorted(located)))
            novel = fingerprint not in self.seen_findings
            self.seen_findings.add(fingerprint)
        if kind == 'checkpoint':
            self.checkpoint = self.save_checkpoint(value)
            self._event('checkpoint_saved', instant, path=self.checkpoint)
        self.seen_hashes.update(checked.values())
        if not novel:
            self._event('repeated_report', instant, summary=value['summary'])
            return
        self.last_progress = value['reported_monotonic']
        self.progress_count += 1
        self._event('verified_progress', instant, summary=value['summary'], evidence=checked,
                    supporting_evidence=supporting)
        if (self.control['stage'] == 'checkpoint' and self.ack == self.control['sequence']
                and self.last_progress >= self.control['requested_monotonic']):
            self._issue('work', 'new_verified_progress', instant)

    def _consume(self, value, instant):
        if (not isinstance(value, dict) or value.get('worker_id') != self.worker_id
                or value.get('schema_version') not in {PROGRESS_SCHEMA, CLOCK_SCHEMA}):
            return
        reported = value.get('reported_monotonic')
        if (type(reported) not in (int, float) or not self.started <= reported <= instant
                or instant - reported > self.policy['grace_seconds']
                or reported > self.effective_deadline()):
            self._event('invalid_report', instant, reason='stale or invalid report clock')
            return
        self._acknowledge(value, instant)
        if value['schema_version'] == PROGRESS_SCHEMA:
            try:
                self._report(value, instant)
            except (OSError, ValueError, KeyError, TypeError) as error:
                self._event('invalid_report', instant, reason=str(error)[:500])

    def _read(self, instant):
        if not self.log.exists():
            return
        # Read only appended bytes. Do not recursively parse prompts, messages,
        # failed commands or arbitrary strings as if they were helper output.
        with self.log.open('rb') as stream:
            stream.seek(self.offset)
            chunk = stream.read(MAX_RECORD_BYTES)
            self.offset += len(chunk)
        lines = (self.partial + chunk).split(b'\n')
        self.partial = lines.pop()
        for raw in lines:
            if self.discard_line:
                self.discard_line = False
                continue
            if len(raw) > MAX_RECORD_BYTES:
                continue
            try:
                event = json.loads(raw)
                item = event.get('item', {})
                if (event.get('type') != 'item.completed' or item.get('type') != 'command_execution'
                        or item.get('exit_code') != 0):
                    continue
                output = item.get('aggregated_output', '')
                if not isinstance(output, str) or len(output) > MAX_RECORD_BYTES:
                    continue
                for line in output.splitlines():
                    try:
                        value = json.loads(line)
                    except ValueError:
                        continue
                    self._consume(value, instant)
            except (ValueError, AttributeError, TypeError):
                continue
        if len(self.partial) > MAX_RECORD_BYTES:
            self.partial = b''
            self.discard_line = True

    def poll(self, instant=None, *, force=False):
        current = self.clock() if instant is None else instant
        if not force and current - self.last_poll < self.policy['poll_seconds']:
            return self.stop_reason
        self.last_poll = current
        before = self.summary()
        self._read(current)
        stage = self.control['stage']
        ack_deadline = self.control['ack_deadline_monotonic']
        if current >= self.hard_deadline:
            self.stop_reason = 'timeout'
        elif ack_deadline is not None and current >= ack_deadline and self.ack < self.control['sequence']:
            self.stop_reason = 'progress_no_ack'
        elif stage == 'checkpoint' and current >= ack_deadline:
            self.stop_reason = 'progress_stagnation'
        else:
            # The worker must acknowledge instructions and have new recent
            # evidence for each grant. Extensions only buy time to finish.
            if (current >= self.deadline - self.policy['respond_seconds'] / 2
                    and self.progress_count > self.last_grant_count
                    and current - self.last_progress < self.policy['grace_seconds']
                    and self.ack == self.control['sequence'] and stage != 'checkpoint'
                    and self.deadline < self.hard_deadline):
                self.deadline = min(self.hard_deadline, self.deadline + self.policy['grant_seconds'])
                self.last_grant_count = self.progress_count
                self._issue('respond', 'verified_progress_finishing_extension', current)
            if current >= self.deadline:
                self.stop_reason = 'progress_finish_timeout'
            elif (self.control['stage'] == 'work'
                  and current - self.last_progress >= self.policy['stagnation_seconds']):
                self._issue('checkpoint', 'no_recent_verified_progress', current)
            elif (self.control['stage'] not in {'checkpoint', 'respond'}
                  and current >= self.soft_deadline - self.policy['respond_seconds']):
                self._issue('respond', 'return_structured_response', current)
            elif (self.control['stage'] == 'work'
                  and current >= self.soft_deadline - self.policy['finish_seconds']):
                self._issue('finish', 'save_current_work_and_checks', current)
        if self.summary() != before:
            self.publish_record(self.summary())
        return self.stop_reason

    def finish(self, reason):
        self._event('process_finished', self.clock(), reason=reason)
        self.publish_record(self.summary())

    def summary(self):
        return {'schema_version': 'accdsl.worker-supervision.v1', 'worker_id': self.worker_id,
                'soft_deadline_monotonic': self.soft_deadline,
                'hard_deadline_monotonic': self.hard_deadline,
                'effective_deadline_monotonic': self.effective_deadline(),
                'progress_count': self.progress_count, 'last_progress_monotonic': self.last_progress,
                'control': dict(self.control), 'control_ack_sequence': self.ack,
                'checkpoint': self.checkpoint, 'stop_reason': self.stop_reason,
                'events': list(self.events)}
