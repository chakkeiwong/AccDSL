"""Bounded semantic validator for the authored debt IR; no general compiler.

Rejects unsupported populated sections and operations explicitly. External
exports are frozen data, never executable code or network-loaded dependencies.
"""
from datetime import date, datetime
from fractions import Fraction
import hashlib
import json
import re

import jsonschema

from build_demo_registry import build as expected_registry, canonical


class Invalid(Exception):
    def __init__(self, code, location, detail):
        self.code, self.location, self.detail = code, location, detail
        super().__init__(f'{code} at {location}: {detail}')


def require(condition, code, location, detail):
    if not condition:
        raise Invalid(code, location, detail)


def strict_json(text):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, 'DuplicateJSONKey', key, 'Duplicate keys lose source information')
            out[key] = value
        return out
    def invalid_constant(value):
        raise Invalid('InvalidJSONNumber', value, 'Non-finite numbers are not JSON')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant)


def rational(value, location):
    n, d = int(value['n']), int(value['d'])
    require(d > 0, 'InvalidRational', location, 'Positive denominator required')
    q = Fraction(n, d)
    require((str(q.numerator), str(q.denominator)) == (value['n'], value['d']),
            'NoncanonicalRational', location, 'Use reduced terms and zero 0/1')
    return q


def iso_date(value, location):
    try:
        result = date.fromisoformat(value)
        require(result.isoformat() == value, 'InvalidDate', location, 'Use YYYY-MM-DD')
        return result
    except ValueError as exc:
        raise Invalid('InvalidDate', location, str(exc)) from exc


def instant(value, location):
    try:
        t = datetime.fromisoformat(value.replace('Z', '+00:00'))
        require(t.tzinfo is not None, 'MissingTimezone', location, 'Timestamp requires timezone')
        return t
    except ValueError as exc:
        raise Invalid('InvalidTimestamp', location, str(exc)) from exc


SUPPORTED = {'models', 'contexts', 'sourceSpans', 'documents', 'observations',
             'entities', 'books', 'accounts', 'symbols', 'expressions', 'constraints',
             'assumptions', 'alternatives', 'contracts', 'states', 'packages',
             'scenarios', 'reviewDecisions', 'evidenceViews', 'modelScopes',
             'historyFamilies', 'reportMappings'}


class Validator:
    def __init__(self, document, registry, schema, root):
        try:
            jsonschema.Draft202012Validator(schema).validate(document)
        except jsonschema.ValidationError as exc:
            raise Invalid('StructuralError', '/'.join(map(str, exc.path)), exc.message) from exc
        self.doc, self.root, self.nodes, self.kinds = document, root, {}, {}
        self.external, self.values, self.inferred = {}, {}, {}
        for section, rows in document.items():
            if section == 'schema_version':
                continue
            require(not rows or section in SUPPORTED, 'UnsupportedSection', section,
                    'This preparation checker does not validate this populated section')
            for row in rows:
                identifier = row['id']
                require(identifier not in self.nodes, 'DuplicateID', identifier, 'IDs are globally unique')
                self.nodes[identifier], self.kinds[identifier] = row, section
        expected = {r['id']: r for r in expected_registry()['records']}
        require(isinstance(registry, dict) and registry.get('version') == '1' and
                registry.get('profile') == 'authored-debt-example' and
                isinstance(registry.get('records'), list), 'UnsupportedRegistry', 'registry',
                'Expected the versioned authored debt export set')
        for row in registry['records']:
            require(isinstance(row, dict) and set(row) == {'id', 'kind', 'artifact', 'sha256', 'pointer', 'value'},
                    'RegistryShape', 'registry', 'Export has missing or unknown fields')
            identifier = row['id']
            require(isinstance(identifier, str) and identifier in expected, 'UnsupportedRegistry', str(identifier),
                    'Export outside this fixed demonstration profile')
            template = expected[identifier]
            require(all(row[k] == template[k] for k in ['kind', 'artifact', 'pointer', 'value']),
                    'RegistryBinding', identifier, 'Export kind, location or built-in definition differs from this profile')
            require(identifier not in self.external and identifier not in self.nodes,
                    'DuplicateID', identifier, 'External and internal exports cannot collide')
            if row['artifact'] is None:
                value = row['value']
                digest = hashlib.sha256(canonical(value)).hexdigest()
            else:
                path = (root / row['artifact']).resolve()
                require(path.is_relative_to(root.resolve()) and path.is_file(),
                        'MissingArtifact', identifier, 'Expected a retained project file')
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                value = strict_json(path.read_text())
                try:
                    for part in row['pointer'].split('/')[1:]:
                        part = part.replace('~1', '/').replace('~0', '~')
                        value = value[int(part)] if isinstance(value, list) else value[part]
                except (KeyError, ValueError, IndexError, TypeError) as exc:
                    raise Invalid('MissingExport', identifier, row['pointer']) from exc
            require(digest == row['sha256'], 'StaleArtifact', identifier, 'Frozen export content differs')
            self.external[identifier] = row['kind']
            self.values[identifier] = value
        require(set(self.external) == set(expected), 'MissingExport', 'registry', 'Incomplete demonstration export set')

    def ref(self, identifier, kinds=None):
        kind = self.kinds.get(identifier, self.external.get(identifier))
        require(kind is not None, 'UnknownReference', identifier, 'No frozen export')
        require(kinds is None or kind in kinds, 'ReferenceKind', identifier, f'Expected {kinds}, got {kind}')
        return self.nodes.get(identifier, self.values.get(identifier))

    def refs(self, identifiers, kinds=None):
        require(len(identifiers) == len(set(identifiers)), 'DuplicateReference', str(identifiers), 'Set-valued reference list')
        return [self.ref(i, kinds) for i in identifiers]

    def time(self, t, where):
        start = iso_date(t['start'], where)
        self.ref(t['calendar'], {'Calendar'})
        if t['kind'] == 'instant':
            require(t['end_exclusive'] is None, 'InvalidPeriod', where, 'Instant has no end')
        else:
            require(t['end_exclusive'] is not None and iso_date(t['end_exclusive'], where) > start,
                    'InvalidPeriod', where, 'Interval must have a later exclusive end')

    def domain(self, d, where):
        low = rational(d['lower'], where) if d['lower'] is not None else None
        high = rational(d['upper'], where) if d['upper'] is not None else None
        require(low is not None or not d['lower_closed'], 'InvalidDomain', where, 'Unbounded endpoint cannot be closed')
        require(high is not None or not d['upper_closed'], 'InvalidDomain', where, 'Unbounded endpoint cannot be closed')
        if d['kind'] == 'missing':
            require(low is high is None and not d['values'] and d['missing_reason'] is not None,
                    'InvalidDomain', where, 'Missingness cannot contain a value')
        else:
            require(d['missing_reason'] is None, 'InvalidDomain', where, 'Nonmissing domain has no missing reason')
            if d['kind'] == 'finite':
                require(low is high is None and bool(d['values']), 'InvalidDomain', where, 'Finite domain needs values only')
                self.refs(d['values'], {'expressions'})
            else:
                require(not d['values'], 'InvalidDomain', where, 'Numeric interval has no finite-value payload')
                require(low is None or high is None or low < high or
                        (low == high and d['lower_closed'] and d['upper_closed']),
                        'InvalidDomain', where, 'Empty/reversed interval')
                if d['kind'] == 'exact':
                    require(low is not None and low == high and d['lower_closed'] and d['upper_closed'],
                            'InvalidDomain', where, 'Exact domain requires equal closed finite bounds')
        return low, high

    def merge_context(self, contexts, where):
        ids = [c for c in contexts if c is not None]
        if not ids:
            return None
        keys = ['entity', 'perimeter', 'basis', 'measurement', 'time', 'unit', 'currency', 'dimensions']
        first = self.ref(ids[0], {'contexts'})
        for identifier in ids[1:]:
            other = self.ref(identifier, {'contexts'})
            require(all(first[k] == other[k] for k in keys), 'ContextMismatch', where,
                    'Contexts require an explicit compatible mapping')
        return ids[0]

    def expression(self, identifier, active=()):
        require(identifier not in active, 'ExpressionCycle', identifier, 'Cyclic expression dependency')
        if identifier in self.inferred:
            return self.inferred[identifier]
        e = self.ref(identifier, {'expressions'})
        op, target = e['op'], e['target']
        args = [self.expression(a, active + (identifier,)) for a in e['args']]
        types = [t for t, _ in args]
        context = self.merge_context([c for _, c in args], identifier)
        numeric = lambda t: t in {'Real', 'Int', 'YearFraction', 'Rate<annual_simple>'} or re.fullmatch(r'Money<[A-Z]{3}>', t) is not None
        require(not e['field_names'], 'UnsupportedExpression', identifier, 'Records/field selection not in this profile')
        if op == 'literal':
            require(not args and target is None and ((e['rational'] is None) != (e['text'] is None)),
                    'ExpressionPayload', identifier, 'One literal payload and no operands/target')
            result = e['type']
            if e['rational'] is not None:
                q = rational(e['rational'], identifier)
                require(numeric(result), 'TypeMismatch', identifier, 'Numeric literal has a numeric type')
                require(result != 'Int' or q.denominator == 1, 'TypeMismatch', identifier, 'Fractional integer')
            elif result == 'SourceRef':
                self.ref(e['text'], {'SourceRef'})
            elif result == 'Date':
                iso_date(e['text'], identifier)
            else:
                require(result == 'String' or (result == 'Bool' and e['text'] in {'true', 'false'}),
                        'TypeMismatch', identifier, 'Invalid text literal type')
            context = e['context']
        else:
            require(e['rational'] is None and e['text'] is None, 'ExpressionPayload', identifier, 'Unused literal payload')
            if op == 'ref':
                require(not args, 'ArityMismatch', identifier, 'Reference takes no operands')
                r = self.ref(target, {'symbols', 'observations', 'expressions'})
                if self.kinds[target] == 'observations':
                    c = self.ref(r['context'], {'contexts'})
                    result, context = f'Observation<Money<{c["currency"]}>>', r['context']
                elif self.kinds[target] == 'symbols':
                    result, context = r['type'], r['context']
                else:
                    result, context = self.expression(target, active + (identifier,))
            elif op == 'call':
                self.ref(target, {'Builtin'})
                require(len(args) == 1, 'ArityMismatch', identifier, 'Supported calls take one argument')
                if target == 'builtin:value@1':
                    require(types[0].startswith('Observation<') and types[0].endswith('>'),
                            'TypeMismatch', identifier, 'value requires an Observation')
                    result = types[0][12:-1]
                elif target == 'builtin:constant@1':
                    result = f'Driver<{types[0]}>'
                else:
                    raise Invalid('UnsupportedExpression', identifier, 'Builtin not implemented in this checker')
            else:
                require(target is None, 'ExpressionPayload', identifier, 'Operator cannot have target')
                arity = 1 if op in {'negate', 'not'} else 2
                require(len(args) == arity, 'ArityMismatch', identifier, 'Wrong operator argument count')
                if op in {'not', 'and', 'or'}:
                    require(all(t == 'Bool' for t in types), 'TypeMismatch', identifier, 'Boolean operands required')
                    result = 'Bool'
                elif op in {'eq', 'ne', 'lt', 'le', 'gt', 'ge', 'add', 'subtract'}:
                    require(types[0] == types[1] and (op in {'eq', 'ne'} or numeric(types[0])),
                            'TypeMismatch', identifier, 'Compatible operand types required')
                    result = types[0] if op in {'add', 'subtract'} else 'Bool'
                elif op == 'negate':
                    require(numeric(types[0]), 'TypeMismatch', identifier, 'Numeric negation required')
                    result = types[0]
                else:
                    raise Invalid('UnsupportedExpression', identifier, op)
        if context is not None:
            c = self.ref(context, {'contexts'})
            m = re.fullmatch(r'Money<([A-Z]{3})>', result)
            require(not m or c['currency'] == m[1], 'ContextMismatch', identifier, 'Money/context currency mismatch')
        require((result, context) == (e['type'], e['context']), 'TypeMismatch', identifier,
                f'Declared {(e["type"], e["context"])} but inferred {(result, context)}')
        self.inferred[identifier] = result, context
        return result, context

    def bounds(self, identifier):
        e = self.ref(identifier, {'expressions'})
        if e['op'] == 'literal' and e['rational'] is not None:
            q = rational(e['rational'], identifier)
            return q, q
        if e['op'] == 'ref' and self.kinds.get(e['target']) in {'observations', 'symbols'}:
            return self.domain(self.nodes[e['target']]['domain'], identifier)
        if e['op'] == 'call' and e['target'] in {'builtin:value@1', 'builtin:constant@1'}:
            return self.bounds(e['args'][0])
        raise Invalid('UnprovedContractBound', identifier, 'Bound computation unsupported in this profile')

    def assumption(self, expression, scope):
        require(any(a['expression'] == expression and a['scope'] == scope for a in self.doc['assumptions']),
                'MissingAssumption', scope + ':' + expression, 'Conditional input lacks assumption provenance')

    def validate(self):
        d = self.doc
        reading = self.values['fixture:synthetic-note-7/exact-reading']
        package_data = self.values['fixture:demo-debt-package.json']
        horizon = self.values['DemoCalendar@1']['one_year']
        for key in ['models', 'contexts', 'documents', 'observations', 'entities', 'books', 'accounts',
                    'symbols', 'contracts', 'states', 'packages', 'scenarios', 'reviewDecisions',
                    'evidenceViews', 'modelScopes', 'historyFamilies', 'reportMappings']:
            require(bool(d[key]), 'IncompleteProfile', key, 'Required part of the authored debt example')
        for entity in d['entities']:
            require(re.fullmatch(r'[A-Z]{3}', entity['functional_currency']) is not None,
                    'InvalidCurrency', entity['id'], 'Three uppercase currency letters required')
        for c in d['contexts']:
            self.ref(c['entity'], {'entities'}); self.time(c['time'], c['id'])
            require(c['currency'] is not None and c['unit'] == c['currency'], 'ContextMismatch', c['id'], 'Monetary profile requires currency/unit agreement')
            require(len({x['axis'] for x in c['dimensions']}) == len(c['dimensions']), 'DuplicateDimension', c['id'], 'One member per axis')
            require(not c['dimensions'] and c['taxonomy_version'] is None, 'UnsupportedContext', c['id'],
                    'Taxonomy and dimensional mappings are outside this profile')
        for doc in d['documents']:
            instant(doc['available'], doc['id']); instant(doc['ingested'], doc['id'])
            require(doc['uri'] == 'fixture:demo-debt-package.json#registry/synthetic-note-7', 'UnsupportedSource', doc['id'], 'Only frozen synthetic source is handled')
            literal = self.values['fixture:synthetic-note-7/exact-reading']['literal']
            require(doc['sha256'] == hashlib.sha256(literal.encode()).hexdigest(), 'SourceDigestMismatch', doc['id'], 'Synthetic document hashes its literal bytes')
        for s in d['sourceSpans']:
            self.ref(s['document'], {'documents'})
            require(s['literal'] == self.values['fixture:synthetic-note-7/exact-reading']['literal'], 'SourceLiteralMismatch', s['id'], 'Source span differs from frozen reading')
            require(s['locator'] == 'fixture:registry/synthetic-note-7/literal' and s['extraction'].strip(),
                    'SourceLocatorMismatch', s['id'], 'Locator and extractor must identify the retained literal')
        for review in d['reviewDecisions']:
            self.refs(review['reading_ids'], {'Reading'}); self.refs(review['evidence'], {'sourceSpans'})
            self.ref(review['prior_view'], {'EvidenceView', 'evidenceViews'}); self.ref(review['new_view'], {'evidenceViews'})
            instant(review['date'], review['id'])
            require(review['reviewer'].strip() and review['reason'].strip(), 'MissingReviewReason', review['id'], 'Reviewer and rationale required')
            require(review['action'] == 'Accept' and not review['invalidated_descendants'],
                    'UnsupportedReview', review['id'], 'This profile checks initial acceptance, not revision transitions')
        for o in d['observations']:
            self.ref(o['context'], {'contexts'}); self.domain(o['domain'], o['id'])
            self.refs(o['source_spans'], {'sourceSpans'}); self.ref(o['reading'], {'Reading'})
            r = self.ref(o['review_decision'], {'reviewDecisions'})
            require(r['action'] == 'Accept' and o['reading'] in r['reading_ids'], 'ObservationNotAccepted', o['id'], 'This profile requires accepted, matching readings')
            require(not o['supersedes'], 'UnsupportedHistory', o['id'], 'Revision graph checked separately, not in this profile')
            require(bool(o['source_spans']) and set(o['source_spans']) <= set(r['evidence']),
                    'AdmissionEvidence', o['id'], 'Acceptance must retain the observation source')
            c = self.ref(o['context'], {'contexts'})
            require(all(c[k] == reading[k] for k in ['entity', 'perimeter', 'basis', 'concept', 'currency'])
                    and c['time']['kind'] == 'instant' and c['time']['start'] == reading['instant']
                    and c['measurement'] == 'principal', 'ReadingContextMismatch', o['id'],
                    'Admitted context differs from the frozen authored reading')
            require(o['domain']['kind'] == 'exact' and self.domain(o['domain'], o['id']) ==
                    (rational(reading['amount'], o['id']),) * 2, 'ReadingValueMismatch', o['id'],
                    'Admitted value differs from the frozen authored reading')
        for v in d['evidenceViews']:
            require(v['mode'] == 'ExplicitSelection' and not v['conflict_sets'] and not v['transforms'], 'UnsupportedView', v['id'], 'Only explicit nonconflicting fixture views')
            docs = self.refs(v['documents'], {'documents'}); self.refs(v['decisions'], {'reviewDecisions'})
            cutoff = instant(v['cutoff'], v['id'])
            system_cutoff = instant(v['system_as_of'], v['id']) if v['system_as_of'] is not None else None
            for review in self.refs(v['decisions'], {'reviewDecisions'}):
                require(review['new_view'] == v['id'], 'ViewMembership', review['id'], 'Decision must produce the selected view')
                require(system_cutoff is None or instant(review['date'], review['id']) <= system_cutoff,
                        'FutureReview', review['id'], 'Decision did not yet exist at the system cutoff')
            for doc in docs:
                require(instant(doc['available'], doc['id']) <= cutoff, 'FutureEvidence', doc['id'], 'Source unavailable at cutoff')
                if v['system_as_of'] is not None:
                    require(instant(doc['ingested'], doc['id']) <= instant(v['system_as_of'], v['id']), 'FutureIngestion', doc['id'], 'Source not yet in database')
            for o in self.refs(v['observations'], {'observations'}):
                require(o['review_decision'] in v['decisions'], 'ViewMembership', o['id'], 'Acceptance decision omitted from view')
                for span in self.refs(o['source_spans'], {'sourceSpans'}):
                    require(span['document'] in v['documents'], 'ViewMembership', span['id'], 'Observation source omitted from view')
        for book in d['books']:
            entity = self.ref(book['entity'], {'entities'}); package = self.ref(book['package'], {'packages'})
            require(book['currency'] == entity['functional_currency'], 'BookCurrency', book['id'], 'Declared functional currency differs')
            require(book['basis'] == package['id'], 'PackageBasis', book['id'], 'Demo book uses its dated package ID')
        for a in d['accounts']:
            self.ref(a['book'], {'books'})
            expected = {'Cash': ('Asset', 'cash'), 'Debt': ('Liability', 'debt'),
                        'InterestExpense': ('Expense', 'interest'), 'Retained': ('Equity', 'retained')}
            require(a['id'] in expected and (a['role'], a['report_concept']) == expected[a['id']],
                    'AccountMapping', a['id'], 'Account differs from the frozen statement-template role')
        for s in d['symbols']:
            self.domain(s['domain'], s['id']); self.ref(s['scope'], {'models', 'modelScopes'})
            self.refs(s['dependencies']); self.refs(s['provenance'], {'sourceSpans'})
            r = self.ref(s['admission'], {'reviewDecisions'})
            require(s['uncertainty_kind'] == 'HistoricalFact' and r['action'] == 'Accept', 'UnsupportedAdmission', s['id'], 'This profile handles an admitted factual unknown')
            require(s['id'] == 'alpha' and s['type'] == 'Real' and s['context'] is None and not s['dependencies'],
                    'UnsupportedSymbol', s['id'], 'Only the independent real fixed-rate fraction is supported')
            require(s['domain']['kind'] == 'interval' and self.domain(s['domain'], s['id']) == (0, 1)
                    and s['domain']['lower_closed'] and s['domain']['upper_closed'],
                    'AdmissionDomain', s['id'], 'Frozen admission specifies the full closed fraction interval')
            require(bool(s['provenance']) and set(s['provenance']) <= set(r['evidence']),
                    'AdmissionEvidence', s['id'], 'Unknown admission needs retained evidence')
        for e in d['expressions']:
            self.expression(e['id'])
        for a in d['assumptions']:
            self.expression(a['expression']); self.ref(a['scope'], {'alternatives', 'models', 'scenarios', 'contracts'})
            self.time(a['valid'], a['id']); instant(a['information_cutoff'], a['id']); self.refs(a['source_refs'])
            require(bool(a['rationale'].strip()), 'MissingAssumptionReason', a['id'], 'Rationale required')
            require(a['role'] != 'ReviewedDefault', 'UnprovedDefaultReview', a['id'], 'No reviewed-default evidence in this profile')
            require(a['valid']['kind'] == 'interval' and a['valid']['start'] <= horizon[0]
                    and a['valid']['end_exclusive'] >= horizon[1], 'AssumptionValidity', a['id'],
                    'Example assumptions must cover the full named scenario period')
            require(all(instant(a['information_cutoff'], a['id']) <= instant(v['cutoff'], v['id'])
                        for v in d['evidenceViews']), 'FutureAssumption', a['id'],
                    'Assumption information cutoff exceeds the example evidence view')
        for c in d['constraints']:
            require(self.expression(c['expression'])[0] == 'Bool', 'ConstraintType', c['id'], 'Constraint must be Boolean')
            self.ref(c['scope']); self.refs(c['source_refs'])
            if c['kind'] == 'assumption':
                self.assumption(c['expression'], c['scope'])
            else:
                raise Invalid('UnsupportedConstraint', c['id'], 'Only named assumption constraints in this profile')
        for a in d['alternatives']:
            self.ref(a['parent'], {'historyFamilies'}); self.ref(a['scope'], {'modelScopes'})
            self.refs(a['constraints'], {'constraints'}); self.refs(a['evidence'], {'sourceSpans'}); self.refs(a['opposing_evidence'], {'sourceSpans'})
            require(a['choice_group'] is None, 'UnsupportedChoice', a['id'], 'Named conditional views only')
            require(a['author'].strip() and a['reason'].strip(), 'MissingAlternativeReason', a['id'], 'Author and reason required')
            instant(a['created_at'], a['id'])
            require(bool(a['constraints']) and all(self.nodes[c]['scope'] == a['id'] for c in a['constraints']),
                    'AlternativeScope', a['id'], 'Alternative constraints must belong to that alternative')
            require(self.nodes[a['parent']]['scope'] == a['scope'], 'AlternativeScope', a['id'], 'Family and alternative scope differ')
        for p in d['packages']:
            path = self.root / 'docs/design/fixtures/demo-debt-package.json'
            require(p['id'] == 'DemoDebt@1' and p['version'] == '1', 'UnsupportedPackage', p['id'], 'Debt profile only')
            require(hashlib.sha256(path.read_bytes()).hexdigest() == p['digest'], 'PackageDigestMismatch', p['id'], 'Package lock differs from bytes')
            self.time(p['effective'], p['id']); self.refs(p['operations'], {'Operation'})
            self.refs(p['dependencies'], {'Library', 'Calendar'}); self.refs(p['authority'], {'SourceRef'})
            require(p['review_status'] == 'illustrative', 'UnprovedDomainReview', p['id'], 'No domain-review evidence supplied')
            require(p['basis'] == 'DemoDebt' and p['implementation'] is None and not p['extension_points'],
                    'UnsupportedPackage', p['id'], 'No executable package or overrides validated here')
            require(set(p['operations']) == {'DemoDebt@1/' + n for n in ['reset', 'accrue_and_pay', 'close', 'statements']},
                    'PackageOperations', p['id'], 'All demonstration operations required')
            require(p['effective']['kind'] == 'interval' and p['effective']['start'] <= horizon[0]
                    and p['effective']['end_exclusive'] >= horizon[1], 'PackageValidity', p['id'], 'Package must apply over the scenario period')
        for c in d['contracts']:
            self.ref(c['type'], {'ContractType'}); book = self.ref(c['book'], {'books'})
            require(c['package'] == book['package'], 'PackageBasis', c['id'], 'Contract and book package differ')
            self.refs(c['source_refs'], {'sourceSpans'})
            fields = {f['name']: f['expression'] for f in c['fields']}
            required = {'principal': f'Money<{book["currency"]}>', 'fixed_fraction': 'Real', 'fixed_rate': 'Rate<annual_simple>', 'initial_floating_rate': 'Rate<annual_simple>'}
            require(len(fields) == len(c['fields']) and fields.keys() == required.keys(), 'ContractFields', c['id'], 'Wrong or repeated contract fields')
            for name, expected in required.items():
                require(self.expression(fields[name])[0] == expected, 'ContractType', c['id'] + '.' + name, expected)
                context = self.expression(fields[name])[1]
                if context is not None:
                    ctx = self.nodes[context]
                    require(ctx['entity'] == book['entity'] and ctx['basis'] == book['basis'],
                            'ContractContext', c['id'], 'Contract input belongs to another entity or basis')
                low, high = self.bounds(fields[name])
                require(low is not None and low >= 0 and (name != 'fixed_fraction' or (high is not None and high <= 1)), 'ContractDomain', name, 'Nonnegative amounts/rates and share in [0,1] required')
                if name in {'fixed_rate', 'initial_floating_rate'}:
                    self.assumption(fields[name], c['id'])
        for s in d['states']:
            self.ref(s['book'], {'books'}); iso_date(s['date'], s['id'])
            seen = set(); total = Fraction(0)
            for b in s['balances']:
                a = self.ref(b['account'], {'accounts'})
                require(a['book'] == s['book'], 'StateBook', s['id'], 'Balance belongs to another book')
                require(a['id'] not in seen, 'DuplicateBalance', s['id'], a['id']); seen.add(a['id'])
                total += rational(b['signed_amount'], s['id'])
            require(total == 0, 'UnbalancedState', s['id'], 'Signed opening balances must sum to zero')
            require(seen == {a['id'] for a in d['accounts'] if a['book'] == s['book']}, 'IncompleteState', s['id'], 'This fixture requires explicit zero balances too')
            self.refs(s['contracts'], {'contracts'}); self.refs(s['dependencies'])
            require(not s['measurements'], 'UnsupportedState', s['id'], 'Measurement state not validated in this profile')
            require(all(self.nodes[c]['book'] == s['book'] for c in s['contracts']),
                    'StateBook', s['id'], 'Active contract belongs to another book')
            opening = package_data['registry']['after-2025-close']
            require(s['book'] == opening['book'] and s['date'] == opening['date'] and
                    set(s['contracts']) == set(opening['contracts']) and
                    {b['account']: rational(b['signed_amount'], s['id']) for b in s['balances']} ==
                    {a: Fraction(v) for a, v in opening['signed_balances'].items()},
                    'OpeningStateMismatch', s['id'], 'Balanced state differs from the frozen authored opening')
        for s in d['scenarios']:
            require(s['kind'] == 'ExogenousStress' and s['probability_model'] is None and s['observed_event'] is None and s['structural_model'] is None and not s['replaced_equations'], 'UnsupportedScenario', s['id'], 'Exogenous debt stress only')
            require(len(s['drivers']) == 1 and s['drivers'][0]['name'] == 'market_rate', 'ScenarioDrivers', s['id'], 'Expected market_rate')
            require(self.expression(s['drivers'][0]['expression'])[0] == 'Driver<Rate<annual_simple>>', 'TypeMismatch', s['id'], 'Rate driver required')
            self.assumption(s['drivers'][0]['expression'], s['id'])
            low, _ = self.bounds(s['drivers'][0]['expression'])
            require(low is not None and low >= 0, 'ContractDomain', s['id'], 'DemoDebt rejects a negative reset rate')
        for scope in d['modelScopes']:
            self.refs(scope['templates'], {'ContractType'}); self.refs(scope['calendars'], {'Calendar'})
            require(not scope['choices'] and not scope['obligations'], 'UnsupportedScope', scope['id'], 'Additional structural choices/obligations need a fuller checker')
            require(len(scope['slot_limits']) == 1, 'SlotLimit', scope['id'], 'One concrete debt slot limit required')
            for slot in scope['slot_limits']:
                require(self.expression(slot['expression'])[0] == 'Int', 'SlotLimitType', scope['id'], 'Slot limit is an integer, not an implicit Real cast')
                low, high = self.bounds(slot['expression'])
                require(low == high and low is not None and low >= 0 and slot['name'] == 'debt_contracts' and len(d['contracts']) <= low, 'SlotLimit', scope['id'], 'Concrete nonnegative capacity required')
        for f in d['historyFamilies']:
            for key, kind in [('scope', 'modelScopes'), ('evidence_view', 'evidenceViews'), ('opening_state', 'states')]:
                self.ref(f[key], {kind})
            for key, kind in [('symbols', 'symbols'), ('constraints', 'constraints'), ('alternatives', 'alternatives')]:
                self.refs(f[key], {kind})
            self.refs(f['witnesses'], {'Witness'}); self.refs(f['solver_results'], {'ReferenceResult'})
            view = self.nodes[f['evidence_view']]
            require(all(o['id'] in view['observations'] for o in d['observations']) and
                    all(s['admission'] in view['decisions'] for s in d['symbols']),
                    'ViewMembership', f['id'], 'All evidence used by this bounded family must be selected')
            require(set(f['symbols']) == {s['id'] for s in d['symbols']} and
                    set(f['alternatives']) == {a['id'] for a in d['alternatives'] if a['parent'] == f['id']},
                    'FamilyMembership', f['id'], 'Family omits an authored symbol or conditional alternative')
            require(not f['choices'], 'UnsupportedChoice', f['id'], 'Finite structural cells not implemented here')
            require(f['coverage'] != 'ExactWithinScope' or f['unresolved_cells'] == 0, 'FalseCoverage', f['id'], 'Exact coverage cannot contain unknown cells')
            require(f['coverage'] != 'ExactWithinScope' or (f['completed_cells'] > 0 and f['solver_results']),
                    'FalseCoverage', f['id'], 'Exact label needs completed cells and result references; this is not proof verification')
            require(f['feasibility'] != 'Feasible' or bool(f['witnesses']), 'MissingWitness', f['id'], 'Feasible label requires a witness reference')
        for r in d['reportMappings']:
            b = self.ref(r['book'], {'books'})
            require(r['basis'] == b['basis'], 'PackageBasis', r['id'], 'Report and book bases differ')
            self.ref(r['closing_policy'], {'Operation'}); self.ref(r['cash_flow_policy'], {'CashFlowPolicy'})
            self.refs(r['required_operations'], {'Operation'})
            require(r['closing_policy'] == 'DemoDebt@1/close' and r['cash_flow_policy'] == 'DemoDebt@1/interest_operating'
                    and r['required_operations'] == ['DemoDebt@1/accrue_and_pay'], 'ReportPolicy', r['id'],
                    'Wrong policy binding for the frozen report template')
            require(len(r['rows']) == 1 and r['rows'][0]['name'] == 'package_mapping', 'ReportMappingType', r['id'], 'One frozen template binding required')
            for row in r['rows']:
                require(self.expression(row['expression'])[0] == 'SourceRef', 'ReportMappingType', r['id'], 'This profile binds a frozen report template')
                e = self.nodes[row['expression']]
                require(e['op'] == 'literal' and e['text'] == 'DemoDebt.statements.v1', 'ReportMappingType', r['id'], 'Expected the statement mapping export')
        for m in d['models']:
            self.refs(m['declarations']); self.refs(m['package_lock'], {'packages'}); self.ref(m['scope'], {'modelScopes'})
            require(m['language_version'] == 'Core0.1', 'UnsupportedLanguage', m['id'], 'Core0.1 only')
            required = {r['id'] for section in ['entities', 'books', 'accounts', 'observations', 'symbols',
                        'contracts', 'alternatives', 'scenarios', 'reportMappings', 'states'] for r in d[section]}
            require(required <= set(m['declarations']) and set(m['package_lock']) == {p['id'] for p in d['packages']},
                    'ModelMembership', m['id'], 'Model omits an authored declaration or package lock')
        return {'status': 'passed', 'profile': 'authored-debt-example',
                'internal_records': len(self.nodes), 'external_exports': len(self.external),
                'coverage_claims_verified': False,
                'limits': 'Bounded static admission only; no general compiler, runtime, accounting certification or proof of historical coverage.'}


def validate(document, registry, schema, root):
    return Validator(document, registry, schema, root).validate()
