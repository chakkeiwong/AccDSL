#!/usr/bin/env python3
"""Resumable, reviewed accounting work with bounded repair and one stable command."""
from __future__ import annotations

import argparse
import ast
import ctypes
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
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
                                      editable_files, worker_inventory, validate_artifact_contract, verification_input_errors)

ROOT = Path(__file__).resolve().parents[1]
CATALOG = 'scripts/accounting_master_catalog.json'
SCHEMA = 'scripts/accounting_master_response.schema.json'
CONTROLS = [
    'scripts/run_accounting_master.py', 'scripts/accounting_master_support.py',
    CATALOG, SCHEMA, 'tests/test_accounting_master.py',
    'docs/plans/accounting-master-program.md',
    'scripts/check_accounting_proposal.py', 'tests/test_accounting_proposal.py',
]
ACCEPTED = 'accepted_internal'
PUBLIC_ACTIONS = ['install-and-run', 'run', 'status', 'refresh', 'stop', 'review']
RESPONSE_KEYS = {'verdict', 'summary', 'steps', 'assumptions', 'checks',
                 'evidence', 'issues', 'residuals', 'next_actions'}


class MasterError(RuntimeError):
    pass


class ContinuationVeto(MasterError):
    pass


class ProcessTimeout(MasterError):
    pass


class ReviewPending(MasterError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def stable_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':'), allow_nan=False).encode()).hexdigest()


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
                'blocked_external', 'needs_plan_repair', 'needs_repair', 'needs_review', ACCEPTED}
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
    current = process_identity(proc.pid)
    if original is None:
        if proc.returncode is not None:
            return  # Already reaped by the caller: do not signal a reusable PID.
        original = current
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


def bounded_process(argv, cwd, log, seconds, *, prompt=None, heartbeat=None, stopped=None, on_spawn=None, pass_fds=()):
    """Bound the initial process group. Workers are trusted not to detach jobs."""
    log.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    prompt_file = log.with_suffix('.stdin.txt')
    if prompt is not None:
        prompt_file.write_text(prompt)
    if threading.active_count() != 1:
        raise ContinuationVeto('The reviewed process launcher requires a single-threaded supervisor')
    with log.open('wb') as stream, (prompt_file.open('rb') if prompt is not None else open(os.devnull, 'rb')) as input_stream:
        proc = None
        old_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGTERM, signal.SIGINT})
        try:
            # Defer handled interruption until ownership is durably registered.
            # Restore the child's inherited mask before exec. This preexec path
            # is restricted above to a dedicated single-threaded supervisor.
            proc = subprocess.Popen(argv, cwd=cwd, stdin=input_stream,
                                    stdout=stream, stderr=subprocess.STDOUT, start_new_session=True,
                                    env={**os.environ, 'PYTHONUNBUFFERED': '1', 'CUDA_VISIBLE_DEVICES': '-1'}, pass_fds=pass_fds,
                                    preexec_fn=lambda: signal.pthread_sigmask(signal.SIG_SETMASK, old_mask))
            proc._master_identity = process_identity(proc.pid)
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
                if elapsed >= seconds:
                    reason = 'timeout'
                elif log.stat().st_size > 16 * 1024 * 1024:
                    reason = 'output_limit'
                elif stopped and stopped():
                    reason = 'stop_requested'
                if reason or exited is not None:
                    break
                if heartbeat and time.monotonic() - last_beat >= 20:
                    heartbeat(round(elapsed, 1))
                    last_beat = time.monotonic()
                time.sleep(0.1)
            terminate_group(proc)
            if log.stat().st_size > 16 * 1024 * 1024:
                reason = 'output_limit'
            return {'argv': argv, 'exit_code': proc.returncode, 'reason': reason,
                    'wall_seconds': round(time.monotonic() - started, 3), 'log': str(log)}
        finally:
            try:
                if proc is not None:
                    terminate_group(proc)
            finally:
                signal.pthread_sigmask(signal.SIG_SETMASK, old_mask)


class Master:
    def __init__(self, root=ROOT, worker=None, check=None, builtin=None):
        self.root = root.resolve()
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
        record = {'time': now(), 'run': self.run_id, 'event': kind, **fields}
        with (self.home / 'events.jsonl').open('a') as stream:
            stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        print(json.dumps(record, ensure_ascii=False), flush=True)

    def remaining(self, requested):
        value = min(requested, self.deadline - time.monotonic())
        if value <= 0:
            raise MasterError('Run wall-time limit reached; preserve partial work and resume')
        return value

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

    def process(self, argv, log, seconds, prompt=None, internal_phase=None):
        active_path = self.home / 'active-process.json'
        active = {}
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
            active.update({'status': 'running', 'run_id': self.run_id, 'started_at': now(),
                           'identity': process_identity(proc.pid), 'argv': argv, 'log': str(log.relative_to(self.root))})
            atomic_json(active_path, active)
        try:
            result = bounded_process(argv, self.root, log, self.remaining(seconds), prompt=prompt,
                                     heartbeat=lambda elapsed: self.event('heartbeat', stage=log.stem, seconds=elapsed),
                                     stopped=lambda: (self.home / 'stop-request.json').exists(), on_spawn=spawned,
                                     pass_fds=(self.lock_fd,) if internal_phase and self.lock_fd is not None else ())
        finally:
            with defer_shutdown():
                errors, remaining, changed = [], [], []
                original_error = str(sys.exception())
                try:
                    if active.get('identity'):
                        remaining = live_group_members(active['identity']['pgid'])
                        active.update(status='cleanup_required' if remaining else 'finished', finished_at=now(), survivors=remaining)
                        atomic_json(active_path, active)
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
        if result['exit_code'] != 0 or result['reason']:
            error_type = ProcessTimeout if result['reason'] == 'timeout' else MasterError
            raise error_type(f'Command failed ({result["reason"] or result["exit_code"]}); inspect {log.relative_to(self.root)}')
        return result

    def recover_process(self):
        path = self.home / 'active-process.json'
        if not path.exists():
            return
        saved = load_json(path)
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

    def worker(self, role, phase, packet, folder, attempt=0):
        role_verdicts(role)
        if phase['id'] in self.phases and self.phase_block(phase['id']):
            raise ContinuationVeto(self.phase_block(phase['id']))
        if (folder / f'{role}-{attempt}.response.json').exists():
            raise MasterError('Worker response destination is not fresh')
        guarded, absent = control_snapshot(self.root, [self.state_path, self.home / 'authorization.json', self.home / 'next-plan.json', self.home / 'proposal-ready.json'])
        generated = [str((folder / f'{role}-{attempt}{suffix}').relative_to(self.root)) for suffix in
                     ('.response.json', '.schema.json', '.recovery.json', '.prompt.txt', '.log',
                      '.stdin.txt', '.process.json', '.raw-negative-response.json', '.integrity-failure.json')]
        generated += ['data/accounting-master/events.jsonl', 'data/accounting-master/active-process.json',
                      'data/accounting-master/stop-request.json']
        try:
            before = worker_inventory(self.root, generated)
        except (ValueError, OSError) as error:
            raise ContinuationVeto('Cannot establish worker write inventory: ' + str(error)) from error
        try:
            return self._worker_result(role, phase, packet, folder, attempt)
        finally:
            original_error = str(sys.exception())
            try:
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
            except (ValueError, OSError) as error:
                try:
                    atomic_json(folder / f'{role}-{attempt}.integrity-failure.json',
                                {'verification_error': str(error), 'original_error': original_error})
                except OSError:
                    pass
                raise ContinuationVeto('Worker integrity failure (read-only or declared write scope): ' + str(error)) from error

    def _worker_result(self, role, phase, packet, folder, attempt=0):
        runtime_guard = {str(p.relative_to(self.root)): digest(p) for p in [self.state_path, self.home / 'authorization.json'] if p.exists()}
        seconds = worker_seconds(role, self.catalog['limits'])
        reserve = self.catalog['limits'].get('verification_reserve_seconds', 0) if role in {'implement', 'repair'} else 0
        cutoff = min(time.monotonic() + seconds, self.deadline - reserve)
        def remaining_work():
            available = cutoff - time.monotonic()
            if available <= 0:
                raise MasterError('Insufficient run budget for editable work plus supervisor verification reserve')
            return available
        available = remaining_work()
        budget = {'worker_limit_seconds': seconds, 'available_attempt_seconds': round(available, 1),
                  'run_remaining_seconds': round(self.deadline - time.monotonic(), 1) if self.deadline != float('inf') else None,
                  'reserve_for_checks_and_response_seconds': min(120, round(available / 5, 1)),
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
        if self.worker_override:
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
            def config_query(command):
                try:
                    return subprocess.run(command, capture_output=True, text=True,
                                          timeout=min(30, remaining_work()), check=True)
                except (subprocess.SubprocessError, OSError) as error:
                    raise MasterError('Bounded worker configuration failed: ' + str(error)) from error
            listed = config_query([executable, '-C', str(self.root), 'mcp', 'list', '--json'])
            servers = json.loads(listed.stdout)
            names = [entry['name'] for entry in servers]
            overrides = worker_overrides(mode, {'mcp_servers': dict.fromkeys(names)}, role)
            checked = config_query([executable, '-C', str(self.root), *overrides, 'mcp', 'list', '--json'])
            if any(entry.get('enabled', True) for entry in json.loads(checked.stdout)):
                raise MasterError('Worker integration isolation was not effective')
            argv[-1:-1] = overrides
            budget.update(available_attempt_seconds=round(remaining_work(), 1), measured_at=now())
            prompt = self.prompt(role, phase, packet)
            (folder / f'{role}-{attempt}.prompt.txt').write_text(prompt)
            self.process(argv, folder / f'{role}-{attempt}.log', remaining_work(), prompt)
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
            'The artifact format is documented in docs/plans/accounting-proposal-artifact-format.md. '
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
            'The packet budget is in seconds and is enforced by the supervisor. Start checks and write required deliverables before the reserved final interval. Return the required structured response before the attempt expires. If incomplete, identify exact remaining work honestly; a timeout or partial implementation cannot pass acceptance.',
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
            'When repair_workflow is supplied, select only the first unresolved bounded task using current checks and retained evidence. State its stop condition, required outputs and next task explicitly. Do not combine unresolved authority research with complete lifecycle implementation in one attempt. After partial work or timeout, narrow the remaining scope using the supervisor continuation/check record; do not repeat the unchanged broad plan.',
            'For review_plan, actively check wrong baselines, proxy promotion, missing stops, unfair comparisons, hidden assumptions, stale context, environment mismatch and whether proposed artifacts answer the question. AGREE requires no unresolved material objection.',
            'For implement/repair, execute the reviewed task and write its actual deliverables. For proposal phases, repair the specification itself and use the registered checker; do not edit controller-owned checker/tests. For an explicitly scoped probe, use meaningful tests of the named design question.',
            'Never redirect a checker onto an existing result file. Use a fresh task-local filename, validate nonempty JSON before citing it, and preserve previous evidence. Read-only reviewers may use disposable /tmp output only; never redirect into the project or rebuild project files.',
            'For implement/repair, maintain a concise progress.md in the declared output_dir after the first inspection and meaningful edits. Record checked findings, changed files, exact next checks and unfinished deliverables within 600 words. This checkpoint is partial progress, never a substitute for the required result or acceptance.',
            'For proposal writing, save each completed substantive section or group of assessments to the actual deliverable before inspecting the next group. Do not defer all substantive writing until the end. Use the supplied measured_at and attempt budget to stop new research before the checks/response reserve; save current progress and return PARTIAL with the exact next task when time is short.',
            'For review_result, inspect actual code, tests, source evidence and deterministic check reports. A returned success or many tests alone is insufficient. Return REVISE with actionable repairs if acceptance criteria fail.',
            'An AGREE response must have issues=[]; put nonblocking limitations in residuals. An empty implementation or a plan-only deliverable must not pass an implementation phase.',
            'For review_controller, audit orchestration, recovery, permissions, repair, plan refresh, child-process limits and honest completion against the plan and tests. Do not change files.',
            'Every evidence entry must be an existing repository-relative FILE path, never prose, a directory or an invented artifact. Include concrete unresolved work in residuals and justified next tasks in next_actions.',
            'Return only the response schema. Verdict: PLAN for plan; AGREE/REVISE for review; IMPLEMENTED for completed phase work; PARTIAL for a completed bounded task with explicit next_actions; BLOCKED only for a real dependency preventing the stated slice. A partial-task review may AGREE on that task only when review_scope says bounded_partial_work; it does not accept the phase.',
            format_instruction,
            json.dumps({'phase': phase, 'packet': packet}, ensure_ascii=False, indent=2),
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
            'worker-boundary': ['worker_overrides', 'worker_seconds', 'role_verdicts', 'validate_response', 'control_snapshot', 'created_controls', 'Master.process', 'Master.worker', 'Master._worker_result', 'Master.phase_review'],
            'state-refresh': ['validate_catalog', 'validate_state', 'Master.__init__', 'Master.verify_workflow', 'Master.phase_block', 'Master.reload_state', 'Master.save', 'Master.event', 'Master.check_protection', 'Master.refresh', 'Master.input_fingerprint', 'Master.review_dependencies'],
            'scheduler': ['Master.run', 'Master.remaining', 'boot_identity', 'Master.recover_process', 'Master.phase_block', 'Master.proposal_gate', 'Master.review_dependencies'],
            'phase-plan-repair': ['validate_response', 'acceptance_ready', 'Master.refresh_worker_plan', 'Master.approve_phase_plan', 'Master.save_continuation', 'Master.execute_phase', 'Master.check_phase', 'Master.load_pending_review', 'Master.save_pending_review', 'Master.phase_review', 'Master.evidence_hashes', 'Master.worker'],
            'evidence': ['Master.check_protection', 'Master.evidence_hashes', 'Master.ensure_controller_tests', 'Master.capture_phase_changes', 'Master.proposal_gate', 'Master.review_dependencies'],
        }
        tests_source = (self.root / 'tests/test_accounting_master.py').read_text()
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
                      'constants': {'ACCEPTED': ACCEPTED, 'PUBLIC_ACTIONS': PUBLIC_ACTIONS, 'CONTROLS': CONTROLS, 'ROOT': str(self.root)},
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
                          'per_phase_plan': 'execute_phase obtains a fresh plan and separate review_plan verdict, stores its hash and checks it before and after implementation. Builtins P00/P01 use a stored fresh instance of an already reviewed fixed-operation contract plus verified input hashes; they invent no scientific method.',
                          'resume_semantics': 'run is the explicit operator resume action. There is no self-restarting daemon. It archives a prior stop only on that new invocation; a stop during execution prevents further work.',
                          'external_blocks': 'Unobservable external changes are deliberately not polled. A known access change is retried by the explicit --retry-blocked option, using the same approved entrypoint. Changed declared dependencies also invalidate a block signature.',
                      },
                      'verification': load_json(self.home / 'controller-tests.json') if (self.home / 'controller-tests.json').exists() else {'status': 'missing'},
                      'test_names': test_names, 'controller_hashes': self.controls,
                      'reviewed_evidence_contract_and_permission_scope': plan_contract}
            if name in {'evidence', 'phase-plan-repair', 'scheduler', 'worker-boundary'}:
                packet['support_code'] = (self.root / 'scripts/accounting_master_support.py').read_text()
            if name == 'evidence':
                packet['proposal_checker'] = (self.root / 'scripts/check_accounting_proposal.py').read_text()
                packet['proposal_tests'] = (self.root / 'tests/test_accounting_proposal.py').read_text()
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
            test_command = ('import unittest; '
                            'suite = unittest.TestSuite(unittest.TestLoader().discover("tests", pattern=p) '
                            'for p in ("test_accounting_master.py", "test_accounting_proposal.py")); '
                            'result = unittest.TextTestRunner(verbosity=2).run(suite); '
                            'raise SystemExit(0 if result.wasSuccessful() else 1)')
            self.process([sys.executable, '-c', test_command], log, 180)
        except ContinuationVeto:
            raise
        except MasterError as error:
            failed = str(error)
        text = log.read_text() if log.exists() else ''
        count = re.search(r'Ran (\d+) tests? in', text)
        skipped = re.search(r'OK \(skipped=(\d+)\)', text)
        tests = int(count[1]) if count else 0
        passed = failed is None and tests > 0 and (not skipped or int(skipped[1]) < tests)
        result = {'passed': passed, 'tests': tests, 'error': failed, 'sha256': expected,
                  'log': str(log.relative_to(self.root)), 'checked_at': now()}
        atomic_json(report, result)
        atomic_json(folder / 'controller-tests.json', result)
        self.event('controller_tests_finished', passed=passed, tests=tests)
        if not passed:
            raise ContinuationVeto('Current controller tests failed; model review and phase execution are blocked')

    def check_phase(self, phase, folder):
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

    def save_pending_review(self, phase, record, packet, stage):
        if verification_input_errors(self.root, packet['checks']):
            raise MasterError('Checked inputs changed; rerun verification before review')
        names = set(record['contributed_files']) | set(packet['work']['evidence']) | {phase['test_file']}
        names.update(packet['checks'].get('input_hashes', {}))
        names.update(str(Path(phase['output_dir']) / n) for n in phase['deliverables'])
        names.update([packet['check_path'], packet['approved_plan_path'], packet['work_path']])
        checkpoint = {'phase_hash': stable_hash(phase), 'dependencies': self.review_dependencies(phase),
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
            if (saved['phase_hash'] != stable_hash(phase)
                    or saved['dependencies'] != self.review_dependencies(phase)
                    or not saved['evidence_hashes'] or verify_hashes(self.root, saved['evidence_hashes'])
                    or not acceptance_ready(phase, checked)
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

    def execute_phase(self, phase, folder):
        identifier = phase['id']
        if self.phase_block(identifier):
            raise ContinuationVeto(self.phase_block(identifier))
        folder.mkdir(parents=True, exist_ok=True)
        record = self.state['phases'][identifier]
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
            self.check_protection()
            evidence = [str(p.relative_to(self.root)) for p in folder.rglob('*') if p.is_file()]
            record.update(status=ACCEPTED, residuals=result.get('residuals', []), issues=[],
                          evidence_hashes=self.evidence_hashes(evidence), accepted_at=now(),
                          accepted_phase_hash=stable_hash(phase), accepted_dependencies=self.review_dependencies(phase))
            return
        packet = {'next_plan': self.refresh_worker_plan(), 'phase_output_dir': phase['output_dir'],
                  'prior_attempts': record['attempts'][:-1], 'prior_issues': record.get('issues', []),
                  'original_criteria': phase['criteria'], 'repair_workflow': phase.get('repair_workflow', [])}
        resumed = self.load_pending_review(phase, record)
        approved = resumed['approved'] if resumed else None
        if resumed:
            atomic_json(folder / 'approved-plan.json', approved)
            self.event('checked_work_resumed', phase=identifier, prior_check=resumed['check_path'])
        if not resumed:
            if phase.get('checker'):
                preflight = folder / 'preflight'
                preflight.mkdir()
                before_preflight = preserve_editable(self.root, self.home / 'prior-bytes')
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
            entry = preserve_editable(self.root, self.home / 'prior-bytes')
            entry_path = folder / 'phase-entry-inventory.json'
            atomic_json(entry_path, entry)
            record['entry_inventory_path'] = str(entry_path.relative_to(self.root))
            self.save()
        packet['phase_entry_inventory'] = record['entry_inventory_path']
        for attempt in range(self.catalog['limits']['max_repairs'] + 1):
            if (self.home / 'stop-request.json').exists():
                record.update(status='interrupted', issues=['Stop requested; preserved work needs verification on resume.'])
                return
            # Internal helpers verify this persisted execution state. A partial
            # continuation temporarily changes it during replanning.
            record['status'] = 'repairing' if attempt else 'running'
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
                before = preserve_editable(self.root, self.home / 'prior-bytes')
                atomic_json(stage / 'pre-edit-files.json', before)
                work_error = None
                work = None
                try:
                    if reuse_work:
                        work = resumed['work']
                        work_path = stage / 'resumed-work.response.json'
                        atomic_json(work_path, work)
                    else:
                        work = self.worker(role, phase, packet, stage, attempt)
                        work_path = stage / f'{role}-{attempt}.response.json'
                except ContinuationVeto:
                    raise
                except (MasterError, ValueError, OSError) as error:
                    work_error = f'{type(error).__name__}: {error}'
                finally:
                    changes, cumulative = self.capture_phase_changes(record, stage, before, entry)
                if stable_hash(load_json(folder / 'approved-plan.json')['plan']) != approved['plan_hash']:
                    raise ContinuationVeto('Implementation changed its approved plan')
                if record['outstanding_deletions']:
                    raise MasterError('Restore prohibited phase deletions before acceptance: ' + ', '.join(record['outstanding_deletions']))
                try:
                    checked = self.check_phase(phase, stage)
                finally:
                    changes, cumulative = self.capture_phase_changes(record, stage, before, entry)
                if record['outstanding_deletions']:
                    raise MasterError('Verification deleted preserved project files: ' + ', '.join(record['outstanding_deletions']))
                if (work_error or work['verdict'] in {'PARTIAL', 'BLOCKED'}
                        or (phase.get('checker') and checked.get('passed') is True and not acceptance_ready(phase, checked))):
                    reason = work_error or work['summary']
                    actions = (work['next_actions'] if work else []) or ['Plan one smaller remaining task from the current checks and preserved changes.']
                    continuation = self.save_continuation(phase, record, stage, checked, reason, actions)
                    if work and work['verdict'] == 'BLOCKED':
                        record.update(status='blocked_external', issues=work['issues'], residuals=work['residuals'], next_actions=work['next_actions'])
                        return
                    partial_review = None
                    if work and checked.get('passed') is True and checked.get('tests', 0) > 0:
                        try:
                            partial_review, _ = self.phase_review('review_result', phase,
                                {**packet, 'work': work, 'checks': checked, 'review_scope': 'bounded_partial_work',
                                 'continuation': continuation, 'actual_changes': changes}, stage, attempt)
                        except ReviewPending:
                            pass  # Keep a checked continuation; no phase acceptance or invented verdict.
                        if verify_hashes(self.root, continuation['evidence_hashes']):
                            raise ContinuationVeto('Checked partial work changed during read-only review')
                        if partial_review and partial_review['verdict'] == 'BLOCKED':
                            record.update(status='blocked_external', issues=partial_review['issues'],
                                          residuals=partial_review['residuals'], next_actions=partial_review['next_actions'])
                            return
                    progress = any(changes.values())
                    record['no_progress_count'] = 0 if progress else record.get('no_progress_count', 0) + 1
                    issues = [reason]
                    packet['repair_findings'] = {'continuation': continuation, 'partial_review': partial_review,
                                                'required_action': 'Fresh reviewed plan for one smaller unresolved task.'}
                    record.update(status='needs_repair', issues=issues)
                    self.save()
                    self.event('partial_work_checked', phase=identifier, attempt=attempt, passed=checked.get('passed'), progress=progress)
                    if not progress:
                        record['status'] = 'needs_plan_repair'
                        if record['no_progress_count'] >= 2:
                            record['deferred_signature'] = self.input_fingerprint(identifier)
                            record['issues'].append('Repeated unchanged partial failure deferred until relevant inputs change or explicit --retry-blocked.')
                        return
                    if attempt == self.catalog['limits']['max_repairs']:
                        return
                    packet['next_plan'] = self.refresh_worker_plan()
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
                    record.update(status=ACCEPTED, issues=[], accepted_at=now(),
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
            except ContinuationVeto:
                raise
            except (MasterError, ValueError, OSError) as error:
                issues = [str(error)]
                packet['repair_findings'] = {'execution_error': str(error)}
            record.update(status='repairing', issues=issues)
            self.save()
            self.event('verification_requires_repair', phase=identifier, attempt=attempt, issues=issues)
            if attempt < self.catalog['limits']['max_repairs']:
                packet['next_plan'] = self.refresh_worker_plan()
                approved = self.approve_phase_plan(phase, record, packet, folder / f'replan-{attempt + 1}')
                if approved is None:
                    return
                atomic_json(folder / 'approved-plan.json', approved)
                packet['approved'] = approved
        record.update(status='needs_repair', issues=issues,
                      residuals=record.get('residuals', []) + ['Repair allowance exhausted for this invocation; retain partial work and refresh the next slice.'])
        if record.get('outstanding_deletions'):
            raise ContinuationVeto('Phase left prohibited deletions unresolved; preserve the entry inventory and repair before continuing')

    def run(self, max_phases=15, seconds=7200, require_review=True, retry_blocked=False):
        with exclusive_lock(self.home / 'runner.lock') as lock_fd:
            self.lock_fd = lock_fd
            self.recover_process()
            self.reload_state()
            self.run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8]
            folder = self.home / 'runs' / self.run_id
            folder.mkdir(parents=True)
            self.deadline = time.monotonic() + seconds
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
            if stop.exists():
                stop.rename(folder / 'prior-stop-request.json')
            manifest = {'run_id': self.run_id, 'started_at': now(), 'command': sys.argv,
                        'python': sys.executable, 'python_version': sys.version, 'controller_hashes': self.controls,
                        'catalog_sha256': digest(self.root / CATALOG), **git_provenance(self.root),
                        'device': 'CPU; CUDA_VISIBLE_DEVICES=-1 in child commands',
                        'seeds': 'N/A for controller; scientific phases must declare their own',
                        'max_phases': max_phases, 'wall_limit_seconds': seconds,
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
                if require_review:
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
                                                  'issues': record.get('issues', []), 'residuals': record.get('residuals', [])}
                    self.event('phase_finished', phase=identifier, status=record['status'])
                    refreshed = self.refresh()
                    self.event('next_plan_refreshed', previous_phase=identifier, next_phase=refreshed['next_phase'])
                if stop.exists():
                    outcome = 'stop_requested'
                elif time.monotonic() >= self.deadline:
                    outcome = 'wall_limit'
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
    if not 1 <= args.max_phases <= 15 or not 1 <= args.max_seconds <= 86400:
        parser.error('Use 1..15 phases and 1..86400 seconds')
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
