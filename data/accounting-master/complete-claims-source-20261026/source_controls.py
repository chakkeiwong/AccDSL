"""Adverse syntax and admission cases for complete supplied claim source."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
import complete_text as text

HERE = Path(__file__).resolve().parent
opening = text.opening
core = text.core
def equal(a, b): return core.canonical(a) == core.canonical(b)
def dump(name, value): (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def run_controls(base, ensure, controls):
    selection = base['selection']
    source, resources = text.render(selection, base['contract'], base['completeness'], base['program'])
    def rejected(label, changed, reason, imports=None, reviewed=None):
        imports = resources if imports is None else imports
        reviewed = selection if reviewed is None else reviewed
        (HERE / f'adverse/{label}.acc').write_bytes(changed.encode())
        try:
            text.lower(changed, imports, reviewed)
        except text.Invalid as exc:
            ensure(reason in exc.reason, label + ':reason:' + exc.reason)
            loc, raw = exc.location, changed.encode()
            ensure(loc is not None, label + ':location')
            ensure(0 <= loc['byte_start'] <= loc['byte_end'] <= len(raw), label + ':bounds')
            ensure(sha256(raw[loc['byte_start']:loc['byte_end']]).hexdigest() == loc['slice_sha256'], label + ':span')
            ensure(raw[:loc['byte_start']].count(b'\n') + 1 == loc['line'], label + ':line')
            controls.append(dict(case=label, reason=exc.reason, location=loc))
            return loc
        raise AssertionError(label + ':accepted')

    population_line = source.split('\n')[2]
    reviewed_line = source.split('\n')[1]
    rejected('missing_population', source.replace(population_line + '\n', '', 1), 'required_population')
    rejected('duplicate_population', source.replace(population_line, population_line + '\n' + population_line, 1), 'complete_company_declaration')
    rejected('invalid_population_status', source.replace(' complete "/claims"', ' inferred "/claims"', 1), 'population_status')
    rejected('wrong_population_scope', source.replace(' complete "/claims"', ' complete "/balances"', 1), 'population_profile_or_scope')
    rejected('missing_provenance', source.replace(text.selected.j(base['completeness']['provenance']), '""', 1), 'text:string_token')
    rejected('missing_reviewed_selection', source.replace(reviewed_line + '\n', '', 1), 'required_reviewed_selection')
    rejected('duplicate_reviewed_selection', source.replace(reviewed_line, reviewed_line + '\n' + reviewed_line, 1), 'required_population')
    rejected('stale_selection_hash', source.replace(core.digest(selection), '0' * 64, 1), 'reviewed_selection_identity')
    changed = deepcopy(selection)
    changed['residuals'].append('Changed independently supplied selection')
    rejected('different_reviewed_selection', source, 'reviewed_selection_identity', reviewed=changed)
    rejected('repinned_but_different_selection', source.replace(core.digest(selection), core.digest(changed), 1),
             'source_differs_from_reviewed_selection', reviewed=changed)
    rejected('edited_opening', source.replace('Exact retained empty-opening conditions;', 'Edited retained empty-opening conditions;', 1),
             'source_differs_from_reviewed_selection')
    rejected('edited_invariant', source.replace('Supplied internal state only; customer selection', 'Edited internal state only; customer selection', 1),
             'source_differs_from_reviewed_selection')
    line = next(line for line in source.split('\n') if line.startswith('guarded "claim_total"'))
    rejected('edited_opening_predicate', source.replace(line, line.replace('(eq ', '(le ', 1), 1),
             'source_differs_from_reviewed_selection')
    line = next(line for line in source.split('\n') if line.startswith('guarded "remaining_nonnegative"'))
    rejected('edited_invariant_predicate', source.replace(line, line.replace('(le ', '(eq ', 1), 1),
             'source_differs_from_reviewed_selection')
    extra = deepcopy(resources)
    extra[core.digest(base['contract'])] = deepcopy(base['contract'])
    rejected('opaque_algorithm_resource', source, 'exact_resource_population', imports=extra)
    rejected('missing_resource', source, 'missing_resource', imports={})
    rejected('wrong_target', source.replace(opening.PROGRAM, 'WrongProgram/1', 1), 'source_profile')
    rejected('missing_outer_end', source.replace('end_complete_claims_company;', '', 1), 'incomplete_source')
    rejected('trailing_declaration', source + 'population "extra";\n', 'declaration_after_end')
    rejected('missing_contract_residual', '\n'.join(line for line in source.split('\n') if not line.startswith('contract_residual ')),
             'required_contract_residual')
    bad = source.replace('begin_selected_company;', 'contract_residual "汉字/é/\u2028";\nbegin_selected_company;', 1)
    bad = bad.replace('book_invariant ', '@book_invariant ', 1).replace('\n', '\r\n')
    loc = rejected('nested_utf8_crlf', bad, 'unexpected_token')
    ensure(loc['granularity'] == 'declaration' and
           bad.encode()[loc['byte_start']:loc['byte_end']].startswith(b'@book_invariant '),
           'nested_utf8_crlf:inherited_declaration_granularity')
    token_bad = source.replace('begin_selected_company;', 'contract_residual "汉字/é/\u2028";\nbegin_selected_company;', 1)
    token_bad = token_bad.replace('opening_admission ', '@opening_admission ', 1).replace('\n', '\r\n')
    token_loc = rejected('nested_opening_utf8_crlf', token_bad, 'unexpected_token')
    ensure(token_loc['granularity'] == 'token' and
           token_bad.encode()[token_loc['byte_start']:token_loc['byte_end']] == b'@',
           'nested_opening_utf8_crlf:exact_bad_token')

    for status in ('partial', 'unknown'):
        changed = source.replace(' complete "/claims"', ' ' + status + ' "/claims"', 1)
        lowered = text.lower(changed, resources, selection)
        actual = text.execute_source(changed, resources, selection)
        ensure(lowered['completeness']['status'] == status and not lowered['opening_admitted'], status + ':not_inferred_complete')
        ensure(actual['status'] == 'unresolved' and actual['reason'] == 'complete_supplied_population_required', status + ':unresolved')
        ensure(not actual['executed'] and actual['delegated'] is None, status + ':not_executed')
        controls.append(dict(case='population_' + status, result=actual))
        (HERE / f'adverse/population_{status}.acc').write_text(changed)

    # Structural lowering cannot invoke admission or execution callbacks.
    originals = {name: getattr(opening, name) for name in ('assess', 'execute')}
    def disabled(*args, **kwargs): raise AssertionError('admission during structural lowering')
    try:
        for name in originals: setattr(opening, name, disabled)
        lowered = text.lower(source, resources, selection)
        ensure(not lowered['opening_admitted'] and not lowered['executed'], 'lowering_does_not_admit')
    finally:
        for name, value in originals.items(): setattr(opening, name, value)
    controls.append(dict(case='lowering_does_not_admit', passed=True))

    crlf = '\r\n'.join('  ' + line for line in source.split('\n'))
    lowered = text.lower(crlf, resources, selection)
    normal = text.lower(source, resources, selection)
    ensure(equal(lowered['program'], normal['program']) and lowered['source_sha256'] != normal['source_sha256'], 'crlf_program')
    ensure(equal(text.execute_source(crlf, resources, selection), text.execute_source(source, resources, selection)), 'crlf_full_execution')
    for loc in lowered['source_spans'] + lowered['nested_source_spans'] + [b['location'] for b in lowered['blocks']]:
        raw = crlf.encode()
        ensure(sha256(raw[loc['byte_start']:loc['byte_end']]).hexdigest() == loc['slice_sha256'], 'crlf_translated_span')
        ensure(raw[:loc['byte_start']].count(b'\n') + 1 == loc['line'], 'crlf_translated_line')
    (HERE / 'examples/alpha-crlf.acc').write_bytes(crlf.encode())
    controls.append(dict(case='crlf_full_execution_and_spans', passed=True))

    altered = deepcopy(base['completeness'])
    altered['provenance'] += ' 汉字/é/\u2028'
    unicode_source, imports = text.render(selection, base['contract'], altered, base['program'])
    ensure(text.lower(unicode_source, imports, selection)['completeness'] == altered, 'unicode_provenance_roundtrip')
    controls.append(dict(case='unicode_provenance_roundtrip', passed=True))
    (HERE / 'examples/alpha-unicode.acc').write_text(unicode_source)
    corrupt_states(base, ensure, controls)


def corrupt_states(base, ensure, controls):
    path = HERE.parent / 'nonempty-opening-audit-20261026/controls.json'
    for row in json.loads(path.read_text()):
        program = deepcopy(base['program'])
        program['opening'] = deepcopy(row['input']['opening'])
        population = opening.population(program['opening'], 'Explicit complete corrupted test population')
        source, resources = text.render(base['selection'], base['contract'], population, program)
        lowered = text.lower(source, resources, base['selection'])
        ensure(equal(lowered['input'], row['input']), row['case'] + ':exact_corrupt_input')
        actual = text.execute_source(source, resources, base['selection'])
        expected = opening.execute(base['selection'], base['contract'], row['input'], population, program,
            opening.make_program_call(base['selection'], base['contract'], row['input'], population, program))
        ensure(actual['status'] == 'invalid' and not actual['executed'] and actual['delegated'] is None, row['case'] + ':refused_before_execution')
        ensure(equal(actual['admission']['invariant'], row['invariant']), row['case'] + ':original_invariant_result')
        ensure(actual['program_order_sha256'] == opening.a.order_digest(lowered['program']), row['case'] + ':lowered_order')
        ensure(expected['program_order_sha256'] == opening.a.order_digest(program), row['case'] + ':typed_order')
        compared = deepcopy(actual)
        compared['program_order_sha256'] = expected['program_order_sha256']
        ensure(equal(compared, expected), row['case'] + ':full_refusal_result')
        (HERE / f'adverse/{row["case"]}.acc').write_text(source)
        dump(f'adverse/{row["case"]}.resources.json', resources)
        dump(f'results/refusal-{row["case"]}.json', dict(actual=actual, expected=expected, exception_paths=['program_order_sha256']))
        controls.append(dict(case=row['case'], result=actual))
