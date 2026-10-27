"""Bind retrieved documentary evidence; no accounting method promotion."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
SOURCES = BASE / 'sources'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path):
    return str(path.relative_to(ROOT))
def save(name, data):
    (BASE / name).write_text(json.dumps(data, indent=2) + '\n')

original = json.loads((BASE / 'source-manifest.json').read_text())
index = next(r for r in original['responses'] if r['id'] == 'gt-index')
responses = [index]
roles = {
 'gt-reversal': '2022 technical interpretation; inspected, no all-zero allocation',
 'gt-ias36-series': 'discovery collection only',
 'gt-reversal-pdf': 'eight-page technical article; text inspected, pages 5-7 visually checked',
 'gt-reversal-sandbox-failure': 'sandbox DNS failure; superseded by successful trusted retry',
 'gt-ias36-series-sandbox-failure': 'sandbox DNS failure; superseded by successful trusted retry',
}
for stem, role in roles.items():
    raw = SOURCES / (stem + '-curl.json')
    m, _ = json.JSONDecoder().raw_decode(raw.read_text())
    response = SOURCES / ('gt-reversal.pdf' if stem == 'gt-reversal-pdf' else stem + '.html')
    headers = SOURCES / (stem + '.headers')
    responses.append({
      'id': stem, 'requested_url': m.get('url'), 'effective_url': m['url_effective'],
      'http_status': m['http_code'], 'curl_exit': m['exitcode'],
      'size_download': m['size_download'], 'wall_seconds': m['time_total'],
      'response_path': rel(response) if response.exists() else None,
      'response_sha256': sha(response) if response.exists() else None,
      'headers_path': rel(headers) if headers.exists() else None,
      'raw_metrics_path': rel(raw), 'raw_metrics_sha256': sha(raw), 'role': role,
      'trust': 'sandbox' if 'sandbox-failure' in stem else 'trusted',
    })
bindings = [{'path': rel(p), 'bytes': p.stat().st_size, 'sha256': sha(p)}
            for p in sorted(SOURCES.iterdir()) if p.is_file()]
save('source-manifest.json', {'recorded_utc': datetime.now(timezone.utc).isoformat(),
 'responses': responses, 'source_bindings': bindings,
 'technical_scope': 'one technical article and its linked PDF; no all-zero allocation support'})
checks = [
 {'name':'individual_asset_displayed_reversal', 'computed':1300-1012, 'source_table':288, 'pass':1300-1012==288},
 {'name':'source_analysis_316_discrepancy', 'computed_closing':1012+316, 'recoverable_cap':1300, 'excess':28, 'pass':1012+316-1300==28},
 {'name':'positive_weight_cgu_reversal', 'computed':min(1500,1440)-1012, 'source_table':428, 'pass':min(1500,1440)-1012==428},
 {'name':'cgu_example_not_all_zero', 'eligible_aggregate_carrying':1012, 'pass':1012>0},
 {'name':'candidate_unchanged', 'pass':sha(ROOT/'docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf')=='afbbdbe73d6ac25a9e59ea6f39e25b2e579ebd1e5fcad0ac9959e87cc6ab5d80'},
]
for binding in bindings:
    checks.append({'name':binding['path'], 'pass':sha(ROOT/binding['path'])==binding['sha256']})
assert all(c['pass'] for c in checks)
save('checks.json', {'checks':checks, 'passed':len(checks), 'failed':0,
 'scope':'source preservation and displayed-figure checks only'})
commands = []
for stem, name, url in [
 ('gt-reversal','gt-reversal.html','https://www.grantthornton.global/en/insights/articles/IFRS-ias-36/ifrs-Reversing-impairment-losses/'),
 ('gt-ias36-series','gt-ias36-series.html','https://www.grantthornton.global/en/insights/articles/IFRS-ias-36/'),
 ('gt-reversal-pdf','gt-reversal.pdf','https://www.grantthornton.global/globalassets/1.-member-firms/global/insights/insight-content-blocks-and-media/ifrs/ias-36/12.-reversing-impairment-losses.pdf')]:
    commands.append({'tool':'curl','permissions':'require_escalated','arguments':['--silent','--show-error','--location','--max-redirs','5','--connect-timeout','15','--max-time','45','--max-filesize','15728640','--dump-header',rel(SOURCES/(stem+'.headers')),'--output',rel(SOURCES/name),'--write-out','%{json}\n',url], 'stdout_path':rel(SOURCES/(stem+'-curl.json'))})
save('run-manifest.json', {
 'git_commit':'03fea070f089821f4759e49a4466a3399b7fc078',
 'git_scope':'existing worktree identity; no commit or clean-tree claim',
 'environment':'existing bash, curl, Python standard library, pdftotext and pdftoppm; no installation',
 'cpu_gpu':'CPU document tools only; no GPU detection, initialization or ML import',
 'random_seeds':'N/A: deterministic documentary inquiry',
 'data_version':'retained 23 March 2022 publisher article and copyright-2022 PDF, bound by hashes',
 'wall_time':{'overall_seconds':None,'reason':'overall resumed inquiry elapsed time was not measured','per_response_seconds':{r['id']:r['wall_seconds'] for r in responses}},
 'plan_file':'docs/plans/accounting-zero-weight-cgu-publisher-followup-20261018.md',
 'result_file':rel(BASE/'source-reading.md'), 'source_manifest':rel(BASE/'source-manifest.json'),
 'commands':commands, 'local_commands':[
  'python3 '+rel(BASE/'extract_sources.py'),
  'pdftotext -layout '+rel(SOURCES/'gt-reversal.pdf')+' '+rel(SOURCES/'gt-reversal-pdf.txt'),
  'pdftoppm -f 5 -l 7 -scale-to 1500 -png '+rel(SOURCES/'gt-reversal.pdf')+' /tmp/accdsl-gt-reversal',
  'python3 '+rel(BASE/'finish_inquiry.py')],
 'artifacts':[rel(p) for p in sorted(BASE.iterdir()) if p.is_file()],
 'source_reading_sha256':sha(BASE/'source-reading.md'),
 'disposition':'dependent all-zero allocation unsupported; independent manuscript review continues',
})
print(json.dumps({'responses':len(responses),'source_bindings':len(bindings),'checks_passed':len(checks),'all_zero_allocation':'unsupported'}))
