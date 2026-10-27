#!/usr/bin/env python3
"""Resumable, reviewed accounting work with bounded repair and one stable command."""
from __future__ import annotations

import argparse
import ast
import ctypes
from contextlib import contextmanager, nullcontext
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
import uuid

from accounting_master_support import (atomic_json, baseline, digest, load_json,
                                      local_path, release_hashes, run_phase_tests,
                                      source_register, verify_hashes, preserve_editable, changes_since, protected_hashes,
                                      atomic_bytes, merge_hashes, verify_builtin,
                                      phase_recovery, recovery_excerpt, contributed_changes,
                                      editable_files, worker_inventory, validate_artifact_contract, verification_input_errors,
                                      compact_worker_packet, historical_resolution_checks)
from accounting_worker_clock import worker_budget
from accounting_worker_supervision import ProgressMonitor, scoped_inventory, inventory_hash

ROOT = Path(__file__).resolve().parents[1]
CATALOG = 'scripts/accounting_master_catalog.json'
SCHEMA = 'scripts/accounting_master_response.schema.json'
CONTROLS = [
    'scripts/run_accounting_master.py', 'scripts/accounting_master_support.py',
    CATALOG, SCHEMA, 'tests/test_accounting_master.py',
    'docs/plans/accounting-master-program.md',
    'scripts/check_accounting_proposal.py', 'tests/test_accounting_proposal.py',
    'docs/plans/accounting-p15-execution-repair-20261004.md',
    'scripts/accounting_worker_clock.py',
    'scripts/accounting_worker_supervision.py',
    'docs/plans/accounting-progress-supervision-20261006.md',
    'docs/plans/accounting-worker-timing-repair-20261004.md',
    'docs/plans/accounting-master-campaign-20261005.md',
    'tests/test_accounting_proposal_current.py',
    'docs/plans/accounting-proposal-evidence-supplement-20261005.md',
    'docs/plans/accounting-master-controller-repair-20261005.md',
]
ACCEPTED = 'accepted_internal'
PUBLIC_ACTIONS = ['install-and-run', 'run', 'campaign', 'status', 'refresh', 'stop', 'review']
RESPONSE_KEYS = {'verdict', 'summary', 'steps', 'assumptions', 'checks',
                 'evidence', 'issues', 'residuals', 'next_actions'}
MAX_RUN_SECONDS = 7200


class MasterError(RuntimeError):
    pass


class ContinuationVeto(MasterError):
    pass


class ProcessTimeout(MasterError):
    pass


class ReviewPending(MasterError):
    pass


class BudgetDeferred(MasterError):
    """No useful worker can be launched within this invocation's budget."""


def now():
    return datetime.now(timezone.utc).isoformat()


def stable_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def campaign_remaining(record):
    if (not isinstance(record, dict) or record.get('schema_version') != 'accdsl.master.campaign.v1'
            or not record.get('boot_id') or record['boot_id'] != boot_identity()):
        raise ContinuationVeto('Campaign host boot changed or state is invalid; supervisor recovery required without resetting its allowance')
    values = [record.get(k) for k in ('started_monotonic', 'deadline_monotonic', 'allowance_seconds')]
    if (any(type(v) not in (float, int) or not math.isfinite(v) for v in values)
            or not 0 < values[2] <= 172800 or abs(values[1] - values[0] - values[2]) > .001):
        raise ContinuationVeto('Invalid campaign deadline or allowance')
    current = time.monotonic()
    if current < values[0]:
        raise ContinuationVeto('Campaign monotonic clock moved backwards')
    return max(0, values[1] - current)


def campaign_progress(root, run_folder, before_accepted, state):
    accepted = sorted(p for p, record in state['phases'].items()
                      if record['status'] == ACCEPTED and p not in before_accepted)
    changed = set()
    for path in run_folder.glob('*/execution-*/changes.json'):
        delta = load_json(path)
        changed.update(n for names in delta.values() for n in names
                       if not n.endswith('/progress.md'))
    # This is the existing controller's file-progress signal, not substantive
    # acceptance. Independent phase review still decides whether work is sound.
    return {'accepted_phases': accepted, 'changed_files': sorted(changed),
            'progress': bool(accepted or changed)}


def git_provenance(root):
    """Observe HEAD; the existing content hashes identify uncommitted work."""
    try:
        result = subprocess.run(['git', 'rev-parse', '--verify', 'HEAD'], cwd=root,
                                capture_output=True, encoding='utf-8', errors='replace',
                                timeout=5, check=False)
    except subprocess.TimeoutExpired:
        reason = 'git rev-parse --verify HEAD timed out after 5 seconds'
    except OSError as error:
        reason = f'{type(error).__name__}: {error}'[:500]
    else:
        commit = result.stdout.strip()
        if result.returncode:
            detail = (result.stderr.strip() or result.stdout.strip() or 'no diagnostic')[:500]
            reason = f'git rev-parse --verify HEAD exited {result.returncode}: {detail}'
        elif not re.fullmatch(r'(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})', commit):
            reason = 'git rev-parse returned an invalid commit ID'
        else:
            return {'git_commit': commit, 'git_reason': None}
    return {'git_commit': None, 'git_reason': reason}


def worker_overrides(mode, config, role=None):
    overrides = []
    for server in config.get('mcp_servers', {}):
        # Codex's dotted override parser treats quoted key segments literally.
        # Existing bare server keys must be addressed without adding quotes.
        if not re.fullmatch(r'[A-Za-z0-9_-]+', server):
            raise MasterError('An integration key needs an explicitly reviewed override form')
        overrides += ['-c', 'mcp_servers.' + server + '.enabled=false']
    for feature in ['apps', 'plugins', 'hooks', 'multi_agent']:
        overrides += ['--disable', feature]
    if mode == 'read-only':
        effort = 'medium' if role == 'review_controller' else 'high'
        overrides += ['-c', 'model_reasoning_effort=' + json.dumps(effort)]
    return overrides


def worker_seconds(role, limits):
    if role == 'probe':
        return 60
    if role in {'implement', 'repair'}:
        return limits['phase_seconds']
    if role == 'plan':
        return limits['plan_seconds']
    if role in {'review_plan', 'review_result'}:
        return limits.get('phase_review_seconds', limits['review_seconds'])
    return limits['review_seconds']


def validate_response(value, allowed):
    if not isinstance(value, dict) or set(value) != RESPONSE_KEYS:
        raise MasterError('Invalid worker response fields')
    if (not isinstance(value['verdict'], str) or value['verdict'] not in allowed
            or not isinstance(value['summary'], str) or not value['summary'].strip()):
        raise MasterError('Invalid worker verdict or summary')
    for key in RESPONSE_KEYS - {'verdict', 'summary'}:
        if not isinstance(value[key], list) or any(not isinstance(x, str) for x in value[key]):
            raise MasterError(f'Invalid worker list: {key}')
    if value['verdict'] == 'PLAN' and (not value['steps'] or not value['checks']):
        raise MasterError('A plan requires concrete steps and checks')
    if value['verdict'] == 'AGREE' and value['issues']:
        raise MasterError('AGREE cannot retain unresolved review issues')
    if value['verdict'] == 'PARTIAL' and not value['next_actions']:
        raise MasterError('Partial work requires an explicit next bounded task')
    return value


def role_verdicts(role):
    if role == 'plan':
        return {'PLAN', 'BLOCKED'}
    if role in {'probe', 'review_plan', 'review_result', 'review_controller'}:
        return {'AGREE', 'REVISE', 'BLOCKED'}
    if role in {'implement', 'repair'}:
        return {'IMPLEMENTED', 'PARTIAL', 'BLOCKED'}
    raise MasterError('Unknown worker role')


def acceptance_ready(phase, checked):
    """Engineering success cannot override a declared incomplete criterion."""
    if (checked.get('passed') is not True or type(checked.get('tests')) is not int
            or checked['tests'] <= 0):
        return False
    acceptance = checked.get('acceptance', {})
    if not isinstance(acceptance, dict):
        return False
    if checked.get('phase_criteria_complete') is False or acceptance.get('phase_criteria_complete') is False:
        return False
    if phase.get('checker'):
        expected = {f'criterion_{i + 1}': 'complete_bounded' for i in range(len(phase['criteria']))}
        return (acceptance.get('phase_criteria_complete') is True
                and acceptance.get('criteria') == expected)
    return True


def validate_catalog(catalog):
    phases = catalog['phases']
    ids = [p['id'] for p in phases]
    if len(ids) != len(set(ids)) or not phases:
        raise MasterError('Duplicate or empty phase catalog')
    seen = set()
    for p in phases:
        if not p['id'].startswith('P') or not p['id'][1:].isdigit():
            raise MasterError('Invalid phase identifier')
        if any(d not in seen for d in p['deps']):
            raise MasterError('Catalog must be an ordered acyclic dependency graph')
        if p['kind'] not in {'builtin', 'worker'} or not p['criteria'] or not p['deliverables']:
            raise MasterError('Invalid phase contract')
        if 'checker' in p:
            argv = p['checker']
            if (not isinstance(argv, list) or not argv or any(not isinstance(a, str) or not a for a in argv)
                    or not argv[0].startswith('scripts/') or not argv[0].endswith('.py')
                    or '..' in Path(argv[0]).parts):
                raise MasterError('Checker must be a repository Python script and literal argument list')
        for name in p.get('retry_inputs', []):
            if not isinstance(name, str) or Path(name).is_absolute() or '..' in Path(name).parts:
                raise MasterError('Unsafe retry input path')
        if p.get('continuation_policy', 'fresh_plan') not in {'fresh_plan', 'reviewed_scope'}:
            raise MasterError('Unknown continuation policy')
        for key in ('execution_plan', 'historical_input_resolutions'):
            if key in p and (not isinstance(p[key], str) or not p[key]
                             or Path(p[key]).is_absolute() or '..' in Path(p[key]).parts):
                raise MasterError('Unsafe phase document path')
        seen.add(p['id'])
    gaps = {g for p in phases for g in p['gaps']}
    if gaps != {f'G{i}' for i in range(1, 19)}:
        raise MasterError('Catalog does not preserve all G1–G18')
    workflow = catalog.get('workflow', {})
    if workflow.get('mode') != 'proposal':
        raise MasterError('This master runs proposal work only; implementation needs a separately selected plan')
    policies = workflow.get('phase_policy', {})
    if set(policies) != set(ids):
        raise MasterError('Every phase needs an explicit workflow policy')
    proposal = workflow.get('proposal_phases', [])
    if (not proposal or len(proposal) != len(set(proposal)) or not set(proposal) <= set(ids)
            or workflow.get('gate_phase') != proposal[-1]):
        raise MasterError('Invalid proposal sequence')
    for identifier, policy in policies.items():
        if policy.get('class') not in {'design', 'research', 'exploratory_probe', 'product_implementation', 'review'}:
            raise MasterError('Unknown phase class')
        if identifier not in proposal and policy.get('schedule') != 'held':
            raise MasterError('Legacy work must remain held during proposal preparation')
        if identifier in proposal:
            if policy.get('schedule') != 'active' or policy['class'] == 'product_implementation':
                raise MasterError('Product work cannot be a proposal prerequisite')
            phase = next(p for p in phases if p['id'] == identifier)
            if any(d not in proposal for d in phase['deps']):
                raise MasterError('Proposal work cannot depend on the held implementation queue')
            if not policy.get('write_scope'):
                raise MasterError('Proposal work needs an explicit write scope')
            if policy['class'] == 'exploratory_probe' and not all(policy.get(k) for k in ('design_question', 'decision_effect', 'stop_condition')):
                raise MasterError('A probe must answer a named design decision')
        for name in policy.get('write_scope', []):
            if (not isinstance(name, str) or not name or name.strip('/') in {'', '.'}
                    or Path(name).is_absolute() or '..' in Path(name).parts
                    or '*' in name or Path(name).as_posix() != name.rstrip('/')):
                raise MasterError('Unsafe workflow write scope')


def validate_state(state, phases):
    """Reject damaged or incompatible state before it can select work."""
    required = {'schema_version', 'created_at', 'mission_complete', 'gap_status', 'phases', 'runs', 'last_outcome'}
    statuses = {'pending', 'running', 'repairing', 'interrupted', 'stale',
                'blocked_external', 'needs_plan_repair', 'needs_repair', 'needs_review', 'budget_deferred', ACCEPTED}
    def reject(message):
        raise ContinuationVeto('Invalid persisted state: ' + message)
    def strings(value):
        return isinstance(value, list) and all(isinstance(v, str) for v in value)
    if not isinstance(state, dict) or not required <= state.keys():
        reject('required fields are missing')
    if state['schema_version'] != 'accdsl.master.state.v1' or state['mission_complete'] is not False:
        reject('unsupported schema or mission promotion')
    if not isinstance(state['created_at'], str) or not strings(state['runs']):
        reject('invalid creation/run metadata')
    if state['last_outcome'] is not None and not isinstance(state['last_outcome'], dict):
        reject('invalid last outcome')
    if 'plan_generation' in state and (type(state['plan_generation']) is not int or state['plan_generation'] < 0):
        reject('invalid plan generation')
    if state['gap_status'] != {f'G{i}': 'open' for i in range(1, 19)}:
        reject('gap keys or unsupported closure')
    if not isinstance(state['phases'], dict) or set(state['phases']) != set(phases):
        reject('catalog IDs changed; explicit migration required')
    for name, record in state['phases'].items():
        if not isinstance(record, dict) or not {'status', 'attempts', 'residuals'} <= record.keys():
            reject(name + ' required phase fields are missing')
        if not isinstance(record['status'], str) or record['status'] not in statuses:
            reject(name + ' unknown status')
        for field in ['attempts', 'residuals', 'issues', 'next_actions', 'outstanding_deletions', 'contributed_files']:
            if field in record and not strings(record[field]):
                reject(name + ' invalid ' + field)
        for field in ['entry_inventory_path', 'accepted_at', 'block_signature',
                      'pending_review', 'pending_review_sha256']:
            if field in record and not isinstance(record[field], str):
                reject(name + ' invalid ' + field)
        if 'evidence_hashes' in record:
            hashes = record['evidence_hashes']
            if not isinstance(hashes, dict) or any(not isinstance(k, str) or not isinstance(v, str)
                    or re.fullmatch(r'[0-9a-f]{64}', v) is None for k, v in hashes.items()):
                reject(name + ' invalid evidence hashes')


def control_snapshot(root, paths):
    existing = {str(p.relative_to(root)): digest(p) for p in paths if p.exists()}
    absent = [str(p.relative_to(root)) for p in paths if not p.exists()]
    return existing, absent


def created_controls(root, absent):
    return [name for name in absent if (root / name).exists()]


@contextmanager
def exclusive_lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise MasterError('Another master runner holds the single-writer lock') from exc
        stream.seek(0)
        stream.truncate()
        stream.write(str(os.getpid()))
        stream.flush()
        try:
            yield stream.fileno()
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def terminate_group(proc):
    with defer_shutdown():
        _terminate_group(proc)


@contextmanager
def defer_shutdown():
    previous = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGTERM, signal.SIGINT})
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous)


def _terminate_group(proc):
    if getattr(proc, '_master_cleanup_done', False):
        return
    original = getattr(proc, '_master_identity', None)
    if getattr(proc, '_master_direct_group', False) and original is None:
        return terminate_unidentified_child(proc)
    try:
        current = process_identity(proc.pid)
    except (OSError, ValueError):
        if getattr(proc, '_master_direct_group', False):
            return terminate_unidentified_child(proc)
        raise
    if original is None:
        if proc.returncode is not None:
            return  # Already reaped by the caller: do not signal a reusable PID.
        original = current
    if current is None and getattr(proc, '_master_direct_group', False):
        return terminate_unidentified_child(proc)
    if current is None:
        if live_group_members(proc.pid):
            raise ContinuationVeto('Group leader was reaped before cleanup; ownership needs inspection')
    elif not original or current['start_ticks'] != original['start_ticks'] or current['pgid'] != proc.pid:
        raise ContinuationVeto('Process-group identity changed; unrelated processes were not signalled')
    else:
        os.killpg(proc.pid, signal.SIGTERM)
        deadline = time.monotonic() + 3
        while live_group_members(proc.pid) and time.monotonic() < deadline:
            time.sleep(.02)
        # The leader remains unreaped, including when it is a zombie. Its PID
        # therefore cannot be reused between the ownership check and this signal.
        current = process_identity(proc.pid)
        if current and current['start_ticks'] == original['start_ticks']:
            if live_group_members(proc.pid):
                os.killpg(proc.pid, signal.SIGKILL)
        deadline = time.monotonic() + 3
        while live_group_members(proc.pid) and time.monotonic() < deadline:
            time.sleep(.02)
        if live_group_members(proc.pid):
            raise ContinuationVeto('Group did not become quiescent after escalation; recovery remains unresolved')
    proc.wait(timeout=5)
    proc._master_cleanup_done = True


def terminate_unidentified_child(proc):
    """An unreaped Popen child anchors its initial group without /proc identity."""
    if proc.returncode is not None:
        raise ContinuationVeto('Unidentified child was already reaped; no group signal sent')
    # WNOWAIT verifies that this is still our direct, unreaped child. No other
    # thread/reaper is permitted by bounded_process's single-threaded contract.
    os.waitid(os.P_PID, proc.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
    if os.getpgid(proc.pid) != proc.pid:
        raise ContinuationVeto('New child no longer anchors its initial process group')
    def members():
        found = []
        for entry in Path('/proc').iterdir():
            if not entry.name.isdigit():
                continue
            try:
                fields = (entry / 'stat').read_text().rsplit(') ', 1)[1].split()
            except (FileNotFoundError, ProcessLookupError):
                continue
            # Unreadable metadata cannot establish quiescence; preserve a veto.
            if int(fields[2]) == proc.pid and fields[0] != 'Z':
                found.append(int(entry.name))
        return found
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(proc.pid, sig)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + 3
        try:
            while members() and time.monotonic() < deadline:
                time.sleep(.02)
            if not members():
                proc.wait(timeout=5)
                proc._master_cleanup_done = True
                return
        except (OSError, ValueError, IndexError):
            if sig == signal.SIGKILL:
                raise ContinuationVeto('Cannot verify new-child group cleanup; supervisor inspection required')
    raise ContinuationVeto('New-child group remained live after bounded escalation')


def boot_identity():
    value = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    if not value:
        raise ContinuationVeto('Host boot identity is unavailable')
    return value


def process_identity(pid):
    try:
        fields = (Path('/proc') / str(pid) / 'stat').read_text().rsplit(') ', 1)[1].split()
        return {'pid': pid, 'state': fields[0], 'pgid': int(fields[2]), 'start_ticks': int(fields[19]),
                'boot_id': boot_identity()}
    except FileNotFoundError:
        return None


def live_group_members(pgid):
    members = []
    for entry in Path('/proc').iterdir():
        if entry.name.isdigit():
            try:
                info = process_identity(int(entry.name))
            except (PermissionError, ProcessLookupError):
                continue
            if info and info['pgid'] == pgid and info['state'] != 'Z':
                members.append(info)
    return members


def open_pidfd(pid):
    if hasattr(os, 'pidfd_open'):
        return os.pidfd_open(pid)
    # This host's Python lacks the wrapper, but Linux x86-64 exposes syscall
    # 434, verified in /usr/include/x86_64-linux-gnu/asm/unistd_64.h. See the
    # Linux man-pages pidfd_open(2) syscall example. Other ABIs fail explicitly.
    if sys.platform != 'linux' or platform.machine() != 'x86_64':
        raise ContinuationVeto('No reviewed pidfd_open binding for this platform')
    libc = ctypes.CDLL(None, use_errno=True)
    libc.syscall.restype = ctypes.c_long
    result = libc.syscall(ctypes.c_long(434), ctypes.c_int(pid), ctypes.c_uint(0))
    if result < 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))
    return int(result)


def stop_recovered_group(previous):
    with defer_shutdown():
        _stop_recovered_group(previous)


def _stop_recovered_group(previous):
    """Freeze membership before destroying the live group-lifetime anchor."""
    if previous.get('boot_id') != boot_identity():
        raise ContinuationVeto('Recovered worker has no matching host boot identity; no signal was sent')
    leader = process_identity(previous['pid'])
    if not leader or any(leader[k] != previous[k] for k in ['pid', 'pgid', 'start_ticks']):
        raise ContinuationVeto('Recovered worker ownership changed before signalling')
    if not hasattr(signal, 'pidfd_send_signal'):
        raise ContinuationVeto('Stable process signalling is unavailable; inspect the prior worker')
    descriptors = {}
    try:
        def retain(member):
            key = (member['pid'], member['start_ticks'])
            if key in descriptors:
                return descriptors[key]
            try:
                fd = open_pidfd(member['pid'])
            except ProcessLookupError:
                return None
            descriptors[key] = fd
            current = process_identity(member['pid'])
            if not current or current['start_ticks'] != member['start_ticks'] or current['pgid'] != previous['pgid']:
                del descriptors[key]
                os.close(fd)
                return None
            return fd
        anchor_fd = retain(leader)
        anchor = process_identity(previous['pid'])
        if anchor_fd is None or not anchor or any(anchor[k] != previous[k] for k in ['pid', 'pgid', 'start_ticks']):
            raise ContinuationVeto('Saved group lifetime changed while collecting recovery handles; no signal was sent')
        if anchor['state'] == 'Z':
            if live_group_members(previous['pgid']):
                raise ContinuationVeto('Recovered leader has exited with descendants; preserve identities for scoped recovery')
            return
        signal.pidfd_send_signal(anchor_fd, signal.SIGSTOP)
        deadline = time.monotonic() + 3
        while True:
            anchor = process_identity(previous['pid'])
            if not anchor or anchor['start_ticks'] != previous['start_ticks'] or anchor['state'] == 'Z':
                raise ContinuationVeto('Recovery lost its live lifetime anchor before quiescence')
            members = live_group_members(previous['pgid'])
            for member in members:
                fd = retain(member)
                if fd is not None and member['state'] not in {'T', 't'}:
                    try:
                        signal.pidfd_send_signal(fd, signal.SIGSTOP)
                    except ProcessLookupError:
                        pass
            # All members must have acknowledged STOP; another scan catches
            # children forked between the previous enumeration and STOP delivery.
            current = live_group_members(previous['pgid'])
            if current and all(m['state'] in {'T', 't'} and (m['pid'], m['start_ticks']) in descriptors for m in current):
                break
            if time.monotonic() >= deadline:
                raise ContinuationVeto('Recovery could not freeze all group members within its bound')
            time.sleep(.02)
        for fd in descriptors.values():
            try:
                signal.pidfd_send_signal(fd, signal.SIGKILL)
            except ProcessLookupError:
                pass
        deadline = time.monotonic() + 3
        while live_group_members(previous['pgid']) and time.monotonic() < deadline:
            time.sleep(.02)
    finally:
        for fd in descriptors.values():
            os.close(fd)
    if live_group_members(previous['pgid']):
        raise ContinuationVeto('Prior worker group still has live members after stable-identity cleanup')


@contextmanager
def catch_termination():
    previous = signal.getsignal(signal.SIGTERM)
    def stopped(signum, frame):
        raise KeyboardInterrupt('Supervisor received SIGTERM')
    signal.signal(signal.SIGTERM, stopped)
    try:
        yield
    finally:
        signal.signal(signal.SIGTERM, previous)


def bounded_process(argv, cwd, log, seconds, *, prompt=None, heartbeat=None, stopped=None, on_spawn=None, pass_fds=(), deadline=None, separate_stderr=False, progress_monitor=None):
    """Bound the initial process group. Workers are trusted not to detach jobs."""
    log.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    cutoff = min(started + seconds, deadline) if deadline is not None else started + seconds
    prompt_file = log.with_suffix('.stdin.txt')
    if prompt is not None:
        prompt_file.write_text(prompt)
    if threading.active_count() != 1:
        raise ContinuationVeto('The reviewed process launcher requires a single-threaded supervisor')
    stderr_path = log.with_suffix('.stderr.log') if separate_stderr else log
    with log.open('wb') as stream, (prompt_file.open('rb') if prompt is not None else open(os.devnull, 'rb')) as input_stream, (stderr_path.open('wb') if separate_stderr else nullcontext(stream)) as error_stream:
        proc = None
        old_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGTERM, signal.SIGINT})
        try:
            # Preparation can consume the remaining window or observe a stop.
            # Refuse before any child exists; callers must not charge a retry.
            reason = ('stop_requested' if stopped and stopped() else
                      'timeout' if time.monotonic() >= (min(cutoff, progress_monitor.soft_deadline)
                          if progress_monitor is not None else cutoff) else None)
            if reason:
                return {'argv': argv, 'exit_code': None, 'reason': reason,
                        'launched': False, 'started_monotonic': started,
                        'deadline_monotonic': cutoff,
                        'wall_seconds': round(time.monotonic() - started, 3), 'log': str(log)}
            # Defer handled interruption until ownership is durably registered.
            # Restore the child's inherited mask before exec. This preexec path
            # is restricted above to a dedicated single-threaded supervisor.
            proc = subprocess.Popen(argv, cwd=cwd, stdin=input_stream,
                                    stdout=stream, stderr=error_stream, start_new_session=True,
                                    env={**os.environ, 'PYTHONUNBUFFERED': '1', 'CUDA_VISIBLE_DEVICES': '-1'}, pass_fds=pass_fds,
                                    preexec_fn=lambda: signal.pthread_sigmask(signal.SIG_SETMASK, old_mask))
            proc._master_direct_group = True
            try:
                proc._master_identity = process_identity(proc.pid)
                if proc._master_identity is None:
                    raise ContinuationVeto('New child metadata is unavailable')
            except (OSError, ValueError, ContinuationVeto):
                proc._master_identity = None
                if on_spawn:
                    on_spawn(proc)
                raise
            if on_spawn:
                on_spawn(proc)
            signal.pthread_sigmask(signal.SIG_SETMASK, old_mask)
            last_beat = started
            reason = None
            # WNOWAIT observes exit without reaping the group leader. Cleanup
            # retains an unambiguous ownership anchor until all signalling ends.
            while True:
                exited = os.waitid(os.P_PID, proc.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
                elapsed = time.monotonic() - started
                if stopped and stopped():
                    reason = 'stop_requested'
                elif sum(p.stat().st_size for p in {log, stderr_path}) > 16 * 1024 * 1024:
                    reason = 'output_limit'
                elif started + elapsed >= cutoff:
                    reason = 'timeout'
                elif progress_monitor is not None:
                    reason = progress_monitor.poll(force=exited is not None)
                if reason or exited is not None:
                    break
                if heartbeat and time.monotonic() - last_beat >= 20:
                    heartbeat(round(elapsed, 1))
                    last_beat = time.monotonic()
                time.sleep(0.1)
            terminate_group(proc)
            if sum(p.stat().st_size for p in {log, stderr_path}) > 16 * 1024 * 1024:
                reason = 'output_limit'
            if progress_monitor is not None:
                progress_monitor.finish(reason)
            return {'argv': argv, 'exit_code': proc.returncode, 'reason': reason, 'launched': True,
                    'started_monotonic': started, 'deadline_monotonic': cutoff,
                    'effective_deadline_monotonic': (progress_monitor.effective_deadline()
                                                     if progress_monitor is not None else cutoff),
                    'wall_seconds': round(time.monotonic() - started, 3), 'log': str(log)}
        finally:
            try:
                if proc is not None:
                    terminate_group(proc)
            finally:
                signal.pthread_sigmask(signal.SIG_SETMASK, old_mask)


class Master:
    def __init__(self, root=ROOT, worker=None, check=None, builtin=None, *, test_only=False):
        self.root = root.resolve()
        self.test_only = test_only
        if test_only and self.root == ROOT:
            raise MasterError('Test injection is prohibited in the live worktree')
        if any(x is not None for x in (worker, check, builtin)) and not test_only:
            raise MasterError('Overrides require explicit isolated test-only mode')
        self.home = self.root / 'data/accounting-master'
        self.catalog = load_json(self.root / CATALOG)
        validate_catalog(self.catalog)
        self.phases = {p['id']: p for p in self.catalog['phases']}
        self.home.mkdir(parents=True, exist_ok=True)
        self.worker_override, self.check_override, self.builtin_override = worker, check, builtin
        self.deadline = float('inf')
        self.run_id = 'not-running'
        self.lock_fd = None
        self.protected = {}
        self.runtime_expected = None
        self.controls = {name: digest(self.root / name) for name in CONTROLS if (self.root / name).exists()}
        self.state_path = self.home / 'state.json'
        self.state_observed = self.state_path.exists()
        self.state = load_json(self.state_path) if self.state_path.exists() else {
            'schema_version': 'accdsl.master.state.v1', 'created_at': now(),
            'mission_complete': False, 'gap_status': {f'G{i}': 'open' for i in range(1, 19)},
            'phases': {p: {'status': 'pending', 'attempts': [], 'residuals': []} for p in self.phases},
            'runs': [], 'last_outcome': None,
            'workflow_sha256': stable_hash(self.catalog['workflow']),
        }
        validate_state(self.state, self.phases)
        self.verify_workflow()

    def verify_workflow(self):
        if self.state.get('workflow_sha256') != stable_hash(self.catalog['workflow']):
            raise ContinuationVeto('Workflow changed; explicit evidence-preserving state migration required')

    def phase_block(self, identifier):
        policy = self.catalog['workflow']['phase_policy'][identifier]
        if policy['class'] == 'product_implementation':
            return 'blocked_by_proposal_gate: product implementation is outside the current proposal campaign'
        if policy['schedule'] != 'active':
            return 'held_historical_evidence: use the new proposal sequence'
        return None

    def proposal_gate(self):
        workflow = self.catalog['workflow']
        pending = [p for p in workflow['proposal_phases'] if self.state['phases'][p]['status'] != ACCEPTED]
        value = {'schema_version': 'accdsl.proposal.readiness.v1', 'ready': False,
                 'status': 'incomplete', 'pending_phases': pending,
                 'workflow_sha256': stable_hash(workflow), 'human_acceptance': 'pending',
                 'implementation_enabled': False,
                 'reason': 'Complete and independently review the governing proposal before choosing implementation.'}
        if not pending:
            try:
                for identifier in workflow['proposal_phases']:
                    accepted = self.state['phases'][identifier]
                    if (accepted.get('accepted_phase_hash') != stable_hash(self.phases[identifier])
                            or accepted.get('accepted_dependencies') != self.review_dependencies(self.phases[identifier])
                            or not accepted.get('evidence_hashes')
                            or verify_hashes(self.root, accepted['evidence_hashes'])):
                        raise ValueError('stale proposal phase: ' + identifier)
                from check_accounting_proposal import check_proposal
                checked = check_proposal(self.root, workflow['gate_phase'])
                if not checked['passed']:
                    raise ValueError('; '.join(checked['errors']))
                record = self.state['phases'][workflow['gate_phase']]
                if any(record['evidence_hashes'].get(name) != sha
                       for name, sha in checked['input_hashes'].items()):
                    raise ValueError('proposal acceptance does not bind every current input')
                review_path = record['accepted_review_path']
                process_path = review_path.replace('.response.json', '.process.json')
                if (not review_path.endswith('.response.json')
                        or review_path not in record['evidence_hashes']
                        or process_path not in record['evidence_hashes']):
                    raise ValueError('proposal review/evidence changed')
                review = load_json(local_path(self.root, review_path))
                validate_response(review, {'AGREE'})
                process = load_json(local_path(self.root, process_path))
                if (process['exit_code'] != 0 or process['reason']
                        or process.get('surviving_group_members')):
                    raise ValueError('proposal review process did not finish cleanly')
                value.update(ready=True, status='reviewed_internal',
                             evidence_hashes=record['evidence_hashes'], review=review_path,
                             reason='Proposal reviewed internally; present it to the user before selecting product implementation.')
            except (OSError, ValueError, KeyError, TypeError, MasterError) as error:
                value.update(status='evidence_incomplete', reason=str(error))
        return value

    def reload_state(self):
        if self.state_path.exists():
            self.state = load_json(self.state_path)
            self.state_observed = True
        elif self.state_observed:
            raise ContinuationVeto('Persisted checkpoint disappeared; explicit recovery is required')
        validate_state(self.state, self.phases)
        self.verify_workflow()

    def save(self):
        if self.state_observed and not self.state_path.exists():
            raise ContinuationVeto('Persisted checkpoint disappeared; refusing to recreate cached state')
        self.state['updated_at'] = now()
        self.state['mission_complete'] = False
        validate_state(self.state, self.phases)
        atomic_json(self.state_path, self.state)
        self.state_observed = True

    def event(self, kind, **fields):
        with defer_shutdown():
            self.check_runtime()
            record = {'time': now(), 'run': self.run_id, 'event': kind, **fields}
            path = self.home / 'events.jsonl'
            prior = path.read_bytes() if self.runtime_expected is not None and path.exists() else b''
            line = json.dumps(record, ensure_ascii=False, allow_nan=False) + '\n'
            with path.open('a') as stream:
                stream.write(line)
                stream.flush()
                os.fsync(stream.fileno())
            if self.runtime_expected is not None:
                self.runtime_expected[str(path.relative_to(self.root))] = hashlib.sha256(prior + line.encode()).hexdigest()
            self.check_runtime()
            print(json.dumps(record, ensure_ascii=False), flush=True)

    def check_runtime(self):
        for name, expected in (self.runtime_expected or {}).items():
            path = self.root / name
            actual = digest(path) if path.exists() else None
            if actual != expected:
                raise ContinuationVeto('Supervisor runtime file changed outside its recorded writes: ' + name)

    def runtime_json(self, path, value):
        with defer_shutdown():
            self.check_runtime()
            atomic_json(path, value)
            if self.runtime_expected is not None:
                encoded = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()
                self.runtime_expected[str(path.relative_to(self.root))] = hashlib.sha256(encoded).hexdigest()
            self.check_runtime()

    def remaining(self, requested):
        value = min(requested, self.deadline - time.monotonic())
        if value <= 0:
            raise MasterError('Run wall-time limit reached; preserve partial work and resume')
        return value

    def require_budget(self, seconds, purpose):
        available = self.deadline - time.monotonic()
        if available < seconds:
            raise BudgetDeferred(f'Budget deferred before {purpose}: need {seconds:g} seconds, '
                                 f'have {max(0, available):.1f}; preserve work and resume with a fresh invocation.')

    def check_protection(self):
        try:
            expected = merge_hashes(self.protected, self.controls)
        except ValueError as error:
            raise ContinuationVeto(str(error)) from error
        changed = verify_hashes(self.root, expected)
        if changed:
            raise ContinuationVeto('Protected evidence/controller changed: ' + ', '.join(changed[:20]))

    def refresh(self):
        self.check_protection()
        self.verify_workflow()
        validate_state(self.state, self.phases)
        # A previous accepted phase is reusable only while its recorded evidence survives.
        for identifier, record in self.state['phases'].items():
            if record['status'] == ACCEPTED:
                stale = verify_hashes(self.root, record.get('evidence_hashes', {})) if record.get('evidence_hashes') else ['missing acceptance evidence']
                if record.get('accepted_phase_hash') != stable_hash(self.phases[identifier]):
                    stale.append('accepted phase contract changed or requires explicit legacy migration')
                if record.get('accepted_dependencies') != self.review_dependencies(self.phases[identifier]):
                    stale.append('accepted prerequisite evidence changed')
                if stale:
                    record['status'] = 'stale'
                    record['issues'] = ['Accepted evidence changed: ' + ', '.join(stale[:10])]
        for p in self.catalog['phases']:
            record = self.state['phases'][p['id']]
            if record['status'] == ACCEPTED and any(self.state['phases'][d]['status'] != ACCEPTED for d in p['deps']):
                record['status'] = 'stale'
                record['issues'] = ['A prerequisite is no longer accepted']
        blocked = {p: self.phase_block(p) for p in self.phases if self.phase_block(p)}
        eligible = [p['id'] for p in self.catalog['phases']
                    if self.state['phases'][p['id']]['status'] != ACCEPTED
                    and p['id'] not in blocked
                    and (self.state['phases'][p['id']]['status'] != 'blocked_external'
                         or self.state['phases'][p['id']].get('block_signature') != self.input_fingerprint(p['id']))
                    and self.state['phases'][p['id']].get('deferred_signature') != self.input_fingerprint(p['id'])
                    and all(self.state['phases'][d]['status'] == ACCEPTED for d in p['deps'])]
        self.state['plan_generation'] = self.state.get('plan_generation', 0) + 1
        self.save()  # Canonical commit first; derived views are rebuilt on every resume.
        gate = self.proposal_gate()
        atomic_json(self.home / 'proposal-ready.json', gate)
        plan = {'schema_version': 'accdsl.master.next_plan.v1', 'created_at': now(),
                'generation': self.state['plan_generation'], 'state_sha256': digest(self.state_path),
                'catalog_sha256': digest(self.root / CATALOG), 'controller_hashes': self.controls,
                'last_outcome': self.state['last_outcome'], 'eligible_phases': eligible,
                'next_phase': eligible[0] if eligible else None,
                'phase_states': {k: v['status'] for k, v in self.state['phases'].items()},
                'residuals': {k: v.get('residuals', []) for k, v in self.state['phases'].items()},
                'next_actions': {k: v.get('next_actions', []) for k, v in self.state['phases'].items() if v.get('next_actions')},
                'issues': {k: v.get('issues', []) for k, v in self.state['phases'].items() if v.get('issues')},
                'gap_status': self.state['gap_status'], 'mission_complete': False,
                'workflow_mode': self.catalog['workflow']['mode'], 'proposal_gate': gate,
                'blocked_phases': blocked,
                'phase_classes': {p: v['class'] for p, v in self.catalog['workflow']['phase_policy'].items()},
                'external_retry_policy': 'Unknown external changes are not polled. After a known access/input change, explicitly run --retry-blocked with the same approved prefix.',
                'continuation': 'Complete the governing product proposal. Preserve prototypes as evidence; product implementation is held. ' + gate['reason']}
        atomic_json(self.home / 'next-plan.json', plan)
        lines = ['# Accounting master — refreshed next plan', '', f'Updated: {plan["created_at"]}', '',
                 f'Next eligible phase: {plan["next_phase"] or "none in this catalog"}.',
                 f'Workflow: proposal first. Proposal ready: **{gate["ready"]}**. Product implementation enabled: **false**.',
                 'Mission complete: **no**. Scoped phase acceptance does not close the original gaps.', '',
                 '| Phase | State | Residual work |', '| --- | --- | --- |']
        for identifier, record in self.state['phases'].items():
            residual = '; '.join(record.get('residuals', [])).replace('|', '/')
            scheduling = blocked.get(identifier, 'active proposal sequence')
            lines.append(f'| {identifier} — {self.phases[identifier]["name"]} | {record["status"]}; {scheduling} | {residual} |')
        lines.extend(['', '## Latest outcome', '', json.dumps(plan['last_outcome'], indent=2), '',
                      '## Next action', '', plan['continuation'], ''])
        atomic_bytes(self.home / 'next-plan.md', '\n'.join(lines).encode())
        return plan

    def refresh_worker_plan(self):
        """Keep retries focused while retaining the complete plan on disk."""
        plan = self.refresh()
        compact = {key: plan[key] for key in
                   ('generation', 'next_phase', 'workflow_mode', 'proposal_gate',
                    'continuation', 'last_outcome', 'phase_states')}
        active = set(self.catalog['workflow']['proposal_phases'])
        for key in ('next_actions', 'issues', 'residuals'):
            compact[key] = {phase: values for phase, values in plan[key].items()
                            if phase in active and values}
        compact['full_plan_path'] = str((self.home / 'next-plan.json').relative_to(self.root))
        return compact

    def input_fingerprint(self, identifier):
        inputs = {}
        for name in self.phases[identifier].get('retry_inputs', []):
            path = local_path(self.root, name)
            if path.is_dir():
                for child in sorted(path.rglob('*')):
                    if child.is_file() and not child.is_symlink() and '__pycache__' not in child.parts:
                        inputs[str(child.relative_to(self.root))] = digest(child)
            else:
                inputs[name] = digest(path) if path.is_file() else None
        return stable_hash({'catalog': digest(self.root / CATALOG), 'controls': self.controls,
            'relevant_inputs': inputs,
            'dependencies': {d: self.state['phases'][d].get('evidence_hashes', {}) for d in self.phases[identifier]['deps']}})

    def process(self, argv, log, seconds, prompt=None, internal_phase=None, deadline=None,
                separate_stderr=False, progress_monitor=None):
        active_path = self.home / 'active-process.json'
        active = {}
        owned_process = None
        guarded, absent = control_snapshot(self.root, [self.state_path, self.home / 'authorization.json', self.home / 'next-plan.json', self.home / 'proposal-ready.json'])
        if internal_phase:
            if self.lock_fd is None:
                raise MasterError('An internal operation requires the held supervisor lock')
            capability = uuid.uuid4().hex + uuid.uuid4().hex
            grant = log.with_suffix('.capability.json')
            output = str(Path(argv[argv.index('--out') + 1]).resolve())
            atomic_json(grant, {'phase': internal_phase, 'output': output, 'run_id': self.run_id,
                               'parent': process_identity(os.getpid()), 'consumed': False,
                               'capability_sha256': hashlib.sha256(capability.encode()).hexdigest()})
            argv = [*argv, '--lock-fd', str(self.lock_fd), '--grant', str(grant), '--capability', capability]
        def spawned(proc):
            nonlocal owned_process
            owned_process = proc
            active.update({'status': 'running', 'run_id': self.run_id, 'started_at': now(),
                           'identity': getattr(proc, '_master_identity', None) or {'pid': proc.pid, 'pgid': proc.pid, 'metadata_unavailable': True},
                           'argv': argv, 'log': str(log.relative_to(self.root))})
            self.runtime_json(active_path, active)
        try:
            result = bounded_process(argv, self.root, log, self.remaining(seconds), prompt=prompt,
                                     heartbeat=lambda elapsed: self.event('heartbeat', stage=log.stem, seconds=elapsed),
                                     stopped=lambda: (self.home / 'stop-request.json').exists(), on_spawn=spawned,
                                     deadline=deadline, separate_stderr=separate_stderr,
                                     pass_fds=(self.lock_fd,) if internal_phase and self.lock_fd is not None else (),
                                     progress_monitor=progress_monitor)
        finally:
            with defer_shutdown():
                errors, remaining, changed = [], [], []
                original_error = str(sys.exception())
                try:
                    if active.get('identity'):
                        if owned_process is not None and getattr(owned_process, '_master_cleanup_done', False):
                            remaining = []
                        elif active['identity'].get('metadata_unavailable'):
                            remaining = [{'pid': active['identity']['pid'], 'cleanup': 'unverified; metadata unavailable'}]
                        else:
                            remaining = live_group_members(active['identity']['pgid'])
                        active.update(status='cleanup_required' if remaining else 'finished', finished_at=now(), survivors=remaining)
                        self.runtime_json(active_path, active)
                        if remaining:
                            errors.append('Owned child group is still live; another writer is prohibited')
                except (OSError, ValueError) as error:
                    errors.append('Cleanup/status recording failed: ' + str(error))
                try:
                    changed = verify_hashes(self.root, merge_hashes(self.protected, self.controls, guarded)) + created_controls(self.root, absent)
                    if changed:
                        errors.append('Protected evidence or supervisor controls changed: ' + ', '.join(changed[:15]))
                except (OSError, ValueError) as error:
                    errors.append('Integrity verification failed: ' + str(error))
                if errors:
                    atomic_json(log.with_suffix('.integrity-failure.json'), {'changed': changed, 'errors': errors,
                        'original_error': original_error, 'snapshot_provisional_while_survivors_live': bool(remaining)})
                    raise ContinuationVeto('; '.join(errors))
        atomic_json(log.with_suffix('.process.json'), result)
        if result.get('launched') is False:
            raise BudgetDeferred('Process not launched: ' + result['reason'])
        if result['exit_code'] != 0 or result['reason']:
            error_type = (ProcessTimeout if result['reason'] in {
                'timeout', 'progress_no_ack', 'progress_stagnation',
                'progress_finish_timeout'} else MasterError)
            raise error_type(f'Command failed ({result["reason"] or result["exit_code"]}); inspect {log.relative_to(self.root)}')
        return result

    def recover_process(self):
        path = self.home / 'active-process.json'
        if not path.exists():
            return
        try:
            saved = load_json(path)
            if not isinstance(saved, dict) or saved.get('status') not in {'running', 'finished', 'cleanup_required'}:
                raise ValueError('Invalid active-process record shape or status')
            if saved['status'] != 'finished':
                identity = saved.get('identity')
                if (not isinstance(identity, dict) or
                        any(type(identity.get(k)) is not int or identity[k] <= 0 for k in ('pid', 'pgid', 'start_ticks'))):
                    raise ValueError('Incomplete prior-worker identity; inspect before resuming')
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise ContinuationVeto('Invalid prior-worker recovery record: ' + str(error)) from error
        if saved.get('status') == 'finished':
            return
        previous = saved.get('identity')
        if not previous or previous['pgid'] != previous['pid']:
            raise ContinuationVeto('Incomplete prior-worker identity; inspect before resuming')
        if not previous.get('boot_id'):
            raise ContinuationVeto('Prior worker has no boot identity; explicit ownership recovery is required')
        if previous['boot_id'] != boot_identity():
            saved.update(status='finished', survivors=[], finished_at=now(),
                         recovery='Prior host boot ended; no current process was inspected or signalled')
            atomic_json(path, saved)
            self.event('prior_worker_recovered', recovery=saved['recovery'])
            return
        current = process_identity(previous['pid'])
        if current and current['start_ticks'] != previous['start_ticks']:
            if live_group_members(previous['pgid']):
                raise ContinuationVeto('Prior PID was reused but the saved group still has members; no unrelated process was signalled')
            saved.update(status='finished', recovery='Prior PID has been reused; unrelated process was not signalled')
        elif current:
            if current['pgid'] != previous['pgid']:
                raise ContinuationVeto('Prior worker changed process group; inspect before resuming')
            try:
                stop_recovered_group(previous)
            except (ContinuationVeto, OSError) as error:
                saved.update(status='cleanup_required', recovery_error=str(error),
                             survivors=live_group_members(previous['pgid']))
                atomic_json(path, saved)
                raise
            saved.update(status='finished', recovery='Terminated positively identified prior worker group')
        elif live_group_members(previous['pgid']):
            raise ContinuationVeto('Prior worker leader is absent but its group remains; ownership requires inspection')
        else:
            saved.update(status='finished', recovery='Prior process group is no longer active')
        atomic_json(path, saved)
        self.event('prior_worker_recovered', recovery=saved['recovery'])

    def record_startup_stop(self, error, paths):
        folder = self.home / 'recovery-stops' / uuid.uuid4().hex
        folder.mkdir(parents=True)
        preserved = {}
        for path in paths:
            if path.is_file():
                destination = folder / path.name
                atomic_bytes(destination, path.read_bytes())
                preserved[str(destination.relative_to(self.root))] = digest(destination)
        record = {'status': 'continuation_veto', 'reason': str(error), 'recorded_at': now(),
                  'preserved_inputs': preserved, 'mission_complete': False, 'product_implementation_enabled': False}
        atomic_json(folder / 'stop.json', record)
        atomic_json(self.home / 'startup-stop.json', record)
        atomic_json(self.home / 'next-plan.json', {**record, 'next_phase': None, 'eligible_phases': []})
        atomic_bytes(self.home / 'next-plan.md', ('# Startup stopped\n\n' + str(error) + '\n').encode())
        self.event('run_stopped', reason=str(error), recovery_record=str((folder / 'stop.json').relative_to(self.root)))
        return record

    def worker(self, role, phase, packet, folder, attempt=0):
        role_verdicts(role)
        if phase.get('id') not in self.phases and not (phase.get('id') == 'controller' and role in {'probe', 'review_controller'}):
            raise ContinuationVeto('Worker requires a registered phase or the read-only controller review role')
        if phase['id'] in self.phases and self.phase_block(phase['id']):
            raise ContinuationVeto(self.phase_block(phase['id']))
        if (folder / f'{role}-{attempt}.response.json').exists():
            raise MasterError('Worker response destination is not fresh')
        seconds = worker_seconds(role, self.catalog['limits'])
        editable = role in {'implement', 'repair'}
        reserve = self.catalog['limits'].get('verification_reserve_seconds', 0) if editable else 0
        self.require_budget(seconds + reserve, role + ' including supervisor verification reserve')
        worker_id = f'{self.run_id}:{phase["id"]}:{role}:{attempt}:{uuid.uuid4().hex}'
        monitored = role != 'probe' and not packet.get('packet_only')
        budget = worker_budget(seconds, boot_identity(), editable=editable,
                              latest_deadline=self.deadline - reserve,
                              monitored=monitored)
        budget_path = folder / f'{role}-{attempt}.budget.json'
        if budget_path.exists():
            raise MasterError('Worker budget destination is not fresh')
        control_path = folder / f'{role}-{attempt}.control.json'
        supervision_path = folder / f'{role}-{attempt}.supervision.json'
        checkpoint_path = folder / f'{role}-{attempt}.checkpoint.json'
        budget.update(
            worker_id=worker_id, role=role, root_directory=str(self.root),
            write_scope=self.catalog['workflow']['phase_policy'].get(phase['id'], {}).get('write_scope', []),
            budget_file=str(budget_path.relative_to(self.root)),
            clock_command=['python3', str(self.root / 'scripts/accounting_worker_clock.py'), str(budget_path)])
        if monitored:
            budget.update(control_file=str(control_path.relative_to(self.root)),
                          supervision_file=str(supervision_path.relative_to(self.root)))
        atomic_json(budget_path, budget)
        # The fixed clock record is included in the inventory before launch;
        # unlike response/log files it is not a mutable generated-file exception.
        packet = {**packet, 'budget': budget}
        guarded, absent = control_snapshot(self.root, [self.state_path, self.home / 'authorization.json', self.home / 'next-plan.json', self.home / 'proposal-ready.json'])
        generated = [str((folder / f'{role}-{attempt}{suffix}').relative_to(self.root)) for suffix in
                     ('.response.json', '.schema.json', '.recovery.json', '.packet.json', '.prompt.txt', '.log',
                      '.stdin.txt', '.process.json', '.raw-negative-response.json', '.integrity-failure.json',
                      '.control.json', '.supervision.json', '.checkpoint.json')]
        generated += [str((folder / f'{role}-{attempt}.config-{i}{suffix}').relative_to(self.root))
                      for i in range(2) for suffix in ('.log', '.stderr.log', '.process.json', '.integrity-failure.json')]
        generated += ['data/accounting-master/events.jsonl', 'data/accounting-master/active-process.json',
                      'data/accounting-master/stop-request.json']
        try:
            before = worker_inventory(self.root, generated)
            editable_before = scoped_inventory(self.root, budget['write_scope']) if editable else {}
        except (ValueError, OSError) as error:
            raise ContinuationVeto('Cannot establish worker write inventory: ' + str(error)) from error
        if self.runtime_expected is not None:
            raise ContinuationVeto('Nested worker execution is prohibited')
        runtime_paths = [self.home / name for name in ('events.jsonl', 'active-process.json')]
        runtime_paths += [control_path, supervision_path, checkpoint_path]
        self.runtime_expected = {str(p.relative_to(self.root)): digest(p) if p.exists() else None for p in runtime_paths}
        stop_path = self.home / 'stop-request.json'
        stop_before = digest(stop_path) if stop_path.exists() else None
        try:
            monitor = None
            if monitored:
                monitor = ProgressMonitor(root=self.root, log=folder / f'{role}-{attempt}.log',
                    budget=budget, before_inventory=editable_before,
                    publish_control=lambda value: self.runtime_json(control_path, value),
                    publish_record=lambda value: self.runtime_json(supervision_path, value),
                    save_checkpoint=lambda value: self.save_worker_checkpoint(
                        value, phase, packet, budget_path, checkpoint_path))
            return self._worker_result(role, phase, packet, folder, attempt, progress_monitor=monitor)
        finally:
            pending_error = sys.exception()
            original_error = str(sys.exception())
            try:
                self.check_runtime()
                if stop_before is not None and (not stop_path.exists() or digest(stop_path) != stop_before):
                    raise ValueError('Existing stop request changed during worker execution')
                if stop_before is None and stop_path.exists():
                    request = load_json(stop_path)
                    if (not isinstance(request, dict) or set(request) != {'requested_at'}
                            or not isinstance(request['requested_at'], str)):
                        raise ValueError('Invalid stop request appeared during worker execution')
                    datetime.fromisoformat(request['requested_at'])
                expected = merge_hashes(self.protected, self.controls, guarded)
                changed = verify_hashes(self.root, expected) + created_controls(self.root, absent)
                after = worker_inventory(self.root, generated)
                touched = [n for n in before.keys() | after.keys() if before.get(n) != after.get(n)]
                # Also reject introduced editable symlinks or unreadable inputs.
                editable_files(self.root)
                if role not in {'implement', 'repair'}:
                    changed += touched
                elif phase['id'] in self.phases:
                    scope = self.catalog['workflow']['phase_policy'][phase['id']]['write_scope']
                    changed += [name for name in touched if not any(
                        name.startswith(s) if s.endswith('/') else name == s for s in scope)]
                if changed:
                    raise ValueError('Changed outside role/write scope: ' + ', '.join(sorted(set(changed))[:15]))
                if stop_path.exists() and pending_error is None:
                    raise MasterError('Stop requested during worker execution; response is not accepted')
            except (ValueError, OSError, ContinuationVeto) as error:
                try:
                    atomic_json(folder / f'{role}-{attempt}.integrity-failure.json',
                                {'verification_error': str(error), 'original_error': original_error})
                except OSError:
                    pass
                raise ContinuationVeto('Worker integrity failure (read-only or declared write scope): ' + str(error)) from error
            finally:
                self.runtime_expected = None

    @contextmanager
    def prepared_inputs(self, role, folder, attempt):
        paths = [folder / f'{role}-{attempt}{suffix}' for suffix in
                 ('.budget.json', '.packet.json', '.recovery.json', '.schema.json', '.prompt.txt')]
        paths += [folder / f'{role}-{attempt}.config-{i}{suffix}' for i in range(2)
                  for suffix in ('.log', '.stderr.log', '.process.json')]
        hashes, absent = control_snapshot(self.root, paths)
        try:
            yield
        finally:
            try:
                changed = verify_hashes(self.root, hashes) + created_controls(self.root, absent)
                if changed:
                    raise ValueError(', '.join(changed))
            except (OSError, ValueError) as error:
                raise ContinuationVeto('Prepared worker inputs changed: ' + str(error)) from error

    def _worker_result(self, role, phase, packet, folder, attempt=0,
                       *, progress_monitor=None):
        runtime_guard = {str(p.relative_to(self.root)): digest(p) for p in [self.state_path, self.home / 'authorization.json'] if p.exists()}
        seconds = worker_seconds(role, self.catalog['limits'])
        reserve = self.catalog['limits'].get('verification_reserve_seconds', 0) if role in {'implement', 'repair'} else 0
        cutoff = (packet['budget']['nominal_deadline_monotonic'] if progress_monitor is not None
                  else packet['budget']['deadline_monotonic'])
        def remaining_work():
            available = cutoff - time.monotonic()
            if available <= 0:
                raise BudgetDeferred('Startup consumed the worker window; preserve the supervisor verification reserve')
            return available
        available = remaining_work()
        budget = {**packet['budget'], 'available_attempt_seconds': round(available, 1),
                  'run_remaining_seconds': round(self.deadline - time.monotonic(), 1) if self.deadline != float('inf') else None,
                  'supervisor_verification_reserve_seconds': reserve,
                  'measured_at': now()}
        packet = {**packet, 'budget': budget}
        if phase['id'] in self.phases:
            recovery = phase_recovery(self.root, phase, self.state['phases'][phase['id']])
            recovery.update(role=role, attempt=attempt, budget=budget)
            destination = folder / f'{role}-{attempt}.recovery.json'
            atomic_json(destination, recovery)
            # Keep the full change inventory on disk; a broad phase must not
            # create an unbounded prompt. Criteria and current repair findings
            # remain intact in the original packet.
            compact = {**recovery, 'current_changes': recovery_excerpt(recovery['current_changes'], 2400)}
            packet['recovery'] = {**compact, 'full_record': str(destination.relative_to(self.root))}
        packet_path = folder / f'{role}-{attempt}.packet.json'
        packet['full_packet_path'] = str(packet_path.relative_to(self.root))
        atomic_json(packet_path, packet)
        if self.worker_override:
            if not self.test_only or self.root == ROOT:
                raise ContinuationVeto('Worker override is restricted to isolated test-only mode')
            with self.prepared_inputs(role, folder, attempt):
                response = self.worker_override(role, phase, packet, folder, attempt)
        else:
            grant = self.home / 'authorization.json'
            if not grant.exists() or not load_json(grant).get('sequential_workers'):
                raise MasterError('Sequential workers need the explicit upfront install-and-run grant')
            executable = shutil.which('codex')
            if not executable:
                raise MasterError('Codex CLI unavailable')
            mode = 'workspace-write' if role in {'implement', 'repair'} else 'read-only'
            destination = folder / f'{role}-{attempt}.response.json'
            if destination.exists():
                raise MasterError('Worker output path already exists; allocate a fresh invocation directory')
            schema_path = folder / f'{role}-{attempt}.schema.json'
            schema = load_json(self.root / SCHEMA)
            schema['properties']['verdict']['enum'] = sorted(role_verdicts(role))
            atomic_json(schema_path, schema)
            argv = [executable, '-a', 'never', 'exec', '--sandbox', mode, '--ephemeral',
                    '--skip-git-repo-check', '--ignore-rules', '--json', '--color', 'never',
                    '--output-schema', str(schema_path), '-o', str(destination),
                    '-C', str(self.root), '-c', 'sandbox_workspace_write.network_access=true', '-']
            # Isolate this program's workers from unrelated startup integrations.
            # Keep the user's configured model/authentication; change no global setting.
            # Ask the CLI to resolve its own effective config, including CODEX_HOME
            # and project layers. Do not copy authentication/provider configuration.
            def config_query(command, index):
                log = folder / f'{role}-{attempt}.config-{index}.log'
                self.process(command, log, min(30, remaining_work()), deadline=cutoff, separate_stderr=True)
                return load_json(log)
            servers = config_query([executable, '-C', str(self.root), 'mcp', 'list', '--json'], 0)
            names = [entry['name'] for entry in servers]
            overrides = worker_overrides(mode, {'mcp_servers': dict.fromkeys(names)}, role)
            checked = config_query([executable, '-C', str(self.root), *overrides, 'mcp', 'list', '--json'], 1)
            if any(entry.get('enabled', True) for entry in checked):
                raise MasterError('Worker integration isolation was not effective')
            argv[-1:-1] = overrides
            budget.update(available_attempt_seconds=round(remaining_work(), 1), measured_at=now())
            if remaining_work() <= budget['reserve_for_checks_and_response_seconds']:
                raise BudgetDeferred('Startup left only the finishing interval; preserve the supervisor verification reserve')
            if phase['id'] in self.phases:
                atomic_json(local_path(self.root, packet['recovery']['full_record']), recovery)
            atomic_json(packet_path, packet)
            prompt = self.prompt(role, phase, packet)
            (folder / f'{role}-{attempt}.prompt.txt').write_text(prompt)
            process_seconds = max(0.01, (progress_monitor.hard_deadline
                                         if progress_monitor is not None else cutoff)
                                 - time.monotonic())
            with self.prepared_inputs(role, folder, attempt):
                self.process(argv, folder / f'{role}-{attempt}.log', process_seconds, prompt,
                             deadline=(progress_monitor.hard_deadline if progress_monitor is not None else cutoff),
                             progress_monitor=progress_monitor)
            if not destination.exists():
                raise MasterError('Worker did not produce its structured final response')
            response = load_json(destination)
        if (isinstance(response, dict) and isinstance(response.get('verdict'), str)
                and response['verdict'] in {'REVISE', 'BLOCKED'}):
            # Preserve structured negative findings without ever promoting a
            # malformed positive response. Their JSON text retains every field.
            fields = RESPONSE_KEYS - {'verdict', 'summary'}
            if any(isinstance(response.get(k), list) and any(isinstance(x, (dict, list)) for x in response[k]) for k in fields):
                atomic_json(folder / f'{role}-{attempt}.raw-negative-response.json', response)
                response = {k: [json.dumps(x, ensure_ascii=False, sort_keys=True) if isinstance(x, (dict, list)) else x for x in v]
                            if k in fields and isinstance(v, list) else v for k, v in response.items()}
        value = validate_response(response, role_verdicts(role))
        atomic_json(folder / f'{role}-{attempt}.response.json', value)
        self.check_protection()
        if verify_hashes(self.root, runtime_guard):
            raise ContinuationVeto('Worker changed supervisor state or the upfront grant')
        return value

    def prompt(self, role, phase, packet):
        if role == 'probe':
            return 'Do not use tools or read project files. Return exactly this JSON object, with every field:\n' + json.dumps({
                'verdict': 'AGREE', 'summary': 'MASTER_WORKER_OK', 'steps': [], 'assumptions': [],
                'checks': [], 'evidence': [], 'issues': [], 'residuals': [], 'next_actions': []})
        example = json.dumps({'verdict': 'PLAN' if role == 'plan' else 'IMPLEMENTED' if role in {'implement', 'repair'} else 'AGREE',
            'summary': 'Replace with the actual finding', 'steps': [], 'assumptions': [], 'checks': [],
            'evidence': [], 'issues': [], 'residuals': [], 'next_actions': []})
        format_instruction = 'Return a JSON object with ALL these exact keys and array/string types (fill with actual findings; no extra keys): ' + example
        if role == 'review_controller' and packet.get('packet_only'):
            return '\n'.join([
                'Perform a bounded packet-only code review. Do not use tools, read files, run commands, or reread project/mission history.',
                'The user authorised this precise review scope. All code and relevant evidence for this packet are supplied below; identify any missing interface assumption explicitly.',
                'The engineering target is resumable sequential phase execution with actual repair, fresh reviewed plans, preservation of evidence and reusable narrow command approval.',
                'The accepted source panel has 192 reports; source checks and scoped internal phase acceptance must never close all accounting, scientific or human-acceptance gaps.',
                'Find concrete defects in the assigned scope and its stated interfaces. Test counts are supporting control-plane evidence, not accounting correctness.',
                'Review accidental failures, ordinary handled interruption, stale state and honest acceptance. The controller and workers are trusted; hostile multi-tenant actors, deliberate detachment and an uncatchable kill between fork and durable registration are outside the stated containment guarantee. Do not add those threat models as new acceptance requirements.',
                'Return the required JSON: AGREE only with issues=[]; otherwise REVISE with precise code-level findings and repair instructions. Put nonblocking limitations in residuals.',
                'Evidence entries may name only the supplied real file paths. Do not invent tests or assertions. Keep the response under 1500 words.',
                format_instruction,
                json.dumps({'scope': phase, 'packet': packet}, ensure_ascii=False, indent=2),
            ])
        policy = self.catalog['workflow']['phase_policy'].get(phase['id'])
        workflow_instruction = ('The current task is proposal preparation. Product implementation is disabled. '
            'Existing P00–P14 results are historical source/prototype evidence, not approval of the architecture. '
            'Read the phase design question and produce its document/research deliverable. '
            'IMPLEMENTED is the response protocol for completed work, not a product-readiness claim. '
            'Do not create or extend production modules, or add a test suite merely to certify prose. '
            'The registered supervisor checker supplies structural checks; independent review assesses substantive completeness. '
            'The artifact format is documented in docs/plans/accounting-proposal-artifact-format.md with required P18/P19 additions in docs/plans/accounting-proposal-evidence-supplement-20261005.md. '
            'Allowed project edits for this task: ' + json.dumps(policy['write_scope'])) if policy else ''
        role_instruction = ('You are ONLY reviewing the supplied current plan. Return AGREE, REVISE or BLOCKED; '
                            'do not return PLAN or replace this review with a new planning task.') if role == 'review_plan' else ''
        return '\n'.join([
            'You are a sequential worker for the user-authorised AccDSL master program.',
            f'Role: {role}. Repository: {self.root}. Phase contract follows below.',
            workflow_instruction, role_instruction,
            'Work from this current phase packet and relevant code/source evidence. The master plan preserves MC01–MC35 and G1–G18. Consult specific requirement rows when needed; do not repeat whole-project or historical gap audits.',
            'Use the supplied recovery snapshot first. It identifies current missing deliverables, changed files and the latest structured process/check/review records. Excerpts are navigation aids; inspect the linked structured records for any omitted finding that affects the work. Verify worker-authored progress against actual files.',
            'Do not dump raw worker logs, session JSONL, nested tool output or your own active log. Never recover by concatenating prior logs. If a diagnostic is absent from structured records, parse only the needed fields and return a bounded excerpt. Keep each tool response near 2000 tokens and each combined batch near 4000; retain full output on disk.',
            'Before your first substantial tool batch, run the exact argv in budget.clock_command. Run it again before EVERY substantial tool batch and after checks. It reads the same host monotonic clock as the supervisor. Never compute remaining time from measured_at, UTC, date, or wall-clock tools; civil time can drift or jump. The fixed budget_file is read-only.',
            'The clock reports work, finish, respond or expired. At finish, stop new research/drafting: save current work, run only bounded checks, update progress and respond. At respond, return the structured response immediately; do not start another tool batch. The supervisor keeps nominal_deadline_monotonic as the ordinary window and may grant a small finishing extension only after new verified progress and acknowledgement; deadline_monotonic is absolute. Plan one subsection small enough for seconds_to_save_and_check.',
            'Use budget.clock_command with additional arguments after each substantive subsection and at least within five minutes: --kind milestone (editable work) or --kind finding (read-only plan/review), --summary "concrete saved section or conclusion", --next-action "one bounded next task", --evidence repository/relative/file ... and --locator "source lines or section supporting the finding". Use literal shell quoting or a subprocess argument list. The helper hashes evidence. A milestone needs new saved substantive content; read-only findings need distinct conclusions and source locators. Clock calls, progress.md, log volume and repeated reports are not progress.',
            'Read the clock instruction and its acknowledgement deadline. On checkpoint, report concrete new progress or return your structured response before its grace expires; clock acknowledgement alone does not resolve stagnation. Editable workers should send a recovery checkpoint immediately after completing a saved bounded subsection: append --kind checkpoint, --summary, --next-action, --evidence, and --checkpoint-json with the complete response-schema PARTIAL JSON (all required keys, nonempty next_actions). Pass JSON as a literal argv value. The helper prints it and exact scoped hashes; the supervisor saves it. Do not write supervisor records. Changed files require a new checkpoint. Read-only workers cannot submit editable checkpoints. Recovery needs matching files, fresh checks and independent review; a checkpoint never accepts the phase.',
            'No agents/delegation/recursive workers. Do not launch another model or this master runner. Do not start detached/background jobs.',
            'No paid service/data, accounts, outreach, publication, deployment, global or conda package installation, Git initialization, source deletion or permission changes.',
            'Never use approval/sandbox bypass. Do not request approvals. Record inaccessible capabilities once and continue independent authorised work.',
            'Only implement/repair roles may edit project code and the phase deliverables. Planner/reviewer roles are strictly read-only.',
            'Do not edit the master controller, support module, catalog, response schema, controller tests or master plan. Under data/accounting-master you may write only your declared deliverables and the progress.md checkpoint in phase_output_dir; all other supervisor files are protected from worker edits.',
            'Do not modify data/financial-report-benchmark or any file pinned by its release manifest. Do not modify preserved pre-repair/pre-expert snapshots.',
            'Preserve unrelated work. Add new versioned modules/results instead of rewriting frozen evidence. Record all changed source/code/test files in evidence.',
            'Use only standard-library/existing packages by default. Any essential new open-source dependency must be isolated under this project, version-pinned and documented.',
            'Public-source research must use legitimate official/primary sources, preserve local copies and exact support; no challenge bypass or fabricated authority.',
            'Separate specified behaviour, implemented code, tested invariants, accounting validity, empirical forecast validity and human acceptance. All G1–G18 retain their wider obligations.',
            'Before scientific runs, write the research intent/evidence/default audit and matched baseline plan required by project policy. Short checks cannot establish superiority.',
            'For PLAN, inspect existing artifacts and produce concrete implementation steps, explicit assumptions, exact checks, risks/nonclaims and residuals. Address every supplied review finding before revising a plan.',
            'Planning must stay bounded: use a few grouped targeted reads of relevant existing inputs/interfaces, then return the executable plan. Do not perform the entire accounting analysis or implementation during planning. On recovery, use the prior approved plan and current partial work to plan the remaining repairs under every original criterion. Do not restart discovery. Keep the final plan under 1800 words.',
            ('When repair_workflow is supplied, select only the first unresolved bounded task using current checks and retained evidence. State its stop condition, required outputs and next task explicitly. Do not combine unresolved authority research with complete lifecycle implementation in one attempt. After partial work or timeout, narrow the remaining scope using the supervisor continuation/check record; do not repeat the unchanged broad plan.')
            if phase.get('continuation_policy') != 'reviewed_scope' else
            'The initial plan must sequence every remaining group in execution_plan, with outputs and stops for each. Each editable attempt executes only the first unfinished group; a saved complete group is not repeated. A material new finding requires a revised reviewed plan.',
            ('This phase continues within one reviewed scope. Read execution_plan and cover its remaining task sequence in the initial plan. '
             'On continuation, use current findings and saved substantive sections to choose the next unfinished group within that plan; '
             'do not redo completed groups. Intermediate structural checks are not substantive acceptance; full result review remains mandatory. '
             'The supervisor writes check/continuation records. Do not invent additional completion JSON, validator versions, or reporting-only acceptance prerequisites. '
             'Historical reports describe their retained input versions, not current mutable deliverables. Use the registered historical resolution checks; '
             'never recursively revalidate archived reports against current files. Current evidence references still require current hashes.')
            if phase.get('continuation_policy') == 'reviewed_scope' else '',
            'For review_plan, actively check wrong baselines, proxy promotion, missing stops, unfair comparisons, hidden assumptions, stale context, environment mismatch and whether proposed artifacts answer the question. AGREE requires no unresolved material objection.',
            'For implement/repair, execute the reviewed task and write its actual deliverables. For proposal phases, repair the specification itself and use the registered checker; do not edit controller-owned checker/tests. For an explicitly scoped probe, use meaningful tests of the named design question.',
            'Never redirect a checker onto an existing result file. Use a fresh task-local filename, validate nonempty JSON before citing it, and preserve previous evidence. Read-only reviewers may use disposable /tmp output only; never redirect into the project or rebuild project files.',
            'For implement/repair, maintain a concise progress.md in the declared output_dir after the first inspection and meaningful edits. Record checked findings, changed files, exact next checks and unfinished deliverables within 600 words. This checkpoint is partial progress, never a substitute for the required result or acceptance.',
            'For proposal writing, save each completed substantive section or group of assessments to the actual deliverable before inspecting the next group. Do not defer substantive writing until the end. Use budget.clock_command for remaining time; save current progress and return PARTIAL with the exact next task when time is short. Full-phase checks can remain incomplete while a bounded subsection is complete; report both honestly.',
            'For review_result, inspect actual code, tests, source evidence and deterministic check reports. A returned success or many tests alone is insufficient. Under bounded_partial_work, assess the completed task against its approved plan and actual artifacts, distinguish relevant failures from unfinished whole-phase criteria, and never accept the full phase. Otherwise return REVISE with actionable repairs if phase acceptance criteria fail.',
            'The supervisor dispatches independent review after returned partial work and resumes pending reviews without an editable worker. For plan, use the terminal partial-review disposition to choose the next substantive edit; do not request another assessment merely to obtain a review that the supervisor has already completed.',
            'An AGREE response must have issues=[]; put nonblocking limitations in residuals. An empty implementation or a plan-only deliverable must not pass an implementation phase.',
            'For review_controller, audit orchestration, recovery, permissions, repair, plan refresh, child-process limits and honest completion against the plan and tests. Do not change files.',
            'Every evidence entry must be an existing repository-relative FILE path, never prose, a directory or an invented artifact. Include concrete unresolved work in residuals and justified next tasks in next_actions.',
            'Return only the response schema. Verdict: PLAN for plan; AGREE/REVISE for review; IMPLEMENTED for completed phase work; PARTIAL for a completed bounded task with explicit next_actions; BLOCKED only for a real dependency preventing the stated slice. A partial-task review may AGREE on that task only when review_scope says bounded_partial_work; it does not accept the phase.',
            format_instruction,
            json.dumps({'phase': phase, 'packet': compact_worker_packet(packet)}, ensure_ascii=False, indent=2),
        ])

    def controller_review(self, folder):
        self.ensure_controller_tests(folder)
        receipt = self.home / 'controller-review.json'
        if receipt.exists():
            old = load_json(receipt)
            if old.get('verdict') == 'AGREE' and old.get('issues') == [] and old.get('controller_hashes') == self.controls:
                if old.get('review_kind') == 'supervisor_finding_adjudication':
                    dispositions = old.get('finding_dispositions', [])
                    notes = old.get('review_evidence_hashes', {})
                    if (dispositions and all(d.get('status') in {'repaired_verified', 'not_a_defect'} and d.get('reason') for d in dispositions)
                            and notes and not verify_hashes(self.root, notes)):
                        self.event('controller_review_reused', review_kind='supervisor_finding_adjudication', findings=len(dispositions))
                        return
                elif old.get('scope_reviews') and all(r.get('verdict') == 'AGREE' for r in old['scope_reviews']):
                    return
        phase = {'id': 'controller', 'name': 'Review the master program', 'criteria': [
            'The current controller and tests implement the reviewed master plan without false completion or approval bypass.',
            'Repairs execute; verification and review rerun; next plans incorporate actual findings.',
            'Processes are bounded, writes recover atomically, one writer runs, and frozen evidence is protected.']}
        health = self.worker('probe', phase, {}, folder)
        if health['verdict'] != 'AGREE' or health['summary'] != 'MASTER_WORKER_OK':
            raise ContinuationVeto('Noninteractive worker health probe did not pass')
        source = (self.root / 'scripts/run_accounting_master.py').read_text()
        tree = ast.parse(source)
        source_lines = source.splitlines()
        def excerpt(node):
            start = min([node.lineno] + [d.lineno for d in getattr(node, 'decorator_list', [])])
            return '\n'.join(source_lines[start - 1:node.end_lineno])
        functions = {n.name: excerpt(n) for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        master_node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Master')
        functions.update({'Master.' + n.name: excerpt(n) for n in master_node.body if isinstance(n, ast.FunctionDef)})
        scopes = {
            'process-lifecycle': ['exclusive_lock', 'defer_shutdown', 'terminate_group', '_terminate_group', 'boot_identity', 'process_identity', 'live_group_members', 'open_pidfd', 'catch_termination', 'bounded_process', 'stop_recovered_group', '_stop_recovered_group', 'Master.recover_process'],
            'permissions-install': ['rule_text', 'check_rule', 'atomic_rule_publish', 'install_rule', 'validate_internal', 'main'],
            'worker-boundary': ['BudgetDeferred', 'Master.require_budget', 'worker_overrides', 'worker_seconds', 'role_verdicts', 'validate_response', 'control_snapshot', 'created_controls', 'Master.process', 'Master.worker', 'Master._worker_result', 'Master.phase_review'],
            'state-refresh': ['validate_catalog', 'validate_state', 'Master.__init__', 'Master.verify_workflow', 'Master.phase_block', 'Master.reload_state', 'Master.save', 'Master.event', 'Master.check_protection', 'Master.refresh', 'Master.input_fingerprint', 'Master.review_dependencies'],
            'scheduler': ['BudgetDeferred', 'Master.require_budget', 'Master.run', 'Master.campaign', 'Master.reconcile_campaign_invocation', 'campaign_remaining', 'campaign_progress', 'Master.remaining', 'boot_identity', 'Master.recover_process', 'Master.phase_block', 'Master.proposal_gate', 'Master.review_dependencies'],
            'phase-plan-repair': ['BudgetDeferred', 'Master.require_budget', 'validate_response', 'acceptance_ready', 'Master.refresh_worker_plan', 'Master.approve_phase_plan', 'Master.save_continuation', 'Master.execute_phase', 'Master.check_phase', 'Master.load_pending_review', 'Master.save_pending_review', 'Master.phase_review', 'Master.evidence_hashes', 'Master.preserve_work', 'Master.worker'],
            'evidence': ['Master.check_protection', 'Master.evidence_hashes', 'Master.ensure_controller_tests', 'Master.capture_phase_changes', 'Master.proposal_gate', 'Master.review_dependencies'],
        }
        for name in ('worker-boundary', 'state-refresh', 'phase-plan-repair'):
            scopes[name] += ['Master.check_runtime', 'Master.runtime_json', 'Master.event']
        for name in ('worker-boundary', 'phase-plan-repair'):
            scopes[name] += ['Master.prepared_inputs', 'Master.save_worker_checkpoint', 'Master.load_supervision_checkpoint']
        scopes['process-lifecycle'] += ['terminate_unidentified_child']
        scopes['scheduler'] += ['Master.record_startup_stop']
        tests_source = '\n'.join((self.root / n).read_text() for n in
            ['tests/test_accounting_master.py','tests/test_accounting_proposal_current.py']
            if (self.root / n).exists())
        tests_tree = ast.parse(tests_source)
        test_names = [n.name for n in ast.walk(tests_tree) if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]
        full_plan = (self.root / 'docs/plans/accounting-master-program.md').read_text()
        plan_contract = (full_plan.split('Date: 2 October 2026.', 1)[0] + '\n' +
                         full_plan.split('## Evidence contract and verification', 1)[1].split('## Phase coverage and continuation', 1)[0])
        decisions = []
        for name, symbols in scopes.items():
            subfolder = folder / ('controller-' + name)
            subfolder.mkdir(exist_ok=True)
            packet = {'packet_only': True, 'scope': name,
                      'files': list(CONTROLS),
                      'code': {symbol: functions[symbol] for symbol in symbols},
                      'module_imports': '\n'.join(excerpt(n) for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))),
                      'module_entrypoint': excerpt(tree.body[-1]),
                      'constants': {'ACCEPTED': ACCEPTED, 'PUBLIC_ACTIONS': PUBLIC_ACTIONS, 'CONTROLS': CONTROLS, 'ROOT': str(self.root), 'MAX_RUN_SECONDS': MAX_RUN_SECONDS},
                      'interfaces': {
                          'worker_modes': 'implement/repair workspace-write; other roles read-only; approval never; sequential, no nested workers',
                          'protection': 'check_protection verifies current hashes of frozen release/source/research/snapshot evidence and controller files; worker checks state/grant before and after',
                          'acceptance': 'Worker phases require passing nonzero tests and read-only result-review AGREE. P00/P01 fixed operations require deterministic independent output validation with saved checks and a deterministic PASS review record, never a fabricated model AGREE. All original gaps stay open.',
                          'repair_limits': f"one initial attempt plus up to {self.catalog['limits']['max_repairs']} retries per phase execution within the run wall limit; each eligible phase is scheduled once per run; unchanged external blocks skipped until changed inputs or explicit retry",
                          'preservation': 'before editable work, preserve source/manuscript bytes; delta goes to the result reviewer; deleted tracked files fail',
                          'controller_failure': 'requires supervisor repair and fresh read-only review, never implicit approval',
                          'lifecycle_scope': 'Initial process group only. Trusted workers must not detach; this is an explicit unenforced assumption, not cgroup/malicious-worker containment.',
                          'internal_helpers': 'Only supervisor children with the live inherited lock, matching parent identity, one-use capability, active phase and fresh output may run. Parent retains the lock; child closes its validated copy.',
                          'source_protection': 'Frozen source/release/PDF/snapshot hashes are checked across child and worker failure paths. CLI query helpers are bounded read-only local configuration inspections.',
                          'per_phase_plan': 'execute_phase obtains a fresh plan and separate review_plan verdict and checks its hash around work. P15 checked partial progress can continue within that reviewed scope; failed checks or substantive findings replan. Full result review is mandatory. Builtins use a reviewed fixed-operation contract and verified inputs.',
                          'resume_semantics': 'run is explicit operator resume and may archive an existing stop. campaign repeats bounded invocations within a fixed authorized deadline; its automatic runs never archive a stop request. Integrity, repeated no-progress, missing eligibility and deadline stops require supervisor attention; no infinite restart daemon.',
                          'runtime_inputs': 'Event and active-process files are checked against exact supervisor writes. A new valid stop request is an external operator input: it always stops the worker response from being accepted; it is not attributed to an actor by file hashing. Existing stop bytes cannot change unnoticed. Deliberate same-user forgery is outside this trusted-workspace guarantee.',
                          'test_injection': 'All worker/check/builtin overrides require explicit test_only=True and an isolated root different from ROOT. The live CLI never enables this mode. Synthetic override checks are not live proposal acceptance evidence.',
                          'external_blocks': 'Unobservable external changes are deliberately not polled. A known access change is retried by the explicit --retry-blocked option, using the same approved entrypoint. Changed declared dependencies also invalidate a block signature.',
                      },
                      'verification': load_json(self.home / 'controller-tests.json') if (self.home / 'controller-tests.json').exists() else {'status': 'missing'},
                      'test_names': test_names, 'controller_hashes': self.controls,
                      'reviewed_evidence_contract_and_permission_scope': plan_contract}
            if name in {'evidence', 'phase-plan-repair', 'scheduler', 'worker-boundary'}:
                packet['support_code'] = (self.root / 'scripts/accounting_master_support.py').read_text()
            if name in {'process-lifecycle', 'worker-boundary'}:
                packet['clock_code'] = (self.root / 'scripts/accounting_worker_clock.py').read_text()
            if name in {'process-lifecycle', 'worker-boundary', 'phase-plan-repair'}:
                packet['supervision_code'] = (self.root / 'scripts/accounting_worker_supervision.py').read_text()
            if name == 'evidence':
                packet['proposal_checker'] = (self.root / 'scripts/check_accounting_proposal.py').read_text()
                packet['proposal_tests'] = (self.root / 'tests/test_accounting_proposal_current.py').read_text()
            if name in {'scheduler', 'state-refresh'}:
                packet['workflow'] = self.catalog['workflow']
                packet['proposal_contracts'] = [self.phases[p] for p in self.catalog['workflow']['proposal_phases']]
            if name == 'scheduler':
                packet['phase_planning_implementation'] = functions['Master.execute_phase']
            if name == 'permissions-install':
                grounding = self.home / 'rule-grounding.json'
                if grounding.exists():
                    packet['rule_semantics_and_actual_policy_checks'] = load_json(grounding)
            # Reuse an unchanged modular review only after the full current test
            # suite passes. Changed code/interface/contract in this scope invalidates
            # it; unrelated file hashes or an additional test do not erase the review.
            cache_material = {k: v for k, v in packet.items() if k not in {'verification', 'controller_hashes', 'test_names'}}
            cache_key = stable_hash(cache_material)
            cache = self.home / 'controller-review-cache' / (cache_key + '.json')
            if cache.exists():
                cached = load_json(cache)
                decision = validate_response(cached['response'], {'AGREE'})
                atomic_json(subfolder / 'cached-review.json', cached)
            else:
                if (self.home / 'stop-request.json').exists():
                    raise MasterError('Stop requested during controller review')
                try:
                    decision = self.worker('review_controller', {**phase, 'assigned_scope': name}, packet, subfolder)
                except ContinuationVeto:
                    raise
                except (MasterError, ValueError, OSError) as error:
                    if (self.home / 'stop-request.json').exists():
                        raise MasterError('Stop requested during controller review') from error
                    decision = {'verdict': 'BLOCKED', 'summary': 'This review did not produce an accepted verdict.',
                                'steps': [], 'assumptions': [], 'checks': [], 'evidence': [],
                                'issues': [str(error)], 'residuals': ['Retry this unchanged scope; other independent review scopes continue.'],
                                'next_actions': ['Obtain a valid review for this exact scope before phase execution.']}
                    atomic_json(subfolder / 'incomplete-review.json', decision)
                if decision['verdict'] == 'AGREE':
                    atomic_json(cache, {'packet_sha256': cache_key, 'response': decision, 'reviewed_at': now(),
                                        'original_controller_hashes': self.controls, 'current_tests_required_for_reuse': True})
            decisions.append({'scope': name, **decision})
            self.event('controller_scope_reviewed', scope=name, verdict=decision['verdict'])
        issues = [f'{d["scope"]}: {item}' for d in decisions for item in d['issues']]
        passed = all(d['verdict'] == 'AGREE' for d in decisions)
        atomic_json(receipt, {'verdict': 'AGREE' if passed else 'REVISE', 'issues': issues,
                             'scope_reviews': decisions, 'controller_hashes': self.controls, 'reviewed_at': now()})
        if not passed:
            raise ContinuationVeto('Controller review requires repair: ' + '; '.join(issues))

    def ensure_controller_tests(self, folder):
        report = self.home / 'controller-tests.json'
        expected = self.controls
        if report.exists():
            prior = load_json(report)
            atomic_json(folder / 'previous-controller-tests.json', prior)
        log = folder / 'controller-tests.log'
        self.event('controller_tests_started')
        failed = None
        try:
            test_command = '''import json, unittest
rows = []
for pattern in ("test_accounting_master.py", "test_accounting_proposal_current.py"):
    suite = unittest.TestLoader().discover("tests", pattern=pattern)
    discovered = suite.countTestCases()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    rows.append({"suite": pattern, "discovered": discovered, "run": result.testsRun,
                 "skipped": len(result.skipped), "successful": result.wasSuccessful()})
print("MASTER_TEST_SUITES=" + json.dumps(rows), flush=True)
raise SystemExit(0 if all(r["successful"] and r["run"] > r["skipped"] and r["run"] == r["discovered"] for r in rows) else 1)
'''
            self.process([sys.executable, '-c', test_command], log, 180)
        except ContinuationVeto:
            raise
        except MasterError as error:
            failed = str(error)
        text = log.read_text() if log.exists() else ''
        records = [line.removeprefix('MASTER_TEST_SUITES=') for line in text.splitlines() if line.startswith('MASTER_TEST_SUITES=')]
        suites = []
        try:
            if len(records) != 1:
                raise ValueError('Missing or repeated per-suite execution evidence')
            suites = json.loads(records[0])
            if (not isinstance(suites, list) or len(suites) != 2 or
                    {r['suite'] for r in suites} != {'test_accounting_master.py', 'test_accounting_proposal_current.py'} or
                    not all(r['successful'] is True and
                            all(type(r[k]) is int for k in ('discovered', 'run', 'skipped')) and
                            r['discovered'] == r['run'] > r['skipped'] >= 0 for r in suites)):
                raise ValueError('Every required suite must run non-skipped tests successfully')
        except (ValueError, KeyError, TypeError) as error:
            failed = failed or str(error)
        tests = sum(r.get('run', 0) for r in suites if isinstance(r, dict) and type(r.get('run')) is int) if isinstance(suites, list) else 0
        passed = failed is None
        result = {'passed': passed, 'tests': tests, 'error': failed, 'sha256': expected,
                  'suites': suites, 'log': str(log.relative_to(self.root)), 'checked_at': now()}
        atomic_json(report, result)
        atomic_json(folder / 'controller-tests.json', result)
        self.event('controller_tests_finished', passed=passed, tests=tests)
        if not passed:
            raise ContinuationVeto('Current controller tests failed; model review and phase execution are blocked')

    def check_phase(self, phase, folder):
        if self.check_override and (not self.test_only or self.root == ROOT):
            raise ContinuationVeto('Checker override is restricted to isolated test-only mode')
        if (self.home / 'stop-request.json').exists():
            result = {'passed': False, 'tests': 0, 'verification_deferred': 'stop_requested'}
            atomic_json(folder / 'checks.json', result)
            return result
        if self.check_override:
            try:
                result = self.check_override(phase, folder)
            except ContinuationVeto:
                raise
            except (MasterError, ValueError, OSError) as error:
                result = {'passed': False, 'tests': 0, 'error': str(error)}
            stale = verification_input_errors(self.root, result)
            if stale:
                result.update(passed=False, stale_check_inputs=stale)
            atomic_json(folder / 'checks.json', result)
            return result
        try:
            self.process([sys.executable, str(self.root / 'scripts/run_accounting_master.py'),
                          '_checks', '--phase', phase['id'], '--out', str(folder / 'checks.json')],
                         folder / 'checks-process.log', min(300, self.catalog['limits']['phase_seconds']), internal_phase=phase['id'])
            result = load_json(folder / 'checks.json')
        except ContinuationVeto:
            raise
        except (MasterError, ValueError, OSError) as error:
            try:
                result = load_json(folder / 'checks.json')
                if not isinstance(result, dict):
                    raise ValueError('check output is not an object')
            except (ValueError, OSError):
                result = {'passed': False, 'tests': 0}
            result.update(passed=False, error=str(error))
        missing = [str((Path(phase['output_dir']) / name)) for name in phase['deliverables']
                   if not local_path(self.root, str(Path(phase['output_dir']) / name)).is_file()]
        if missing:
            result.update(passed=False, missing_deliverables=missing)
        failures = validate_artifact_contract(self.root, phase)
        stale = verification_input_errors(self.root, result)
        if stale:
            result.update(passed=False, stale_check_inputs=stale)
        if phase.get('checker'):
            raw = folder / 'checks.checker.json'
            if (not raw.is_file() or raw.stat().st_size == 0
                    or result.get('checker_output_sha256') != digest(raw)):
                failures.append('Missing, empty or inconsistent supervisor checker capture')
        if failures:
            result.update(passed=False, artifact_errors=failures)
        if phase.get('historical_input_resolutions'):
            try:
                historical = historical_resolution_checks(self.root, phase['historical_input_resolutions'])
                result['historical_inputs'] = historical
                result['input_hashes'] = merge_hashes(result.get('input_hashes', {}), historical['input_hashes'])
            except (ValueError, OSError, KeyError, TypeError) as error:
                result.update(passed=False, historical_input_error=str(error))
        atomic_json(folder / 'checks.json', result)
        self.check_protection()
        return result

    def evidence_hashes(self, names):
        result = {}
        for name in names:
            path = local_path(self.root, name)
            if not path.is_file():
                raise MasterError(f'Missing evidence file: {name}')
            result[name] = digest(path)
        if not result:
            raise MasterError('No concrete evidence files')
        return result

    def capture_phase_changes(self, record, stage, before, entry):
        # The snapshot belongs to this actual work/check window, never to the
        # interval in which other phases or the supervisor were editing files.
        changes = changes_since(self.root, before)
        atomic_json(stage / 'changes.json', changes)
        identifier = next(k for k, value in self.state['phases'].items() if value is record)
        scope = self.catalog['workflow']['phase_policy'][identifier]['write_scope']
        outside = [name for names in changes.values() for name in names
                   if not any(name.startswith(s) if s.endswith('/') else name == s for s in scope)]
        if outside:
            raise ContinuationVeto('Phase/check wrote outside its proposal scope: ' + ', '.join(outside[:15]))
        touched = set(record['contributed_files'])
        touched.update(n for names in changes.values() for n in names)
        record['contributed_files'] = sorted(touched)
        cumulative = contributed_changes(self.root, record, entry)
        deleted = set(record.get('outstanding_deletions', [])) | set(changes['deleted']) | set(cumulative['deleted'])
        record['outstanding_deletions'] = sorted(n for n in deleted if not local_path(self.root, n).is_file())
        atomic_json(stage / 'cumulative-changes.json', cumulative)
        self.save()
        return changes, cumulative

    def phase_review(self, role, phase, packet, folder, attempt):
        """Retry unavailable review read-only; never treat timeout text as a verdict."""
        for retry in range(2):
            if (self.home / 'stop-request.json').exists():
                raise ReviewPending('Stop requested before review; checked work retained')
            if self.deadline - time.monotonic() < worker_seconds(role, self.catalog['limits']):
                raise ReviewPending('Insufficient run budget for a full review; checked work retained')
            target = folder if retry == 0 else folder / f'{role}-retry-{retry}'
            target.mkdir(parents=True, exist_ok=True)
            try:
                verdict = self.worker(role, phase, packet, target, attempt)
                return verdict, str((target / f'{role}-{attempt}.response.json').relative_to(self.root))
            except ContinuationVeto:
                raise
            except (MasterError, ValueError, OSError) as error:
                self.event('review_timeout' if isinstance(error, ProcessTimeout) else 'review_unavailable',
                           phase=phase['id'], role=role, retry=retry, reason=str(error))
                if retry == 1:
                    raise ReviewPending('Review unavailable twice; retained work needs a fresh read-only review: ' + str(error)) from error

    def review_dependencies(self, phase):
        return stable_hash({d: self.state['phases'][d].get('evidence_hashes', {}) for d in phase['deps']})

    def preserve_work(self):
        try:
            return preserve_editable(self.root, self.home / 'prior-bytes')
        except (OSError, ValueError) as error:
            raise ContinuationVeto('Cannot preserve complete editable inventory: ' + str(error)) from error

    def save_pending_review(self, phase, record, packet, stage):
        if verification_input_errors(self.root, packet['checks']):
            raise MasterError('Checked inputs changed; rerun verification before review')
        names = set(record['contributed_files']) | set(packet['work']['evidence']) | {phase['test_file']}
        names.update(packet['checks'].get('input_hashes', {}))
        names.update(str(Path(phase['output_dir']) / n) for n in phase['deliverables'])
        required = {packet['check_path'], packet['approved_plan_path'], packet['work_path']}
        names.update(required)
        absent = []
        if packet.get('review_scope') == 'bounded_partial_work':
            absent = sorted(n for n in names - required if not local_path(self.root, n).exists())
            names.difference_update(absent)
        checkpoint = {'phase_hash': stable_hash(phase), 'dependencies': self.review_dependencies(phase),
                      'absent_evidence': absent,
                      'packet': packet, 'evidence_hashes': merge_hashes(self.evidence_hashes(names),
                                                                      packet['checks'].get('input_hashes', {}))}
        path = stage / 'pending-review.json'
        atomic_json(path, checkpoint)
        record.update(pending_review=str(path.relative_to(self.root)), pending_review_sha256=digest(path))
        self.save()
        return checkpoint

    def load_pending_review(self, phase, record):
        if not record.get('pending_review'):
            return None
        try:
            path = local_path(self.root, record['pending_review'])
            if digest(path) != record.get('pending_review_sha256'):
                raise ValueError('pending review record changed')
            saved = load_json(path)
            checked = saved['packet']['checks']
            bounded = (saved['packet'].get('review_scope') == 'bounded_partial_work'
                       and saved['packet'].get('work', {}).get('verdict') in {'PARTIAL', 'IMPLEMENTED'}
                       and type(checked.get('tests')) is int and checked['tests'] > 0)
            if (saved['phase_hash'] != stable_hash(phase)
                    or saved['dependencies'] != self.review_dependencies(phase)
                    or not saved['evidence_hashes'] or verify_hashes(self.root, saved['evidence_hashes'])
                    or any(local_path(self.root, n).exists() for n in saved.get('absent_evidence', []))
                    or (not bounded and not acceptance_ready(phase, checked))
                    or record.get('outstanding_deletions')):
                raise ValueError('checked work, requirements, or prerequisite evidence changed')
            return saved['packet']
        except (OSError, ValueError, KeyError, TypeError) as error:
            self.event('pending_review_invalidated', phase=phase['id'], reason=str(error))
            record.pop('pending_review', None)
            record.pop('pending_review_sha256', None)
            return None

    def approve_phase_plan(self, phase, record, packet, folder):
        folder.mkdir(parents=True, exist_ok=True)
        for attempt in range(self.catalog['limits']['max_repairs'] + 1):
            limits = self.catalog['limits']
            self.require_budget(worker_seconds('plan', limits) + worker_seconds('review_plan', limits)
                                + worker_seconds('implement', limits) + limits.get('verification_reserve_seconds', 0),
                                'planning, plan review and useful execution')
            plan = self.worker('plan', phase, packet, folder, attempt)
            if plan['verdict'] == 'BLOCKED':
                record.update(status='blocked_external', issues=plan['issues'], residuals=plan['residuals'], next_actions=plan['next_actions'])
                return None
            plan_hash = stable_hash(plan)
            try:
                review, _ = self.phase_review('review_plan', phase, {**packet, 'plan': plan, 'plan_hash': plan_hash}, folder, attempt)
            except ReviewPending as error:
                record.update(status='needs_plan_repair', issues=[str(error)])
                return None
            if review['verdict'] == 'BLOCKED':
                record.update(status='blocked_external', issues=review['issues'], residuals=review['residuals'], next_actions=review['next_actions'])
                return None
            if review['verdict'] == 'AGREE':
                approved = {'plan': plan, 'review': review, 'plan_hash': plan_hash}
                atomic_json(folder / 'approved-plan.json', approved)
                return approved
            packet['required_plan_repairs'] = review
            self.event('plan_repair_required', phase=phase['id'], attempt=attempt, issues=review['issues'])
        record.update(status='needs_plan_repair', issues=review['issues'], residuals=review['residuals'])
        return None

    def save_continuation(self, phase, record, stage, checked, reason, next_actions):
        names = set(record['contributed_files']) | {phase['test_file']}
        names.update(checked.get('input_hashes', {}))
        check_name = str((stage / 'checks.json').relative_to(self.root))
        if (stage / 'checks.json').is_file():
            names.add(check_name)
        names.update(str(Path(phase['output_dir']) / n) for n in phase['deliverables'])
        existing = [n for n in names if local_path(self.root, n).is_file()]
        value = {'phase': phase['id'], 'recorded_at': now(), 'reason': reason,
                 'checks': checked, 'check_path': str((stage / 'checks.json').relative_to(self.root)),
                 'evidence_hashes': self.evidence_hashes(existing) if existing else {},
                 'missing_files': sorted(names - set(existing)), 'next_actions': next_actions,
                 'acceptance': False}
        value['changed_check_inputs'] = verify_hashes(self.root, checked.get('input_hashes', {}))
        if value['changed_check_inputs']:
            value['verification_requires_recheck'] = True
        path = stage / 'continuation.json'
        atomic_json(path, value)
        record.update(continuation=str(path.relative_to(self.root)), continuation_sha256=digest(path),
                      next_actions=next_actions)
        self.save()
        return value

    def save_worker_checkpoint(self, report, phase, packet, budget_path, destination):
        """Pin a cooperative PARTIAL report, without granting acceptance."""
        try:
            value = validate_response(report.get('checkpoint_response'), {'PARTIAL'})
        except MasterError as error:
            raise ValueError(str(error)) from error
        scope = self.catalog['workflow']['phase_policy'][phase['id']]['write_scope']
        snapshot = scoped_inventory(self.root, scope)
        if report.get('scoped_sha256') != inventory_hash(snapshot):
            raise ValueError('Checkpoint scoped files changed before supervisor observation')
        try:
            evidence = self.evidence_hashes(value['evidence'])
        except MasterError as error:
            raise ValueError(str(error)) from error
        if report.get('checkpoint_evidence') != evidence:
            raise ValueError('Checkpoint response evidence changed before supervisor observation')
        approved = packet.get('approved')
        if not isinstance(approved, dict) or approved.get('plan_hash') != stable_hash(approved.get('plan')):
            raise ValueError('Checkpoint has no valid approved plan')
        saved = {'schema_version': 'accdsl.worker-checkpoint.v1',
                 'worker_id': report['worker_id'], 'work': value,
                 'phase_hash': stable_hash(phase), 'dependencies': self.review_dependencies(phase),
                 'approved_hash': stable_hash(approved), 'scoped_hashes': snapshot,
                 'evidence_hashes': evidence, 'budget_path': str(budget_path.relative_to(self.root)),
                 'budget_sha256': digest(budget_path), 'saved_at': now(), 'acceptance': False}
        self.runtime_json(destination, saved)
        return str(destination.relative_to(self.root))

    def load_supervision_checkpoint(self, phase, approved, stage, role, attempt):
        """Only an unchanged checkpoint from this failed worker can be reviewed."""
        prefix = stage / f'{role}-{attempt}'
        checkpoint_path = prefix.with_suffix('.checkpoint.json')
        if not checkpoint_path.is_file():
            return None
        try:
            saved = load_json(checkpoint_path)
            supervision = load_json(prefix.with_suffix('.supervision.json'))
            process = load_json(prefix.with_suffix('.process.json'))
            budget = load_json(prefix.with_suffix('.budget.json'))
            scope = self.catalog['workflow']['phase_policy'][phase['id']]['write_scope']
            if (process.get('reason') not in {'timeout', 'progress_no_ack', 'progress_stagnation', 'progress_finish_timeout'}
                    or (self.home / 'stop-request.json').exists()
                    or prefix.with_suffix('.integrity-failure.json').exists()
                    or saved.get('schema_version') != 'accdsl.worker-checkpoint.v1'
                    or saved.get('worker_id') != budget.get('worker_id')
                    or supervision.get('worker_id') != budget.get('worker_id')
                    or supervision.get('checkpoint') != str(checkpoint_path.relative_to(self.root))
                    or saved.get('phase_hash') != stable_hash(phase)
                    or saved.get('dependencies') != self.review_dependencies(phase)
                    or saved.get('approved_hash') != stable_hash(approved)
                    or saved.get('budget_path') != str(prefix.with_suffix('.budget.json').relative_to(self.root))
                    or saved.get('budget_sha256') != digest(prefix.with_suffix('.budget.json'))
                    or saved.get('scoped_hashes') != scoped_inventory(self.root, scope)
                    or not saved.get('evidence_hashes')
                    or verify_hashes(self.root, saved['evidence_hashes'])):
                raise ValueError('Checkpoint no longer matches the failed worker, plan or scoped evidence')
            work = validate_response(saved['work'], {'PARTIAL'})
            return {'work': work, 'checkpoint_path': str(checkpoint_path.relative_to(self.root)),
                    'supervision_path': str(prefix.with_suffix('.supervision.json').relative_to(self.root))}
        except (OSError, ValueError, KeyError, TypeError, MasterError) as error:
            self.event('worker_checkpoint_invalidated', phase=phase['id'], reason=str(error))
            return None

    def execute_phase(self, phase, folder):
        identifier = phase['id']
        if self.phase_block(identifier):
            raise ContinuationVeto(self.phase_block(identifier))
        folder.mkdir(parents=True, exist_ok=True)
        record = self.state['phases'][identifier]
        atomic_json(folder / 'previous-outcome.json', {key: record.get(key) for key in
                    ('status', 'issues', 'residuals', 'stop_reason', 'execution_usage')})
        record['residuals'] = [r for r in record.get('residuals', []) if r !=
            'Repair allowance exhausted for this invocation; retain partial work and refresh the next slice.']
        record.pop('stop_reason', None)
        record['execution_usage'] = {'max_retries': self.catalog['limits']['max_repairs'],
                                     'editable_attempts': 0, 'retries_used': 0,
                                     'completed_partial_tasks': 0, 'timeouts': 0}
        if record.get('preflight_integrity'):
            failed = load_json(local_path(self.root, record['preflight_integrity']))
            unrestored = verify_hashes(self.root, failed['restore_hashes'])
            unrestored += [n for n in failed['unexpected_additions'] if (self.root / n).exists()]
            if unrestored:
                raise ContinuationVeto('Prior preflight changes need restoration: ' + ', '.join(unrestored[:15]))
            record.pop('preflight_integrity')
        if phase['kind'] != 'builtin':
            if record.get('entry_inventory_path') and 'contributed_files' not in record:
                raise ContinuationVeto('Legacy phase needs recorded contribution attribution before resume: ' + identifier)
            record.setdefault('contributed_files', [])
        record['status'] = 'running'
        record['attempts'].append(str(folder.relative_to(self.root)))
        self.save()
        self.event('phase_started', phase=identifier, name=phase['name'])
        self.check_protection()
        if phase['kind'] == 'builtin':
            fixed_plan = {'phase': phase, 'next_plan': self.refresh(),
                          'approval_kind': 'reviewed_fixed_operation_with_verified_input_hashes',
                          'controller_hashes': self.controls}
            atomic_json(folder / 'approved-plan.json', {**fixed_plan, 'plan_hash': stable_hash(fixed_plan)})
            if self.builtin_override:
                if not self.test_only or self.root == ROOT:
                    raise ContinuationVeto('Builtin override is restricted to isolated test-only mode')
                result = self.builtin_override(phase, folder)
            else:
                self.process([sys.executable, str(self.root / 'scripts/run_accounting_master.py'),
                              '_builtin', '--phase', identifier, '--out', str(folder)],
                             folder / 'builtin-process.log', self.catalog['limits']['phase_seconds'], internal_phase=identifier)
                result = load_json(folder / phase['deliverables'][0])
            if result.get('status') != 'passed':
                raise MasterError('Builtin acceptance failed')
            try:
                checked = verify_builtin(self.root, phase, folder, result)
            except (KeyError, TypeError, ValueError, OSError) as error:
                raise MasterError('Builtin output validation failed: ' + str(error)) from error
            if checked['passed'] is not True or checked['tests'] <= 0:
                raise MasterError('Builtin deterministic result review failed')
            if verification_input_errors(self.root, checked):
                raise ContinuationVeto('Builtin primary deliverable changed after verification')
            self.check_protection()
            evidence = [str(p.relative_to(self.root)) for p in folder.rglob('*') if p.is_file()]
            record.update(status=ACCEPTED, residuals=result.get('residuals', []), issues=[],
                          evidence_hashes=self.evidence_hashes(evidence), accepted_at=now(),
                          accepted_phase_hash=stable_hash(phase), accepted_dependencies=self.review_dependencies(phase))
            return
        packet = {'next_plan': self.refresh_worker_plan(), 'phase_output_dir': phase['output_dir'],
                  'prior_attempts': record['attempts'][:-1], 'prior_issues': record.get('issues', []),
                  'original_criteria': phase['criteria'], 'repair_workflow': phase.get('repair_workflow', [])}
        scoped_continuation = phase.get('continuation_policy') == 'reviewed_scope'
        if phase.get('execution_plan'):
            packet['execution_plan'] = phase['execution_plan']
        resumed = self.load_pending_review(phase, record)
        approved = resumed['approved'] if resumed else None
        if resumed:
            atomic_json(folder / 'approved-plan.json', approved)
            if 'supervisor_review_focus' in resumed:
                packet['supervisor_review_focus'] = resumed['supervisor_review_focus']
            self.event('checked_work_resumed', phase=identifier, prior_check=resumed['check_path'])
        if not resumed:
            if phase.get('checker'):
                preflight = folder / 'preflight'
                preflight.mkdir()
                before_preflight = self.preserve_work()
                atomic_json(preflight / 'pre-edit-files.json', before_preflight)
                try:
                    packet['current_checks'] = self.check_phase(phase, preflight)
                finally:
                    try:
                        preflight_changes = changes_since(self.root, before_preflight)
                        atomic_json(preflight / 'changes.json', preflight_changes)
                        if any(preflight_changes.values()):
                            failure = preflight / 'restore-required.json'
                            atomic_json(failure, {
                                'restore_hashes': {n: before_preflight[n] for n in
                                    preflight_changes['changed'] + preflight_changes['deleted']},
                                'unexpected_additions': preflight_changes['added'],
                                'prior_bytes': 'data/accounting-master/prior-bytes'})
                            record['preflight_integrity'] = str(failure.relative_to(self.root))
                            self.save()
                            raise ContinuationVeto('Read-only preflight changed project files; prior bytes preserved')
                    except (ValueError, OSError) as error:
                        raise ContinuationVeto('Preflight integrity check failed: ' + str(error)) from error
            approved = self.approve_phase_plan(phase, record, packet, folder)
        if approved is None:
            return
        packet['approved'] = approved
        if record.get('entry_inventory_path'):
            entry = load_json(local_path(self.root, record['entry_inventory_path']))
        else:
            entry = self.preserve_work()
            entry_path = folder / 'phase-entry-inventory.json'
            atomic_json(entry_path, entry)
            record['entry_inventory_path'] = str(entry_path.relative_to(self.root))
            self.save()
        packet['phase_entry_inventory'] = record['entry_inventory_path']
        execution_slots = self.catalog['limits']['max_repairs'] + 1 + int(resumed is not None)
        for attempt in range(execution_slots):
            if (self.home / 'stop-request.json').exists():
                record.update(status='interrupted', issues=['Stop requested; preserved work needs verification on resume.'])
                return
            # Internal helpers verify this persisted execution state. A partial
            # continuation temporarily changes it during replanning.
            record['status'] = 'repairing' if attempt else 'running'
            record.pop('stop_reason', None)
            self.save()
            self.check_protection()
            if stable_hash(load_json(folder / 'approved-plan.json')['plan']) != approved['plan_hash']:
                raise ContinuationVeto('Approved phase plan changed after review')
            stage = folder / f'execution-{attempt}'
            stage.mkdir()
            atomic_json(stage / 'approved-plan.json', approved)
            role = 'implement' if attempt == 0 else 'repair'
            reuse_work = resumed is not None and attempt == 0
            self.event('verification_resumed' if reuse_work else 'proposal_repair_started' if attempt else 'proposal_work_started', phase=identifier, attempt=attempt)
            try:
                before = self.preserve_work()
                atomic_json(stage / 'pre-edit-files.json', before)
                work_error = None
                work_timed_out = False
                work = None
                try:
                    if reuse_work:
                        work = resumed['work']
                        work_path = stage / 'resumed-work.response.json'
                        atomic_json(work_path, work)
                    else:
                        self.require_budget(worker_seconds(role, self.catalog['limits']) +
                                            self.catalog['limits'].get('verification_reserve_seconds', 0),
                                            'editable work and supervisor verification reserve')
                        usage = record['execution_usage']
                        usage['editable_attempts'] += 1
                        usage['retries_used'] = max(0, usage['editable_attempts'] - 1)
                        self.save()
                        try:
                            work = self.worker(role, phase, packet, stage, attempt)
                        except BudgetDeferred:
                            # Startup refusal occurs before the editable process.
                            usage['editable_attempts'] -= 1
                            usage['retries_used'] = max(0, usage['editable_attempts'] - 1)
                            self.save()
                            raise
                        work_path = stage / f'{role}-{attempt}.response.json'
                except BudgetDeferred:
                    raise
                except ContinuationVeto:
                    raise
                except (MasterError, ValueError, OSError) as error:
                    work_error = f'{type(error).__name__}: {error}'
                    work_timed_out = isinstance(error, ProcessTimeout)
                    record['execution_usage']['timeouts'] += int(work_timed_out)
                finally:
                    changes, cumulative = self.capture_phase_changes(record, stage, before, entry)
                if stable_hash(load_json(folder / 'approved-plan.json')['plan']) != approved['plan_hash']:
                    raise ContinuationVeto('Implementation changed its approved plan')
                recovered_checkpoint = None
                if work is None and work_timed_out and not (self.home / 'stop-request.json').exists():
                    recovered_checkpoint = self.load_supervision_checkpoint(phase, approved, stage, role, attempt)
                    if recovered_checkpoint is not None:
                        work = recovered_checkpoint['work']
                        work_path = stage / 'recovered-work.response.json'
                        atomic_json(work_path, work)
                        self.event('worker_partial_checkpoint_recovered', phase=identifier,
                                   attempt=attempt, checkpoint_path=recovered_checkpoint['checkpoint_path'],
                                   original_process_error=work_error)
                        # The failed process remains failed in its own record.
                        # Recovery only supplies a candidate PARTIAL for fresh
                        # checks and ordinary independent bounded review.
                        atomic_json(stage / 'checkpoint-recovery.json', {
                            'original_process_error': work_error,
                            'checkpoint_path': recovered_checkpoint['checkpoint_path'],
                            'supervision_path': recovered_checkpoint['supervision_path'],
                            'acceptance': False})
                        work_error = None
                if record['outstanding_deletions']:
                    raise MasterError('Restore prohibited phase deletions before acceptance: ' + ', '.join(record['outstanding_deletions']))
                try:
                    checked = self.check_phase(phase, stage)
                finally:
                    changes, cumulative = self.capture_phase_changes(record, stage, before, entry)
                if record['outstanding_deletions']:
                    raise MasterError('Verification deleted preserved project files: ' + ', '.join(record['outstanding_deletions']))
                packet['current_checks'] = checked
                if recovered_checkpoint and self.load_supervision_checkpoint(phase, approved, stage, role, attempt) is None:
                    work = None
                    work_error = 'Recovered checkpoint changed during fresh verification; repair from current files.'
                if (work_error or work['verdict'] in {'PARTIAL', 'BLOCKED'}
                        or (reuse_work and resumed.get('review_scope') == 'bounded_partial_work')
                        or (phase.get('checker') and checked.get('passed') is True and not acceptance_ready(phase, checked))):
                    reason = work_error or work['summary']
                    actions = (work['next_actions'] if work else []) or ['Plan one smaller remaining task from the current checks and preserved changes.']
                    continuation = self.save_continuation(phase, record, stage, checked, reason, actions)
                    if work and work['verdict'] == 'BLOCKED':
                        record.update(status='blocked_external', issues=work['issues'], residuals=work['residuals'], next_actions=work['next_actions'])
                        return
                    partial_review = None
                    if (not scoped_continuation and work and not work_error
                            and type(checked.get('tests')) is int and checked['tests'] > 0):
                        partial_packet = {**packet, 'work': work, 'checks': checked,
                            'review_scope': 'bounded_partial_work', 'continuation': continuation,
                            'actual_changes': changes, 'cumulative_changes': cumulative,
                            'work_path': str(work_path.relative_to(self.root)),
                            'approved_plan_path': str((stage / 'approved-plan.json').relative_to(self.root)),
                            'preserved_inputs': str((stage / 'pre-edit-files.json').relative_to(self.root)),
                            'check_path': str((stage / 'checks.json').relative_to(self.root))}
                        checkpoint = self.save_pending_review(phase, record, partial_packet, stage)
                        try:
                            partial_review, partial_review_path = self.phase_review(
                                'review_result', phase, partial_packet, stage, attempt)
                        except ReviewPending as error:
                            record.update(status='needs_review', issues=[str(error)],
                                next_actions=['Resume the saved bounded review read-only; do not reimplement or repeat the assessment.'])
                            return
                        if verify_hashes(self.root, checkpoint['evidence_hashes']):
                            raise ContinuationVeto('Checked partial work changed during read-only review')
                        record.pop('pending_review', None)
                        record.pop('pending_review_sha256', None)
                        record['last_partial_review'] = {
                            'path': partial_review_path, 'sha256': digest(local_path(self.root, partial_review_path)),
                            'verdict': partial_review['verdict'], 'scope': 'bounded_partial_work'}
                        packet.pop('supervisor_review_focus', None)
                        actions = partial_review['next_actions'] or [
                            'Use the terminal bounded review to plan the next substantive task; do not repeat the completed review.']
                        reason = 'Bounded result review ' + partial_review['verdict'] + ': ' + partial_review['summary']
                        continuation = self.save_continuation(phase, record, stage, checked, reason, actions)
                        if partial_review and partial_review['verdict'] == 'BLOCKED':
                            record.update(status='blocked_external', issues=partial_review['issues'],
                                          residuals=partial_review['residuals'], next_actions=partial_review['next_actions'])
                            return
                    file_progress = any(n != str(Path(phase['output_dir']) / 'progress.md')
                                        for names in changes.values() for n in names)
                    # A resumed terminal review advances the work without an edit.
                    progress = file_progress or (reuse_work and partial_review is not None)
                    if progress and work and work['verdict'] == 'PARTIAL' and checked.get('passed') is True:
                        record['execution_usage']['completed_partial_tasks'] += 1
                    record['no_progress_count'] = 0 if progress else record.get('no_progress_count', 0) + 1
                    issues = [reason] + (partial_review['issues'] if partial_review else work['issues'] if work else [])
                    packet['repair_findings'] = {'continuation': continuation, 'partial_review': partial_review,
                                                'work': work,
                                                'required_action': 'Fresh reviewed plan for one smaller unresolved task.'}
                    record.update(status='needs_repair', issues=issues)
                    self.save()
                    self.event('partial_work_checked', phase=identifier, attempt=attempt, passed=checked.get('passed'), progress=progress)
                    if not progress:
                        record['status'] = 'needs_plan_repair'
                        record['stop_reason'] = 'no_file_progress'
                        if record['no_progress_count'] >= 2:
                            record['deferred_signature'] = self.input_fingerprint(identifier)
                            record['issues'].append('Repeated unchanged partial failure deferred until relevant inputs change or explicit --retry-blocked.')
                        if not scoped_continuation or record['no_progress_count'] >= 2:
                            return
                    if attempt == execution_slots - 1:
                        record['stop_reason'] = 'retry_limit'
                        return
                    packet['next_plan'] = self.refresh_worker_plan()
                    if (scoped_continuation and progress and checked.get('passed') is True
                            and checked.get('tests', 0) > 0 and (not work_error or work_timed_out)
                            and (not work or not work['issues'])):
                        packet['repair_findings']['required_action'] = (
                            'Continue the first unfinished substantive group within the existing reviewed scope. '
                            'Use current checks and saved files. No additional completion record is required; '
                            'full phase result review remains outstanding.')
                        packet['continuation_of_reviewed_scope'] = True
                        record.pop('stop_reason', None)
                        self.event('reviewed_scope_continued', phase=identifier, attempt=attempt,
                                   reason='Checked file progress; substantive acceptance pending')
                        continue
                    packet.pop('continuation_of_reviewed_scope', None)
                    approved = self.approve_phase_plan(phase, record, packet, folder / f'replan-{attempt + 1}')
                    if approved is None:
                        return
                    atomic_json(folder / 'approved-plan.json', approved)
                    packet['approved'] = approved
                    continue
                review_packet = {**packet, 'work': work, 'checks': checked, 'actual_changes': changes,
                     'cumulative_changes': cumulative,
                     'work_path': str(work_path.relative_to(self.root)),
                     'approved_plan_path': str((stage / 'approved-plan.json').relative_to(self.root)),
                     'preserved_inputs': str((stage / 'pre-edit-files.json').relative_to(self.root)),
                     'check_path': str((stage / 'checks.json').relative_to(self.root))}
                checkpoint = None
                record.pop('pending_review', None)
                record.pop('pending_review_sha256', None)
                if acceptance_ready(phase, checked):
                    checkpoint = self.save_pending_review(phase, record, review_packet, stage)
                try:
                    response, review_path = self.phase_review('review_result', phase, review_packet, stage, attempt)
                except ReviewPending as error:
                    if checkpoint is not None:
                        record.update(status='needs_review', issues=[str(error)],
                                      next_actions=['Resume unchanged checked work for read-only review; do not reimplement without a finding.'])
                        return
                    raise MasterError('Checks failed and review is unavailable; repair the failed checks') from error
                if checkpoint is not None and verify_hashes(self.root, checkpoint['evidence_hashes']):
                    raise ContinuationVeto('Checked phase evidence changed during read-only review')
                record.pop('pending_review', None)
                record.pop('pending_review_sha256', None)
                if stable_hash(load_json(folder / 'approved-plan.json')['plan']) != approved['plan_hash']:
                    raise ContinuationVeto('Result review changed the approved plan')
                if response['verdict'] == 'BLOCKED':
                    record.update(status='blocked_external', issues=response['issues'], residuals=response['residuals'], next_actions=response['next_actions'])
                    return
                if acceptance_ready(phase, checked) and response['verdict'] == 'AGREE':
                    if verification_input_errors(self.root, checked):
                        raise MasterError('Checked inputs changed before acceptance; rerun verification')
                    names = set(work['evidence']) | set(response['evidence']) | {phase['test_file']}
                    names.update(checked.get('input_hashes', {}))
                    names.update(record['contributed_files'])
                    names.update(str(Path(phase['output_dir']) / n) for n in phase['deliverables'])
                    names.add(str((stage / 'checks.json').relative_to(self.root)))
                    names.add(str((folder / 'approved-plan.json').relative_to(self.root)))
                    names.add(review_path)
                    for evidence_path in (stage / 'checks.checker.json', stage / 'checks-process.process.json',
                                          local_path(self.root, review_path.replace('.response.json', '.process.json'))):
                        if evidence_path.is_file():
                            names.add(str(evidence_path.relative_to(self.root)))
                    record.update(status=ACCEPTED, issues=[], stop_reason='accepted', accepted_at=now(),
                                  accepted_phase_hash=stable_hash(phase), accepted_dependencies=self.review_dependencies(phase),
                                  residuals=list(dict.fromkeys(work['residuals'] + response['residuals'])),
                                  next_actions=list(dict.fromkeys(work['next_actions'] + response['next_actions'])),
                                  accepted_review_path=review_path,
                                  evidence_hashes=merge_hashes(self.evidence_hashes(names), checked.get('input_hashes', {})))
                    return
                packet['repair_findings'] = {'checks': checked, 'result_review': response, 'work': work}
                issues = checked.get('missing_deliverables', []) + response['issues']
                if not acceptance_ready(phase, checked):
                    issues.append('Machine checks do not establish all declared phase criteria.')
            except (ContinuationVeto, BudgetDeferred):
                raise
            except (MasterError, ValueError, OSError) as error:
                issues = [str(error)]
                packet['repair_findings'] = {'execution_error': str(error)}
            record.update(status='repairing', issues=issues)
            self.save()
            self.event('verification_requires_repair', phase=identifier, attempt=attempt, issues=issues)
            if attempt < execution_slots - 1:
                packet['next_plan'] = self.refresh_worker_plan()
                packet.pop('continuation_of_reviewed_scope', None)
                approved = self.approve_phase_plan(phase, record, packet, folder / f'replan-{attempt + 1}')
                if approved is None:
                    return
                atomic_json(folder / 'approved-plan.json', approved)
                packet['approved'] = approved
        record.update(status='needs_repair', issues=issues, stop_reason='retry_limit')
        if record.get('outstanding_deletions'):
            raise ContinuationVeto('Phase left prohibited deletions unresolved; preserve the entry inventory and repair before continuing')

    def reconcile_campaign_invocation(self, campaign):
        """Consume only a terminal result published under the runner lock."""
        pending = campaign.get('pending_invocation')
        if pending is None:
            return None
        if (not isinstance(pending, dict) or not isinstance(pending.get('id'), str) or not pending['id']
                or not isinstance(pending.get('run_id'), str)
                or not re.fullmatch(r'[0-9]{8}T[0-9]{6}-[0-9a-f]{8}', pending['run_id'])):
            raise ContinuationVeto('Invalid pending campaign run identity')
        run_id = pending['run_id']
        name = 'data/accounting-master/runs/' + run_id
        with exclusive_lock(self.home / 'runner.lock'):
            path = local_path(self.root, name) / 'manifest.json'
            if not path.is_file():
                raise ContinuationVeto('Pending invocation has no start record; supervisor must reconcile it before new work')
            manifest = load_json(path)
            if not manifest.get('startup_stop'):
                self.recover_process()
            result = manifest.get('campaign_result')
            if (not isinstance(result, dict) or result.get('invocation_id') != pending['id']
                    or result.get('run') != name or manifest.get('run_id') != run_id
                    or manifest.get('campaign_invocation_id') != pending['id']
                    or manifest.get('outcome') != result.get('outcome')
                    or not manifest.get('finished_at') or type(result.get('progress')) is not bool
                    or not isinstance(result.get('eligible_phases'), list)):
                raise ContinuationVeto('Pending invocation has no complete bound outcome; preserve it for supervisor recovery')
            entry = {**result, 'manifest_sha256': digest(path)}
            existing = [r for r in campaign['invocations'] if r.get('invocation_id') == pending['id']]
            if existing:
                if len(existing) != 1 or existing[0] != entry:
                    raise ContinuationVeto('Conflicting campaign invocation accounting')
            else:
                campaign['invocations'].append(entry)
                campaign['consecutive_no_progress'] = (0 if result['progress'] else
                                                       campaign['consecutive_no_progress'] + 1)
            campaign['pending_invocation'] = None
            outcome = result['outcome']
            if outcome == 'proposal_reviewed_implementation_held':
                try:
                    self.reload_state()
                    if (self.root / 'data/financial-report-benchmark/release-manifest.json').exists():
                        self.protected = merge_hashes(self.protected, protected_hashes(self.root))
                    elif not self.test_only:
                        raise ContinuationVeto('Required accepted-source release manifest is absent')
                    self.check_protection()
                    gate = self.proposal_gate()
                    if not gate['ready']:
                        raise ContinuationVeto(gate.get('reason', 'Current proposal evidence is no longer ready'))
                except (MasterError, ValueError, OSError) as error:
                    campaign.update(status='needs_supervisor_repair', reason='Historical readiness is no longer current: ' + str(error))
                else:
                    campaign.update(status='proposal_ready', reason='Historical success and current proposal evidence agree')
            elif outcome in {'stop_requested', 'interrupted', 'continuation_veto'}:
                campaign.update(status=outcome, reason=result.get('stop_reason') or outcome)
            elif outcome not in {'phase_limit', 'budget_exhausted', 'wall_limit',
                                 'remaining_work_requires_repair_or_dependency'}:
                campaign.update(status='needs_supervisor_repair', reason='Unexpected invocation outcome: ' + outcome)
            elif not result['eligible_phases']:
                campaign.update(status='needs_supervisor_repair', reason='No eligible phase in completed invocation result')
            campaign.update(remaining_seconds=round(campaign_remaining(campaign), 3), updated_at=now())
            atomic_json(self.home / 'campaign.json', campaign)
            return entry

    def campaign(self, seconds=172800, max_phases=15, require_review=True):
        """Continue authorized proposal invocations under one durable deadline."""
        with exclusive_lock(self.home / 'campaign.lock'):
            path = self.home / 'campaign.json'
            campaign = None
            try:
                if path.exists():
                    campaign = load_json(path)
                else:
                    started = time.monotonic()
                    campaign = {'schema_version': 'accdsl.master.campaign.v1', 'status': 'prepared',
                        'started_at': now(), 'started_monotonic': started,
                        'deadline_monotonic': started + seconds, 'allowance_seconds': seconds,
                        'boot_id': boot_identity(), 'invocations': [], 'consecutive_no_progress': 0,
                        'plan': 'docs/plans/accounting-master-campaign-20261005.md',
                        'mission_complete': False, 'product_implementation_enabled': False}
                campaign_remaining(campaign)  # Resume never silently grants more time.
                if (not isinstance(campaign.get('invocations'), list)
                        or type(campaign.get('consecutive_no_progress')) is not int
                        or campaign['consecutive_no_progress'] < 0):
                    raise ContinuationVeto('Invalid campaign progress record')
            except (MasterError, ValueError, OSError, KeyError, TypeError, AttributeError) as error:
                record = self.record_startup_stop(error, [path])
                campaign = dict(campaign) if isinstance(campaign, dict) else {}
                campaign.update(status='continuation_veto', reason=str(error), supervisor=None,
                                startup_recovery=record, allowance_reset=False)
                atomic_json(path, campaign)
                return 'continuation_veto'
            if campaign.get('status') == 'budget_exhausted':
                return 'budget_exhausted'
            if campaign.get('status') == 'proposal_ready':
                with exclusive_lock(self.home / 'runner.lock'):
                    self.reload_state()
                    if self.proposal_gate()['ready']:
                        return 'proposal_ready'
                campaign.update(status='needs_supervisor_repair', reason='Prior campaign readiness no longer matches current evidence')
                atomic_json(path, campaign)
                return campaign['status']
            campaign.update(status='running', supervisor=process_identity(os.getpid()), resumed_at=now(), reason=None)
            atomic_json(path, campaign)
            limits = self.catalog['limits']
            admission = (worker_seconds('plan', limits) + worker_seconds('review_plan', limits)
                         + worker_seconds('implement', limits)
                         + limits.get('verification_reserve_seconds', 0) + 180)
            try:
                # A completed run may have outlived its caller's final update.
                # Reconcile it before any budget/no-progress/admission decision.
                self.reconcile_campaign_invocation(campaign)
                while campaign['status'] == 'running':
                    remaining = campaign_remaining(campaign)
                    campaign['remaining_seconds'] = round(remaining, 3)
                    if (self.home / 'stop-request.json').exists():
                        campaign['status'] = 'stop_requested'
                        break
                    if campaign['consecutive_no_progress'] >= 2:
                        campaign['status'] = 'needs_supervisor_repair'
                        campaign['reason'] = 'Two invocations without substantive file or new phase-acceptance progress'
                        break
                    if remaining < admission:
                        campaign['status'] = 'budget_exhausted'
                        campaign['reason'] = f'Need {admission:g} seconds for startup and a full useful cycle; have {remaining:.1f}'
                        break
                    allowance = min(MAX_RUN_SECONDS, limits.get('run_seconds', MAX_RUN_SECONDS), int(remaining))
                    pending = {'id': uuid.uuid4().hex,
                        'run_id': datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8],
                        'scheduled_at': now()}
                    campaign.update(next_invocation_seconds=allowance, updated_at=now(), pending_invocation=pending)
                    atomic_json(path, campaign)
                    self.run(max_phases=max_phases, seconds=allowance,
                             require_review=require_review, resume_stop=False,
                             campaign_deadline=campaign['deadline_monotonic'], campaign_invocation=pending)
                    result = self.reconcile_campaign_invocation(campaign)
                    self.event('campaign_invocation_accounted', previous_outcome=result['outcome'],
                               remaining_seconds=campaign['remaining_seconds'], progress=result['progress'])
            except (MasterError, ValueError, OSError, KeyboardInterrupt) as error:
                campaign.update(status='continuation_veto' if isinstance(error, ContinuationVeto) else 'interrupted',
                                reason=f'{type(error).__name__}: {error}')
            finally:
                campaign.update(updated_at=now(), supervisor=None)
                atomic_json(path, campaign)
            self.event('campaign_finished', status=campaign['status'], invocations=len(campaign['invocations']))
            return campaign['status']

    def run(self, max_phases=15, seconds=7200, require_review=True, retry_blocked=False,
            resume_stop=True, campaign_deadline=float('inf'), campaign_invocation=None):
        if any(x is not None for x in (self.worker_override, self.check_override, self.builtin_override)) and (not self.test_only or self.root == ROOT):
            raise ContinuationVeto('Overrides are restricted to isolated test-only mode')
        if type(seconds) not in (float, int) or not 0 < seconds <= MAX_RUN_SECONDS:
            raise MasterError('An ordinary invocation requires 0 < seconds <= 7200')
        with exclusive_lock(self.home / 'runner.lock') as lock_fd:
            self.lock_fd = lock_fd
            startup_run = (campaign_invocation.get('run_id') if isinstance(campaign_invocation, dict) else None)
            if not isinstance(startup_run, str) or not re.fullmatch(r'[0-9]{8}T[0-9]{6}-[0-9a-f]{8}', startup_run):
                startup_run = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8]
            self.run_id = startup_run
            try:
                self.recover_process()
                self.reload_state()
            except (MasterError, ValueError, OSError, KeyError, TypeError, AttributeError) as error:
                stopped = self.record_startup_stop(error, [self.home / 'active-process.json', self.state_path])
                folder = self.home / 'runs' / startup_run
                folder.mkdir(parents=True)
                manifest = {'run_id': startup_run, 'outcome': 'continuation_veto', 'finished_at': now(),
                            'stop_reason': str(error), 'phases_attempted': [], 'startup_stop': stopped,
                            'campaign_invocation_id': campaign_invocation.get('id') if campaign_invocation else None}
                if campaign_invocation:
                    manifest['campaign_result'] = {'invocation_id': campaign_invocation['id'],
                        'run': str(folder.relative_to(self.root)), 'outcome': 'continuation_veto',
                        'stop_reason': str(error), 'completed_at': manifest['finished_at'],
                        'progress': False, 'accepted_phases': [], 'changed_files': [], 'eligible_phases': []}
                atomic_json(folder / 'manifest.json', manifest)
                return 'continuation_veto'
            before_accepted = {p for p, r in self.state['phases'].items() if r['status'] == ACCEPTED}
            if campaign_invocation is not None:
                current = load_json(self.home / 'campaign.json')
                if (not isinstance(campaign_invocation, dict)
                        or not isinstance(campaign_invocation.get('run_id'), str)
                        or not re.fullmatch(r'[0-9]{8}T[0-9]{6}-[0-9a-f]{8}', campaign_invocation['run_id'])
                        or not campaign_invocation.get('id')
                        or current.get('pending_invocation') != campaign_invocation):
                    raise ContinuationVeto('Campaign invocation is not durably scheduled')
                self.run_id = campaign_invocation['run_id']
            else:
                self.run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8]
            folder = self.home / 'runs' / self.run_id
            folder.mkdir(parents=True)
            self.deadline = min(time.monotonic() + seconds, campaign_deadline)
            self.protected = {}
            for record in self.state['phases'].values():
                if record['status'] in {'running', 'repairing'}:
                    record['status'] = 'interrupted'
                    record['issues'] = ['Prior process ended before acceptance; review actual partial work before resuming.']
                if retry_blocked and record['status'] == 'blocked_external':
                    record['status'] = 'pending'
                if retry_blocked:
                    record.pop('deferred_signature', None)
                    record.pop('no_progress_count', None)
            stop = self.home / 'stop-request.json'
            if stop.exists() and resume_stop:
                stop.rename(folder / 'prior-stop-request.json')
            manifest = {'run_id': self.run_id, 'started_at': now(), 'command': sys.argv,
                        'campaign_invocation_id': campaign_invocation['id'] if campaign_invocation else None,
                        'baseline_accepted': sorted(before_accepted),
                        'python': sys.executable, 'python_version': sys.version, 'controller_hashes': self.controls,
                        'catalog_sha256': digest(self.root / CATALOG), **git_provenance(self.root),
                        'device': 'CPU; CUDA_VISIBLE_DEVICES=-1 in child commands',
                        'seeds': 'N/A for controller; scientific phases must declare their own',
                        'max_phases': max_phases, 'wall_limit_seconds': seconds,
                        'deadline_monotonic': self.deadline,
                        'plan': 'docs/plans/accounting-master-program.md', 'mission_complete': False,
                        'workflow_mode': self.catalog['workflow']['mode'], 'product_implementation_enabled': False}
            tried = set()
            outcome = 'stopped'
            initialized = False
            try:
                atomic_json(folder / 'manifest.json', manifest)
                self.state['runs'].append(str(folder.relative_to(self.root)))
                self.refresh()
                initialized = True
                release = self.root / 'data/financial-report-benchmark/release-manifest.json'
                if release.exists():
                    self.protected = protected_hashes(self.root)
                    manifest['protection_scope'] = 'accepted_release_sources_and_historical_evidence'
                elif self.worker_override is not None and self.check_override is not None:
                    manifest['protection_scope'] = 'isolated_injected_control_plane_test_only'
                else:
                    raise ContinuationVeto('Required accepted-source release manifest is absent')
                atomic_json(folder / 'manifest.json', manifest)
                self.check_protection()
                if require_review and not stop.exists():
                    self.controller_review(folder)
                while len(tried) < max_phases and time.monotonic() < self.deadline and not stop.exists():
                    plan = self.refresh()
                    candidates = [x for x in plan['eligible_phases'] if x not in tried]
                    if not candidates:
                        break
                    identifier = candidates[0]
                    tried.add(identifier)
                    try:
                        self.execute_phase(self.phases[identifier], folder / identifier)
                    except BudgetDeferred as error:
                        record = self.state['phases'][identifier]
                        record.update(status='budget_deferred', stop_reason='budget_exhausted', issues=[str(error)])
                        atomic_json(folder / identifier / 'budget-stop.json', {
                            'reason': str(error), 'execution_usage': record.get('execution_usage', {}),
                            'continuation': record.get('continuation'), 'next_actions': record.get('next_actions', []),
                            'acceptance': False, 'recorded_at': now()})
                    except ContinuationVeto:
                        raise
                    except MasterError as error:
                        self.state['phases'][identifier].update(status='needs_repair', issues=[f'{type(error).__name__}: {error}'])
                    except Exception as error:
                        raise ContinuationVeto(f'Unexpected controller failure in {identifier}: {type(error).__name__}: {error}') from error
                    record = self.state['phases'][identifier]
                    unresolved = [n for r in self.state['phases'].values()
                                  for n in r.get('outstanding_deletions', [])
                                  if not local_path(self.root, n).is_file()]
                    if unresolved:
                        raise ContinuationVeto('Phase left prohibited deletions unresolved: ' + ', '.join(unresolved[:15]))
                    if record['status'] == 'blocked_external':
                        record['block_signature'] = self.input_fingerprint(identifier)
                    self.state['last_outcome'] = {'phase': identifier, 'status': record['status'],
                                                  'issues': record.get('issues', []), 'residuals': record.get('residuals', []),
                                                  'stop_reason': record.get('stop_reason', record['status']),
                                                  'execution_usage': record.get('execution_usage', {})}
                    self.event('phase_finished', phase=identifier, status=record['status'])
                    refreshed = self.refresh()
                    self.event('next_plan_refreshed', previous_phase=identifier, next_phase=refreshed['next_phase'])
                    if record['status'] == 'budget_deferred':
                        break
                if stop.exists():
                    outcome = 'stop_requested'
                elif time.monotonic() >= self.deadline:
                    outcome = 'wall_limit'
                elif any(self.state['phases'][p]['status'] == 'budget_deferred' for p in tried):
                    outcome = 'budget_exhausted'
                elif self.proposal_gate()['ready']:
                    outcome = 'proposal_reviewed_implementation_held'
                elif all(p['status'] == ACCEPTED for p in self.state['phases'].values()):
                    outcome = 'catalog_slices_accepted_mission_open'
                elif len(tried) >= max_phases:
                    outcome = 'phase_limit'
                else:
                    outcome = 'remaining_work_requires_repair_or_dependency'
            except (ContinuationVeto, MasterError, ValueError, OSError, KeyboardInterrupt) as error:
                outcome = 'continuation_veto' if isinstance(error, ContinuationVeto) else 'interrupted'
                for record in self.state['phases'].values():
                    if record['status'] in {'running', 'repairing'}:
                        record.update(status='interrupted', issues=[str(error)])
                self.event('run_stopped', reason=str(error))
                manifest['stop_reason'] = str(error)
            finally:
                with defer_shutdown():
                    try:
                        if initialized:
                            self.refresh()
                        else:
                            self.save()
                            atomic_json(self.home / 'next-plan.json', {'mission_complete': False,
                                'next_phase': None, 'eligible_phases': [], 'status': outcome,
                                'reason': manifest.get('stop_reason', 'Run initialization did not complete'),
                                'state_sha256': digest(self.state_path)})
                            atomic_bytes(self.home / 'next-plan.md', b'# Run initialization interrupted\n\nResume verifies current state before selecting work.\n')
                    except (ContinuationVeto, ValueError, OSError) as error:
                        # Preserve a stop without publishing an executable plan from
                        # controls that failed their integrity check.
                        outcome = 'continuation_veto'
                        manifest['stop_reason'] = str(error)
                        self.save()
                        atomic_json(self.home / 'next-plan.json', {'mission_complete': False,
                            'next_phase': None, 'eligible_phases': [], 'status': 'continuation_veto',
                            'reason': str(error), 'state_sha256': digest(self.state_path)})
                        atomic_bytes(self.home / 'next-plan.md', ('# Execution stopped\n\n' + str(error) + '\n').encode())
                    manifest.update(finished_at=now(), outcome=outcome, phases_attempted=sorted(tried),
                                    phase_states={k: v['status'] for k, v in self.state['phases'].items()})
                    if campaign_invocation:
                        manifest['campaign_result'] = {
                            'invocation_id': campaign_invocation['id'], 'run': str(folder.relative_to(self.root)),
                            'outcome': outcome, 'completed_at': manifest['finished_at'],
                            'stop_reason': manifest.get('stop_reason'),
                            **campaign_progress(self.root, folder, before_accepted, self.state),
                            'eligible_phases': load_json(self.home / 'next-plan.json').get('eligible_phases', [])}
                    atomic_json(folder / 'manifest.json', manifest)
                    self.event('run_finished', outcome=outcome, manifest=str((folder / 'manifest.json').relative_to(self.root)))
            return outcome


def validate_internal(master, args, out):
    if args.lock_fd is None or not args.grant or not args.capability:
        raise MasterError('Internal operations require a supervisor-issued one-use grant and inherited lock')
    grant_path = Path(args.grant).resolve()
    if not grant_path.is_relative_to(master.home / 'runs'):
        raise MasterError('Internal grant is outside this master program')
    grant = load_json(grant_path)
    parent = process_identity(os.getppid())
    if not parent or any(parent[k] != grant['parent'][k] for k in ['pid', 'start_ticks']):
        raise MasterError('Internal invocation is not a child of its recorded supervisor')
    if (grant.get('consumed') is not False or grant['phase'] != args.phase or grant['output'] != str(out)
            or grant['capability_sha256'] != hashlib.sha256(args.capability.encode()).hexdigest()):
        raise MasterError('Invalid, mismatched or already-consumed internal grant')
    if not out.is_relative_to(master.home / 'runs' / grant['run_id']):
        raise MasterError('Internal output is outside the active run')
    descriptor = os.fstat(args.lock_fd)
    expected = (master.home / 'runner.lock').stat()
    if (descriptor.st_dev, descriptor.st_ino) != (expected.st_dev, expected.st_ino):
        raise MasterError('Internal descriptor does not refer to the supervisor lock')
    try:
        fcntl.flock(args.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as error:
        raise MasterError('Internal descriptor does not share supervisor lock ownership') from error
    record = master.state['phases'][args.phase]
    if record['status'] not in {'running', 'repairing'}:
        raise MasterError('The registered phase is not being executed by the supervisor')
    targets = [out] if args.action == '_checks' else [out / name for name in master.phases[args.phase]['deliverables']]
    if any(p.exists() for p in targets):
        raise MasterError('Internal operation cannot overwrite an earlier result')
    grant.update(consumed=True, child_pid=os.getpid(), consumed_at=now())
    atomic_json(grant_path, grant)
    # Parent retains the writer lock. The validated child closes only its copy;
    # it must not strand that lock if the parent is killed before recovery.
    os.close(args.lock_fd)


def atomic_rule_publish(target, content):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.read_text() != content:
            raise MasterError('A different dedicated rule exists; preserve it for review')
        return
    descriptor, name = tempfile.mkstemp(prefix='.accdsl-rule-', dir=target.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, target)  # Atomic publication without overwriting another writer.
        except FileExistsError:
            if target.read_text() != content:
                raise MasterError('Conflicting policy appeared during publication; it was preserved')
        parent_fd = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
    finally:
        temporary.unlink(missing_ok=True)


def rule_text(root):
    """pattern is the runtime prefix; match/not_match are load-time rule tests.

    The dedicated rule permits entrypoint invocation. Internal operations still
    require their live one-use supervisor grant; a prefix match is not that grant.
    """
    command = ['python3', str(root / 'scripts/run_accounting_master.py')]
    return ('# AccDSL master only; existing global rules/settings are preserved.\n'
            '# Installed after explicit user approval of the reviewed program.\n'
            'prefix_rule(\n    pattern=' + repr(command) + ',\n    decision="allow",\n'
            '    match=[' + repr(command + ['run']) + ', ' + repr(command + ['status']) + '],\n'
            '    not_match=[["python3", "-c", "print(1)"], ["bash", "-lc", "echo unsafe"],\n'
            '               ["python3", "/tmp/unrelated.py"]],\n)\n')


def check_rule(rule, command):
    files = rule if isinstance(rule, list) else [rule]
    arguments = [item for file in files for item in ['--rules', str(file)]]
    result = subprocess.run(['codex', 'execpolicy', 'check', *arguments, '--', *command],
                            capture_output=True, text=True, timeout=30, check=False)
    if result.returncode:
        raise MasterError('Execpolicy verification failed: ' + result.stderr[-800:])
    return json.loads(result.stdout)


def install_rule(master):
    """Called under writer lock, after abandoned-worker recovery and reload."""
    candidate = master.home / 'accdsl-master.rules'
    receipt = master.home / 'installation.json'
    grant_path = master.home / 'authorization.json'
    target = Path.home() / '.codex/rules/accdsl-master.rules'
    installation = load_json(receipt) if receipt.exists() else None
    pending = installation is not None and installation.get('status') in {'prepared', 'published'}
    if pending:
        if (not candidate.is_file() or digest(candidate) != installation.get('candidate_sha256')
                or installation.get('target') != str(target)
                or installation.get('prepared_controller_hashes') != master.controls):
            raise ContinuationVeto('Prepared installation changed; preserve it for supervisor reconciliation')
        if installation.get('original_authorization_sha256') is not None:
            if not grant_path.exists() or digest(grant_path) != installation['original_authorization_sha256']:
                raise ContinuationVeto('Original standing authorization changed during installation')
        elif grant_path.exists() and stable_hash(load_json(grant_path)) != stable_hash(installation['prepared_authorization']):
            raise ContinuationVeto('Interrupted installation authorization does not match its prepared grant')
    else:
        atomic_bytes(candidate, rule_text(master.root).encode())
    prefix = ['python3', str(master.root / 'scripts/run_accounting_master.py')]
    positives = {name: check_rule(candidate, prefix + [name]) for name in PUBLIC_ACTIONS}
    negatives = [check_rule(candidate, command) for command in [['python3', '-c', 'print(1)'], ['bash', '-lc', 'echo unsafe'], ['python3', '/tmp/unrelated.py']]]
    if any(r.get('decision') != 'allow' for r in positives.values()) or any(r.get('decision') == 'allow' for r in negatives):
        raise MasterError('Exact allow-rule positive/negative checks failed')
    effective_files = [p for p in target.parent.glob('*.rules') if p != target] + [candidate]
    effective = {name: check_rule(effective_files, prefix + [name]) for name in PUBLIC_ACTIONS}
    if any(r.get('decision') != 'allow' for r in effective.values()):
        raise MasterError('Existing policy overrides the proposed allow rule; inspect effective-policy checks before proceeding')
    if not pending:
        prepared_grant = load_json(grant_path) if grant_path.exists() else {
            'created_at': now(), 'scope': str(master.root),
            'basis': 'Explicit upfront approval of install-and-run and the reviewed plan',
            'sequential_workers': True, 'parallel_or_recursive_workers': False,
            'implementer_sandbox': 'workspace-write', 'reviewer_sandbox': 'read-only',
            'nested_approval_policy': 'never', 'public_source_research': True,
            'project_local_dependencies_only': True, 'paid_services_or_professional_review': False,
            'rule': str(target), 'controller_hashes_at_grant': master.controls}
        installation = {'status': 'prepared', 'candidate_sha256': digest(candidate), 'target': str(target),
            'prepared_at': now(), 'prepared_controller_hashes': master.controls,
            'prepared_authorization': prepared_grant,
            'original_authorization_sha256': digest(grant_path) if grant_path.exists() else None,
            'review_required_before_execution': True}
        atomic_json(receipt, installation)
    atomic_rule_publish(target, candidate.read_text())
    installation.update(status='published', published_at=now())
    atomic_json(receipt, installation)
    checks = {'rule': str(target), 'sha256': digest(target), 'positive_checks': positives, 'negative_checks': negatives, 'effective_policy_checks': effective}
    atomic_json(master.home / 'approval-checks.json', checks)
    if not grant_path.exists():
        atomic_json(grant_path, installation['prepared_authorization'])
    installation.update(status='complete', completed_at=now())
    atomic_json(receipt, installation)
    master.event('approval_rule_installed', rule=str(target), verified_commands=list(positives))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=PUBLIC_ACTIONS + ['_checks', '_builtin'])
    parser.add_argument('--max-phases', type=int, default=15)
    parser.add_argument('--max-seconds', type=int, default=7200)
    parser.add_argument('--phase')
    parser.add_argument('--out')
    parser.add_argument('--retry-blocked', action='store_true', help='Explicitly retry unchanged external blocks after repairing access/environment')
    parser.add_argument('--lock-fd', type=int, help=argparse.SUPPRESS)
    parser.add_argument('--grant', help=argparse.SUPPRESS)
    parser.add_argument('--capability', help=argparse.SUPPRESS)
    args = parser.parse_args()
    max_seconds = 172800 if args.action == 'campaign' else MAX_RUN_SECONDS
    if not 1 <= args.max_phases <= 15 or not 1 <= args.max_seconds <= max_seconds:
        parser.error(f'Use 1..15 phases and 1..{max_seconds} seconds')
    master = Master()
    if args.action not in {'_checks', '_builtin'} and (args.phase or args.out or args.lock_fd is not None or args.grant or args.capability):
        parser.error('Internal operation arguments are reserved for supervisor children')
    if args.action in {'_checks', '_builtin'}:
        if args.phase not in master.phases or not args.out:
            parser.error('Internal operation requires an exact registered phase and output path')
        out = Path(args.out).resolve()
        if not out.is_relative_to(master.home / 'runs'):
            parser.error('Internal output must be within master run records')
        validate_internal(master, args, out)
        if args.action == '_checks':
            return 0 if run_phase_tests(ROOT, master.phases[args.phase], out) else 1
        if args.phase == 'P00':
            baseline(ROOT, out)
        elif args.phase == 'P01':
            source_register(ROOT, out)
        else:
            parser.error('No builtin for this phase')
        return 0
    if args.action == 'status':
        plan_file = master.home / 'next-plan.json'
        plan_current = (master.state_path.exists() and plan_file.exists()
                        and load_json(plan_file).get('state_sha256') == digest(master.state_path))
        print(json.dumps({'mission_complete': False, 'workflow_mode': master.catalog['workflow']['mode'],
                          'product_implementation_enabled': False,
                          'blocked_phases': {p: master.phase_block(p) for p in master.phases if master.phase_block(p)},
                          'phase_states': {k: v['status'] for k, v in master.state['phases'].items()},
                          'campaign': load_json(master.home / 'campaign.json') if (master.home / 'campaign.json').exists() else None,
                          'last_outcome': master.state['last_outcome'], 'state': str(master.state_path), 'plan_matches_saved_state': plan_current}, indent=2))
        return 0
    if args.action == 'stop':
        atomic_json(master.home / 'stop-request.json', {'requested_at': now()})
        print('Stop requested; the active child process will be terminated and partial work retained.')
        return 0
    if args.action == 'refresh':
        with exclusive_lock(master.home / 'runner.lock'):
            master.recover_process()
            master.reload_state()
            master.protected = protected_hashes(ROOT)
            print(json.dumps(master.refresh(), indent=2))
        return 0
    if args.action == 'install-and-run':
        with exclusive_lock(master.home / 'runner.lock') as lock_fd:
            master.lock_fd = lock_fd
            master.recover_process()
            master.reload_state()
            install_rule(master)
        master.lock_fd = None
    elif args.action == 'run' and (master.home / 'installation.json').exists():
        # An interrupted explicit installation can be completed idempotently.
        installation = load_json(master.home / 'installation.json')
        if installation.get('status') in {'prepared', 'published'}:
            with exclusive_lock(master.home / 'runner.lock') as lock_fd:
                master.lock_fd = lock_fd
                master.recover_process()
                master.reload_state()
                install_rule(master)
            master.lock_fd = None
    if args.action == 'review':
        with exclusive_lock(master.home / 'runner.lock') as lock_fd:
            master.lock_fd = lock_fd
            master.recover_process()
            folder = master.home / 'runs' / ('review-' + uuid.uuid4().hex[:8])
            folder.mkdir(parents=True)
            master.protected = protected_hashes(ROOT)
            master.controller_review(folder)
        return 0
    if args.action == 'campaign':
        if args.retry_blocked:
            parser.error('Campaign cannot bypass blocked/no-progress deferrals; inspect and repair them explicitly')
        outcome = master.campaign(args.max_seconds, args.max_phases)
        return 0 if outcome == 'proposal_ready' else 2
    outcome = master.run(args.max_phases, args.max_seconds, retry_blocked=args.retry_blocked)
    return 0 if outcome in {'catalog_slices_accepted_mission_open', 'phase_limit', 'proposal_reviewed_implementation_held'} else 2


if __name__ == '__main__':
    try:
        with catch_termination():
            raise SystemExit(main())
    except KeyboardInterrupt:
        print('Interrupted; partial state retained. Resume verifies prior worker cleanup.', file=sys.stderr)
        raise SystemExit(130)
    except (MasterError, ValueError, OSError) as error:
        print(f'{type(error).__name__}: {error}', file=sys.stderr)
        raise SystemExit(2)
