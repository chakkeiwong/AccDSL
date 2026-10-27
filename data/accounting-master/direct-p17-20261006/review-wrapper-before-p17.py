"""Fixed P16 read-only review calls with preserved input/output and no tools."""
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path('/home/chakwong/python/AccDSL')
OUT = ROOT / 'data/accounting-master/direct-p16-20261006'
stage = sys.argv[1]
prompts = {
    'health': 'Return exactly CLAUDE_PROBE_OK.',
    'read': 'Read the attached review packet. Reply exactly CLAUDE_PACKET_READ_OK if it is legible. Do not review yet.\n',
    'packet': 'Read the attached review packet and judge only whether it contains enough information for the requested review. Return PASS_PACKET_SELF_CONTAINED or BLOCK_PACKET_SELF_CONTAINED followed by at most three short reasons. Do not perform the full review yet.\n',
    'platform': '',
    'domain': '',
    'repair': '',
}
if stage not in prompts:
    raise SystemExit('Only the fixed health/read/packet/platform/domain stages are allowed')
prompt = prompts[stage]
if stage != 'health':
    kind = 'domain' if stage == 'domain' else 'platform'
    packet_name = 'repair-review-packet-v1.md' if stage == 'repair' else kind+'-review-packet-v4.md'
    prompt += (OUT / packet_name).read_text()
    if stage == 'packet':
        prompt += '\nFor this probe, perform ONLY the packet-sufficiency assessment, not the substantive review. Return the requested PASS/BLOCK token and at most three short reasons.\n'
env = os.environ.copy()
# Retain the user's currently configured route/model, which may differ from
# stale exported shell values. The configured route uses token authentication;
# --bare's API-key-only path is inappropriate for it. Never print credentials.
configured = json.loads(pathlib.Path('/home/chakwong/.claude/settings.json').read_text())
env.update(configured.get('env', {}))
if env.get('ANTHROPIC_AUTH_TOKEN'):
    env.pop('ANTHROPIC_API_KEY', None)
elif not env.get('ANTHROPIC_API_KEY'):
    raise SystemExit('No configured Claude authentication')
env['CLAUDE_CODE_SIMPLE'] = '1'
env['CLAUDE_CODE_MAX_OUTPUT_TOKENS'] = '24000' if stage in ['platform','domain','repair'] else '4096'
env['MAX_THINKING_TOKENS'] = '8000'
review_tools = ''
command = ['claude','--print','--no-session-persistence',
           '--output-format','stream-json','--verbose','--permission-mode','plan',
           '--setting-sources','','--settings',str(OUT/'review-settings.json'),
           '--tools',review_tools,'--strict-mcp-config','--mcp-config','{"mcpServers":{}}',
           '--effort','medium','--max-turns','8' if review_tools else '1']
if configured.get('model'):
    command += ['--model', configured['model']]
prefix = OUT / (stage+'-review-v6')
stdout_path = prefix.with_suffix('.stdout.json')
stderr_path = prefix.with_suffix('.stderr.txt')
start = time.monotonic()
timeout = 600 if stage in ['platform','domain','repair'] else 180
with stdout_path.open('x') as stdout, stderr_path.open('x') as stderr:
    try:
        result = subprocess.run(command,input=prompt,text=True,cwd=ROOT,env=env,
                                stdout=stdout,stderr=stderr,timeout=timeout)
        code = result.returncode
    except subprocess.TimeoutExpired:
        code = 124
receipt = {'stage':stage,'exit_code':code,'wall_seconds':time.monotonic()-start,
           'read_only':True,'tools':review_tools.split(',') if review_tools else [], 'auth':'configured route/model; token preferred when present; conflict removed only in child environment',
           'stdout':str(stdout_path),'stderr':str(stderr_path),
           'remaining_campaign_hours':(1940875.230219879-time.monotonic())/3600}
prefix.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
if code == 0:
    try:
        value=json.loads(stdout_path.read_text().splitlines()[-1])
        print(value.get('result','')[:22000])
    except json.JSONDecodeError:
        print('Result is not a single JSON object; inspect the saved stdout.')
sys.exit(code)
