"""One bounded P19 reviewer invocation; no tools, hooks, state edits or campaign reset."""
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
stage = sys.argv[1]
if stage not in {'health', 'read', 'assessment', 'repair'}:
    raise SystemExit('Only fixed P19 read-only stages are allowed')
settings = ROOT / 'data/accounting-master/direct-p16-20261006/review-settings.json'
configured = json.loads(Path('/home/chakwong/.claude/settings.json').read_text())
env = os.environ.copy()
env.update(configured.get('env', {}))
if env.get('ANTHROPIC_AUTH_TOKEN'):
    env.pop('ANTHROPIC_API_KEY', None)
elif not env.get('ANTHROPIC_API_KEY'):
    raise SystemExit('Configured reviewer authentication unavailable')
env['CLAUDE_CODE_SIMPLE'] = '1'
env['CLAUDE_CODE_MAX_OUTPUT_TOKENS'] = '7000' if stage in {'assessment','repair'} else '1024'
env['MAX_THINKING_TOKENS'] = '1500' if stage in {'assessment','repair'} else '256'
packet = OUT / ('repair-packet-v1.md' if stage == 'repair' else 'review-packet-v1.md')
if stage == 'health':
    prompt = 'Return exactly CLAUDE_PROBE_OK.'
elif stage == 'read':
    prompt = ('Check whether this packet is legible and self-contained for its stated bounded review. '
              'Return exactly CLAUDE_PACKET_READ_OK or BLOCK_PACKET followed by one reason. '
              'Do not perform the review.\n\n' + packet.read_text())
else:
    prompt = packet.read_text()
command = ['claude', '--print', '--no-session-persistence', '--output-format', 'stream-json',
           '--verbose', '--permission-mode', 'plan', '--setting-sources', '',
           '--settings', str(settings), '--tools', '', '--strict-mcp-config',
           '--mcp-config', '{"mcpServers":{}}', '--effort', 'medium', '--max-turns', '1']
if configured.get('model'):
    command += ['--model', configured['model']]
prefix = OUT / (stage + '-review-v1')
start = time.monotonic()
limit = 180 if stage in {'assessment','repair'} else 90
with prefix.with_suffix('.stdout.jsonl').open('x') as stdout, prefix.with_suffix('.stderr.txt').open('x') as stderr:
    process = subprocess.Popen(command, stdin=subprocess.PIPE, text=True, cwd=ROOT,
                               env=env, stdout=stdout, stderr=stderr, start_new_session=True)
    try:
        process.communicate(prompt, timeout=limit)
        code = process.returncode
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        code = 124
texts = []
for line in prefix.with_suffix('.stdout.jsonl').read_text().splitlines():
    try:
        row = json.loads(line)
    except json.JSONDecodeError:
        continue
    if row.get('type') == 'assistant':
        texts += [x['text'] for x in row.get('message', {}).get('content', []) if x.get('type') == 'text']
prefix.with_suffix('.text.md').write_text('\n\n'.join(texts) + '\n')
receipt = {'stage': stage, 'exit_code': code, 'wall_seconds': time.monotonic()-start,
           'timeout_seconds': limit, 'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
           'wrapper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'read_only': True, 'tools': [], 'model_route': 'existing user configuration',
           'authorization': 'Direct user continuation on 7 October; original stopped campaign unchanged',
           'stdout': str(prefix.with_suffix('.stdout.jsonl').relative_to(ROOT)),
           'stderr': str(prefix.with_suffix('.stderr.txt').relative_to(ROOT)),
           'text': str(prefix.with_suffix('.text.md').relative_to(ROOT))}
prefix.with_suffix('.receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt))
print('\n\n'.join(texts)[:15000])
raise SystemExit(code)
