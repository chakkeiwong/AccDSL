"""Deterministic source-to-typed-gate conformance, with frozen comparators."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys
import time
import eligibility_text as text
import declared_receivable_lifecycle_v1 as native

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = HERE.parent / 'ordered-event-eligibility-20261026'
g = text.gate

def read(path):
    return json.loads(path.read_text())

def sha(path):
    return sha256(path.read_bytes()).hexdigest()

def dump(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

def equal(a, b):
    return g.core.canonical(a) == g.core.canonical(b)

def main():
    start = time.monotonic(); assertions = []; controls = []; comparisons = []; roundtrips = []
    for folder in ('examples', 'adverse'):
        (HERE/folder).mkdir(exist_ok=True)
    lock_path = HERE/'source-lock.json'
    if not lock_path.exists():
        lock = read(PRIOR/'source-lock.json')
        paths = [p for p in PRIOR.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
        paths += [ROOT/'scripts'/n for n in ('method_requirement_text_v1.py', 'method_requirement_text_v2.py')]
        paths += [ROOT/'docs/design/proposal/manuscript-opening-binding-20261026/accounting-product-proposal.pdf',
                  ROOT/'docs/design/proposal/manuscript-observation-quotient-20261026/simulation-foundations.pdf']
        for module in list(sys.modules.values()):
            filename = getattr(module, '__file__', None)
            if filename:
                p = Path(filename).resolve()
                if p.is_relative_to(ROOT) and not p.is_relative_to(HERE) and p.suffix == '.py':
                    paths.append(p)
        for path in paths:
            name = str(path.relative_to(ROOT)); digest = sha(path)
            assert name not in lock or lock[name] == digest, name
            lock[name] = digest
        dump('source-lock.json', lock)
    lock = read(lock_path)
    for name, digest in lock.items():
        assert sha(ROOT/name) == digest, name

    def ensure(ok, label):
        assertions.append(dict(check=label, passed=bool(ok)))
        assert ok, label

    templates = {(owner, kind): read(PRIOR/f'templates/{owner}.{kind}.json')
                 for owner in ('alpha', 'beta') for kind in ('sale', 'collect', 'assess')}
    cases, refusals = read(PRIOR/'cases.json'), read(PRIOR/'refusals.json')
    sources = {}
    for key, template in templates.items():
        source = text.render(template); sources[key] = source
        row = next(r for r in cases if (r['company'], r['method']) == key)
        lowered = text.compile_text(source, row['before'], row['parameters']['memory_definition'])
        ensure(equal(lowered['template'], template), str(key)+':complete_template')
        ensure(text.render(lowered['template']) == source, str(key)+':canonical_source')
        ensure(not lowered['executed'], str(key)+':compilation_not_execution')
        filename = '.'.join(key)
        (HERE/f'examples/{filename}.acc').write_text(source)
        dump(f'examples/{filename}.compiled.json', lowered)
        roundtrips.append(dict(company=key[0], operation=key[1], source=f'examples/{filename}.acc',
                               source_sha256=lowered['source_sha256'], template_sha256=lowered['template_sha256'], equal=True))

    def evaluate(source, book, event, parameters, call=None):
        template = text.lower(source)['template']
        call = g.make_call(template, book, event, parameters['schemas'], parameters['memory_definition']) if call is None else call
        return text.assess_source(source, book, event, parameters['schemas'], parameters['memory_definition'], call)

    disabled_names = ('run', 'make_request', 'event_types', 'validate')
    originals = {name: getattr(native, name) for name in disabled_names}
    def disabled(*args, **kwargs):
        raise AssertionError('native lifecycle used during source replay')
    try:
        for name in originals:
            setattr(native, name, disabled)
        for rows, refused in ((cases, False), (refusals, True)):
            for row in rows:
                key = (row['company'], row['command']['method_key'] if refused else row['method'])
                event = row['command']['event'] if refused else row['event']
                before = g.core.digest(row)
                actual = evaluate(sources[key], row['before'], event, row['parameters'])
                expected = row['actual'] if refused else row['gate']
                ensure(equal(actual, expected), row['case']+':full_gate')
                ensure(g.core.digest(row) == before, row['case']+':inputs_preserved')
                if not refused:
                    ensure(equal(g.c.frontend.v2.propose(row['before'], row['request']), row['transition']), row['case']+':retained_transition')
                comparisons.append(dict(case=row['case'], refused=refused, company=key[0], operation=key[1],
                    expected=expected, actual=actual, complete_equal=True, saved_input_sha256=before))
        run_controls(sources, templates, cases, refusals, evaluate, ensure, controls)
    finally:
        for name, value in originals.items():
            setattr(native, name, value)
    dump('comparisons.json', comparisons); dump('roundtrips.json', roundtrips); dump('controls.json', controls)
    for name, digest in lock.items():
        ensure(sha(ROOT/name) == digest, 'protected:'+name)
    summary = dict(passed=True, templates=len(templates), complete_eligible_cases=len(cases),
        complete_refusals=len(refusals), controls=len(controls), assertions=len(assertions), protected_files=len(lock),
        native_lifecycle_disabled=list(disabled_names), direct_algorithm_source=True, independent_reader_pending=True,
        general_language_complete=False, source_admission=False, accounting_admission=False, production_ready=False)
    dump('checks.json', summary); dump('assertions.json', assertions)
    git = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True)
    dump('run-manifest.json', dict(git_commit=git.stdout.strip() if git.returncode == 0 else 'unavailable',
        command='env CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/ordered-eligibility-source-20261026/verify.py',
        environment=sys.version, cpu_gpu='CPU; GPU intentionally hidden', random_seeds='N/A deterministic',
        wall_seconds=time.monotonic()-start, data_version=sha(lock_path),
        plan_file='docs/plans/accounting-ordered-eligibility-source-20261026.md',
        result_file='data/accounting-master/ordered-eligibility-source-20261026/result.md',
        artifacts=['examples', 'adverse', 'comparisons.json', 'roundtrips.json', 'controls.json', 'checks.json', 'assertions.json'],
        implementation_sha256={n: sha(HERE/n) for n in ('eligibility_text.py', 'verify.py', 'design.md')},
        timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))


def run_controls(sources, templates, cases, refusals, evaluate, ensure, controls):
    row = next(r for r in cases if r['company'] == 'alpha' and r['method'] == 'collect')
    source = sources['alpha', 'collect']; template = templates['alpha', 'collect']
    book, event, parameters = row['before'], row['event'], row['parameters']
    definition = parameters['memory_definition']

    def rejected(label, source, reason, granularity=None, book=book):
        path = HERE/f'adverse/{label}.acc'; path.write_bytes(source.encode())
        try:
            text.compile_text(source, book, definition)
        except text.Invalid as exc:
            ensure(reason in exc.reason, label+':reason:'+exc.reason)
            loc = exc.location
            ensure(loc is not None, label+':location_present')
            raw = source.encode(); start, end = loc['byte_start'], loc['byte_end']
            ensure(0 <= start <= end <= len(raw), label+':byte_bounds')
            ensure(sha256(raw[start:end]).hexdigest() == loc['slice_sha256'], label+':slice_hash')
            ensure(raw[:start].count(b'\n')+1 == loc['line'], label+':line_number')
            if granularity:
                ensure(loc['granularity'] == granularity, label+':granularity')
            controls.append(dict(case=label, status='invalid', reason=exc.reason, location=loc, source=str(path.relative_to(HERE))))
            return loc
        raise AssertionError(label+':invalid_source_accepted')

    rejected('missing_semicolon', source.replace('end_stage;', 'end_stage', 1), 'missing_token', 'token')
    rejected('unknown_declaration', source.replace('full_input', 'unknown_input', 1), 'unknown_declaration', 'token')
    rejected('unknown_binding', source.replace('(event_input', '(python_call', 1), 'unsupported_source_kind', 'token')
    rejected('unknown_operator', source.replace('(ref "approved")', '(execute "approved")', 1), 'unknown_operator', 'token')
    rejected('missing_end', source.replace('end_eligibility;', ''), 'incomplete_source', 'token')
    context_line = next(line for line in source.splitlines() if line.startswith('context '))
    rejected('duplicate_context', source.replace(context_line, context_line+'\n'+context_line), 'duplicate_declaration', 'declaration')
    binding_line = next(line for line in source.splitlines() if line.startswith('bind '))
    rejected('duplicate_binding', source.replace(binding_line, binding_line+'\n'+binding_line), 'duplicate_declaration', 'declaration')
    input_line = next(line for line in source.splitlines() if line.startswith('full_input '))
    rejected('duplicate_input', source.replace(input_line, input_line+'\n'+input_line), 'duplicate_declaration', 'declaration')
    rejected('duplicate_json_key', source.replace('context {', 'context {"book":"duplicate",', 1), 'duplicate_json_key', 'declaration')
    rejected('missing_binding', source.replace(binding_line+'\n', '', 1), 'exact_stage_bindings', 'stage')
    rejected('undeclared_event_input', source.replace('(event_input "approved")', '(event_input "absent")', 1), 'undeclared_event_source', 'stage')
    known_line = next(line for line in source.splitlines() if line.startswith('required_known '))
    rejected('missing_required_known', source.replace(known_line, '', 1), 'explicit_required_known', 'declaration')
    rejected('missing_context', source.replace(context_line+'\n', ''), 'incomplete_template', 'declaration')
    rejected('trailing_tokens', source.replace('end_stage;', 'end_stage; true', 1), 'trailing_tokens', 'token')
    rejected('declaration_after_end', source+'end_eligibility;\n', 'declaration_after_end', 'declaration')

    bad = deepcopy(template); bad['stages'][-1]['bindings']['owner']['after_stage'] = 'future'
    rejected('forward_presence', text.render(bad), 'forward_or_missing_presence_stage', 'stage')
    bad = deepcopy(template); bad['stages'][2]['manifest']['requirements'][0]['guard']['value'] = False
    rejected('conditional_presence', text.render(bad), 'unproved_row_presence', 'stage')
    bad = deepcopy(template); bad['stages'][0]['bindings']['approved'] = {'kind': 'event_metadata', 'field': 'date'}
    rejected('binding_type', text.render(bad), 'binding_type_mismatch', 'stage')
    bad = deepcopy(template); bad['stages'][-1]['bindings']['owner']['field'] = 'missing'
    empty = next(r['before'] for r in cases if r['company'] == 'alpha' and r['method'] == 'sale')
    rejected('invalid_field_empty_map', text.render(bad), 'row_scalar_field', 'stage', book=empty)
    rejected('invalid_late_stage', text.render(bad), 'row_scalar_field', 'stage')
    bad_event = deepcopy(event); bad_event['inputs']['approved']['value']['value'] = False
    try:
        evaluate(text.render(bad), book, bad_event, parameters)
    except text.Invalid as exc:
        ensure(exc.reason == 'row_scalar_field', 'skipped_stage_compiles_before_false_approval')
        controls.append(dict(case='skipped_stage_compiled', reason=exc.reason))
    else:
        raise AssertionError('malformed skipped stage accepted')
    rejected('duplicate_stage', source.replace('stage "unsealed_day"', 'stage "approval"', 1), 'duplicate_stage', 'declaration')
    unicode_template = deepcopy(template)
    unicode_template['stages'][0]['manifest']['inputs']['approved']['source_ref'] = '资料\u2028line/é'
    unicode_source = text.render(unicode_template)
    ensure(equal(text.compile_text(unicode_source, book, definition)['template'], unicode_template), 'unicode_rule_literal_roundtrip')
    controls.append(dict(case='unicode_rule_literal_roundtrip', passed=True))

    changed = source.replace('(ref "approved")', '(not (ref "approved"))', 1)
    result = evaluate(changed, book, event, parameters)
    ensure(result['status'] == 'unsupported' and result['reason'] == 'applicability_not_selected', 'predicate_edit:consequence')
    ensure(result['template_sha256'] != row['gate']['template_sha256'], 'predicate_edit:identity')
    (HERE/'examples/changed-predicate.acc').write_text(changed)
    controls.append(dict(case='consequential_predicate', result=result))

    sealed = next(r for r in refusals if r['company'] == 'alpha' and ':order:sealed_before_missing' in r['case'])
    changed_template = deepcopy(template)
    changed_template['stages'][1], changed_template['stages'][2] = changed_template['stages'][2], changed_template['stages'][1]
    changed = text.render(changed_template)
    result = evaluate(changed, sealed['before'], sealed['command']['event'], sealed['parameters'])
    ensure(result['reason'] == 'unknown_claim' and sealed['actual']['reason'] == 'assessment_day_sealed', 'order_edit:consequence')
    (HERE/'examples/changed-order.acc').write_text(changed)
    controls.append(dict(case='consequential_order', original_reason=sealed['actual']['reason'], result=result))

    variant = source.replace('end_eligibility;', 'residual "审计/é/line\u2028separator";\nend_eligibility;')
    baseline = text.compile_text(variant, book, definition)
    crlf = '\r\n'.join('  '+line+'  ' for line in variant.split('\n'))
    checked = text.compile_text(crlf, book, definition)
    ensure(equal(baseline['template'], checked['template']), 'unicode_crlf:semantics')
    ensure(baseline['source_sha256'] != checked['source_sha256'], 'unicode_crlf:source_identity')
    for loc in checked['source_spans']+checked['stage_spans']:
        raw = crlf.encode()[loc['byte_start']:loc['byte_end']]
        ensure(sha256(raw).hexdigest() == loc['slice_sha256'], 'unicode_crlf:span')
    broken = crlf.replace('end_eligibility;', 'end_eligibility; @')
    loc = rejected('unicode_crlf_bad_token', broken, 'unexpected_token', 'token')
    ensure(broken.encode()[loc['byte_start']:loc['byte_end']] == b'@', 'unicode_crlf:exact_bad_token')
    (HERE/'examples/unicode-crlf.acc').write_bytes(crlf.encode())
    controls.append(dict(case='unicode_crlf_semantics', source_sha256=checked['source_sha256'], template_sha256=checked['template_sha256']))

    rejected('lone_cr', source.replace('context ', 'context \r', 1), 'source_control', 'token')
    rejected('bom', '\ufeff'+source, 'source_control', 'token')
    long_source = source+' '*(g.core.MAX_BYTES+1)
    try:
        text.lower(long_source)
    except text.Invalid as exc:
        ensure(exc.reason == 'source_size_limit', 'source_size_limit')
        controls.append(dict(case='source_size_limit', reason=exc.reason))
    else:
        raise AssertionError('oversize accepted')
    rejected('declaration_limit', 'end_eligibility;\n'*(g.core.MAX_NODES+1), 'declaration_limit', 'declaration')
    bad = deepcopy(template); bad['stages'] = [dict(deepcopy(template['stages'][0]), id='stage'+str(i)) for i in range(65)]
    # The renderer deliberately rejects structurally incomplete source.
    try:
        text.render(bad)
    except text.Invalid as exc:
        ensure(exc.reason == 'stage_limit', 'stage_limit'); controls.append(dict(case='stage_limit', reason=exc.reason))
    else:
        raise AssertionError('stage limit accepted')
    nested = '(calendar_adjacent '* (g.core.MAX_DEPTH+2) + '(book_date)' + ' (period_end))'*(g.core.MAX_DEPTH+2)
    rejected('binding_depth', source.replace('(event_input "approved")', nested, 1), 'binding_limit', 'token')
    nested = '(not '*(g.core.MAX_DEPTH+2)+'(ref "approved")'+')'*(g.core.MAX_DEPTH+2)
    rejected('expression_depth', source.replace('(ref "approved")', nested, 1), 'expression_limit', 'token')

    stale = g.make_call(template, book, event, parameters['schemas'], definition)
    changed = source.replace('(ref "approved")', '(not (ref "approved"))', 1)
    result = evaluate(changed, book, event, parameters, stale)
    ensure(result['reason'] == 'stale_template', 'stale_template_refused')
    controls.append(dict(case='stale_selected_template', result=result))


if __name__ == '__main__':
    main()
