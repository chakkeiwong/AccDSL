"""Explicit supplied-claim completeness around the retained company language."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
for folder in ('selected-company-source-20261026', 'complete-claims-opening-20261026'):
    sys.path.insert(0, str(HERE.parent / folder))
import company_text as selected
import complete_opening as opening

syntax = selected.eligibility
core = opening.core
Invalid = syntax.Invalid
need = syntax.need
PROFILE = 'CompleteClaimsCompanyText/1'


def lower(source, resources, reviewed_selection):
    location = None
    try:
        rows = syntax.source_rows(source)
        raw = source.encode('utf-8')
        state = 'header'
        index = 0
        residuals = []
        spans = []
        nested = None
        selection_location = None
        while index < len(rows):
            line, location = rows[index]
            index += 1
            if not line.strip():
                continue
            spans.append(location)
            need(state != 'done', 'declaration_after_end', location)
            r = syntax.Reader(source, line, location)
            word = r.take('word')
            if state == 'header':
                need(word == 'complete_claims_company' and r.string() == PROFILE
                     and r.string() == opening.PROGRAM, 'source_profile', location)
                state = 'selection'
            elif state == 'selection':
                need(word == 'reviewed_selection', 'required_reviewed_selection', location)
                expected = r.string()
                selection_location = location
                need(type(reviewed_selection) is dict, 'reviewed_selection_type', location)
                need(expected == core.digest(reviewed_selection), 'reviewed_selection_identity', location)
                state = 'population'
            elif state == 'population':
                need(word == 'population', 'required_population', location)
                profile, status, pointer, provenance = r.string(), r.take('word'), r.string(), r.string()
                need(profile == opening.POPULATION and pointer == '/claims', 'population_profile_or_scope', location)
                need(status in ('complete', 'partial', 'unknown'), 'population_status', location)
                opening.c.base.text(provenance, 'population_provenance')
                state = 'body'
            elif state == 'body':
                if word == 'contract_residual':
                    residuals.append(r.string())
                else:
                    need(word == 'begin_selected_company', 'complete_company_declaration:' + word, location)
                    r.finish()
                    start = raw.find(b'\n', location['byte_end']) + 1
                    need(start > 0, 'embedded_newline_required', location)
                    first_line = location['line'] + 1
                    while index < len(rows) and rows[index][0].strip() != 'end_selected_company;':
                        index += 1
                    need(index < len(rows), 'unterminated_selected_company', location)
                    end = rows[index][1]['byte_start']
                    index += 1
                    def translated(loc):
                        return syntax.span(source, start + loc['byte_start'], start + loc['byte_end'],
                                           first_line + loc['line'] - 1, loc.get('granularity', 'declaration'))
                    try:
                        nested = selected.lower(raw[start:end].decode('utf-8'), resources)
                    except Exception as exc:
                        loc = getattr(exc, 'location', None)
                        loc = translated(loc) if loc else syntax.span(source, start, end, first_line, 'block')
                        raise Invalid(getattr(exc, 'reason', str(exc)), loc) from exc
                    block_location = syntax.span(source, start, end, first_line, 'block')
                    nested_spans = [translated(loc) for loc in nested['source_spans']]
                    nested_blocks = [dict(b, location=translated(b['location'])) for b in nested['blocks']]
                    state = 'end'
                    continue
            else:
                need(word == 'end_complete_claims_company', 'required_complete_company_end', location)
                state = 'done'
            r.finish()
        need(state == 'done' and nested is not None, 'incomplete_source:' + state, location)
        need(core.canonical(nested['selection']) == core.canonical(reviewed_selection),
             'source_differs_from_reviewed_selection', selection_location)
        need(bool(residuals), 'required_contract_residual', location)
        contract = opening.make_contract(nested['opening_template'], nested['program']['state_invariant'])
        contract['residuals'] = residuals
        opening.derive(reviewed_selection, contract)
        population = dict(profile=profile, status=status, map_pointer=pointer,
                          book_sha256=core.digest(nested['input']['opening']), provenance=provenance)
        call = opening.make_program_call(reviewed_selection, contract, nested['input'], population, nested['program'])
        return dict(profile=PROFILE, status='lowered_structural', selection=deepcopy(reviewed_selection),
                    contract=contract, input=nested['input'], completeness=population, program=nested['program'], call=call,
                    source_sha256=sha256(raw).hexdigest(), source_spans=spans, nested_source_spans=nested_spans,
                    blocks=[dict(kind='selected_company', location=block_location,
                                 source_sha256=nested['source_sha256'])] + nested_blocks,
                    resources=nested['resources'], executed=False, opening_admitted=False,
                    source_admission=False, accounting_admission=False, actual_population_completeness=False)
    except Exception as exc:
        if isinstance(exc, Invalid):
            raise
        raise Invalid(getattr(exc, 'reason', str(exc)), location) from exc


def execute_source(source, resources, reviewed_selection):
    obj = lower(source, resources, reviewed_selection)
    return opening.execute(obj['selection'], obj['contract'], obj['input'], obj['completeness'], obj['program'], obj['call'])


def render(selection, contract, population, program):
    nested, resources = selected.render(selection, contract['empty_template'], program)
    j = selected.j
    rows = ['complete_claims_company ' + j(PROFILE) + ' ' + j(opening.PROGRAM) + ';',
            'reviewed_selection ' + j(core.digest(selection)) + ';',
            'population ' + j(population['profile']) + ' ' + population['status'] + ' '
            + j(population['map_pointer']) + ' ' + j(population['provenance']) + ';']
    rows.extend('contract_residual ' + j(value) + ';' for value in contract['residuals'])
    rows.append('begin_selected_company;')
    rows.extend(nested.rstrip('\n').split('\n'))
    rows.extend(['end_selected_company;', 'end_complete_claims_company;'])
    source = '\n'.join(rows) + '\n'
    lowered = lower(source, resources, selection)
    for key, value in [('selection', selection), ('contract', contract), ('completeness', population), ('program', program)]:
        need(core.canonical(lowered[key]) == core.canonical(value), 'render_roundtrip:' + key)
    return source, resources
