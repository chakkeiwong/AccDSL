"""Direct ordered eligibility source; the protected gate owns all semantics."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'ordered-event-eligibility-20261026'))
import gate
import method_requirement_text_v2 as rules

core = gate.core
PROFILE = 'OrderedEligibilityText/1'
j = rules.prior.json_token


class Invalid(ValueError):
    def __init__(self, reason, location=None):
        self.reason = str(reason)[:350]
        self.location = location
        super().__init__(self.reason)


def need(ok, reason, location=None):
    if not ok:
        raise Invalid(reason, location)


def span(source, start, end, line, granularity):
    raw = source.encode('utf-8')
    return dict(line=line, byte_start=start, byte_end=end, granularity=granularity,
                slice_sha256=sha256(raw[start:end]).hexdigest())


def source_rows(source):
    need(type(source) is str, 'source_type')
    try:
        raw = source.encode('utf-8')
    except UnicodeEncodeError as exc:
        raise Invalid('source_utf8') from exc
    need(len(raw) <= core.MAX_BYTES, 'source_size_limit')
    rows, offset, count = [], 0, 0
    pieces = source.split('\n')
    for number, piece in enumerate(pieces, 1):
        raw_line = piece + ('\n' if number < len(pieces) else '')
        line = raw_line[:-2] if raw_line.endswith('\r\n') else raw_line[:-1] if raw_line.endswith('\n') else raw_line
        for index, char in enumerate(line):
            if char == '\ufeff' or ord(char) < 32 and char != '\t' or ord(char) == 127:
                start = offset + len(line[:index].encode())
                raise Invalid('source_control', span(source, start, start+len(char.encode()), number, 'token'))
        location = span(source, offset, offset+len(line.encode()), number, 'declaration')
        rows.append((line, location))
        offset += len(raw_line.encode())
        count += bool(line.strip())
        need(count <= core.MAX_NODES, 'declaration_limit', location)
    return rows


def located_tokens(source, line, location):
    """Use the original lexical rules/decoder and retain each token's offsets."""
    items, positions, pos = [], [], 0
    def loc(start, end):
        return span(source, location['byte_start']+len(line[:start].encode()),
                    location['byte_start']+len(line[:end].encode()), location['line'], 'token')
    while pos < len(line):
        char = line[pos]
        if char in ' \t':
            pos += 1
            continue
        start = pos
        try:
            if char in '();':
                item = (char, char); pos += 1
            elif char in '"[{' or char in '-0123456789':
                value, pos = rules.prior.DECODER.raw_decode(line, pos)
                item = ('value', value)
            else:
                match = re.match(r'[A-Za-z_][A-Za-z0-9_]*', line[pos:])
                need(match is not None, 'unexpected_token', loc(pos, pos+1))
                value = match.group(0); pos += len(value)
                item = ('value', {'true': True, 'false': False, 'null': None}[value]) if value in ('true', 'false', 'null') else ('word', value)
        except Exception as exc:
            position = getattr(exc, 'pos', start)
            reason = getattr(exc, 'reason', str(exc))
            error_location = location if str(reason).startswith(('duplicate_json_key:', 'nonfinite_json:')) else loc(position, min(position+1, len(line)))
            raise Invalid(reason, getattr(exc, 'location', None) or error_location) from exc
        items.append(item); positions.append(loc(start, pos))
        need(len(items) <= core.MAX_NODES*12, 'token_limit', positions[-1])
    need(items == rules.prior.tokens(line), 'tokenizer_disagreement', location)
    return items, positions, loc(len(line), len(line))


class Reader(rules.Reader):
    def __init__(self, source, line, location):
        items, self.locations, self.eof = located_tokens(source, line, location)
        super().__init__(items)
        self.binding_nodes = 0

    def location(self, index=None):
        index = self.pos if index is None else index
        return self.locations[index] if index < len(self.locations) else self.eof

    def take(self, kind, exact=None):
        try:
            return super().take(kind, exact)
        except Exception as exc:
            raise Invalid(getattr(exc, 'reason', str(exc)), self.location()) from exc

    def string(self):
        index = self.pos
        try:
            return super().string()
        except Invalid:
            raise
        except Exception as exc:
            raise Invalid(getattr(exc, 'reason', str(exc)), self.location(index)) from exc

    def expression(self, depth=0):
        index = self.pos
        try:
            return super().expression(depth)
        except Invalid:
            raise
        except Exception as exc:
            reason = getattr(exc, 'reason', str(exc))
            raise Invalid(reason, self.location(index+1 if str(reason).startswith('unknown_operator:') else index)) from exc

    def finish(self):
        self.take(';')
        need(self.pos == len(self.items), 'trailing_tokens', self.location())

    def binding(self, depth=0):
        self.binding_nodes += 1
        need(depth <= core.MAX_DEPTH and self.binding_nodes <= core.MAX_NODES, 'binding_limit', self.location())
        self.take('('); index = self.pos; kind = self.take('word')
        result = {'kind': kind}
        fields = {'event_input': ['name'], 'event_metadata': ['field'],
                  'book_date': [], 'period_end': [], 'memory_leaf': ['pointer'],
                  'map_contains': ['pointer', 'key_input'],
                  'map_field': ['pointer', 'key_input', 'field', 'after_stage']}
        if kind in fields:
            for name in fields[kind]:
                result[name] = self.string()
        elif kind == 'calendar_adjacent':
            result.update(left=self.binding(depth+1), right=self.binding(depth+1))
        else:
            raise Invalid('unsupported_source_kind:'+kind, self.location(index))
        self.take(')')
        return result


def lower(source):
    location = None
    try:
        rows = source_rows(source)
        template = None; state = 'header'; current = None; manifest = None
        spans = []; stage_spans = []; fields = {}; ids = set()
        def unique(obj, key, value):
            need(key not in obj, 'duplicate_declaration:'+key, location)
            obj[key] = value
        for line, location in rows:
            if not line.strip():
                continue
            spans.append(location); need(state != 'done', 'declaration_after_end', location)
            r = Reader(source, line, location); word = r.take('word')
            if state == 'header':
                need(word == 'ordered_eligibility' and r.string() == PROFILE, 'source_profile', location)
                template = dict(profile=r.string(), operation=r.string(), input_types={}, stages=[], residuals=[])
                need(template['profile'] == gate.PROFILE, 'eligibility_profile', location)
                fields['header'] = location; state = 'body'
            elif state == 'body':
                if word == 'context':
                    unique(template, 'context', r.take('value')); fields['context'] = location
                elif word == 'full_input':
                    key = r.string(); unique(template['input_types'], key, r.take('value')); fields['input:'+key] = location
                elif word == 'residual':
                    template['residuals'].append(r.string())
                elif word == 'stage':
                    name, reason = r.string(), r.string()
                    need(name not in ids, 'duplicate_stage', location); ids.add(name)
                    need(len(ids) <= 64, 'stage_limit', location)
                    current = dict(id=name, reason=reason, bindings={})
                    template['stages'].append(current); stage_start = location; state = 'stage'
                else:
                    need(word == 'end_eligibility', 'unknown_declaration:'+word, r.location(0))
                    need('context' in template and template['input_types'] and template['stages'], 'incomplete_template', location)
                    state = 'done'
            elif state == 'stage':
                if word == 'bind':
                    unique(current['bindings'], r.string(), r.binding())
                elif word == 'begin_rules':
                    need('manifest' not in current, 'duplicate_rules', location)
                    manifest = dict(profile=r.string(), method_id=r.string(), version=r.string(), inputs={},
                                    requirements=[], required_known=[], capabilities=[], residual_prerequisites=[])
                    need(manifest['profile'] == 'MethodRequirements/3', 'explicit_guard_profile', location)
                    known_seen = False; state = 'rules'
                else:
                    need(word == 'end_stage', 'stage_declaration:'+word, r.location(0))
                    need('manifest' in current, 'stage_rules_required', location)
                    stage_spans.append(span(source, stage_start['byte_start'], location['byte_end'], stage_start['line'], 'stage'))
                    current = None; state = 'body'
            elif state == 'rules':
                if word == 'input':
                    key = r.string()
                    unique(manifest['inputs'], key, dict(type=r.take('value'), role=r.take('word'), source_ref=r.string()))
                elif word == 'guarded':
                    manifest['requirements'].append(dict(id=r.string(), on_false=r.take('word'), on_unknown=r.take('word'),
                        guard_requires=r.take('value'), requires=r.take('value'), admission_refs=r.take('value'),
                        guard=r.expression(), predicate=r.expression()))
                elif word == 'required_known':
                    need(not known_seen, 'duplicate_required_known', location)
                    manifest['required_known'] = r.take('value'); known_seen = True
                elif word in ('capability', 'residual'):
                    manifest['capabilities' if word == 'capability' else 'residual_prerequisites'].append(r.string())
                else:
                    need(word == 'end_rules', 'rules_declaration:'+word, r.location(0))
                    need(known_seen, 'explicit_required_known_declaration', location)
                    current['manifest'] = manifest; manifest = None; state = 'stage'
            r.finish()
        eof = span(source, len(source.encode()), len(source.encode()), source.count('\n')+1, 'token')
        need(state == 'done', 'incomplete_source:'+state, eof)
        return dict(profile=PROFILE, status='lowered_structural', template=template,
                    template_sha256=core.digest(template), source_sha256=sha256(source.encode()).hexdigest(),
                    source_spans=spans, stage_spans=stage_spans, field_spans=fields,
                    executed=False, source_admission=False, accounting_admission=False)
    except Exception as exc:
        if isinstance(exc, Invalid):
            raise
        raise Invalid(getattr(exc, 'reason', str(exc)), location) from exc


def compile_text(source, book, definition):
    lowered = lower(source); template = lowered['template']
    header = deepcopy(template); header['stages'] = []
    try:
        gate.compile_template(header, book, definition)
    except Exception as exc:
        reason = getattr(exc, 'reason', str(exc))
        if reason != 'stage_limit':
            loc = lowered['field_spans']['context'] if reason == 'context_mismatch' else span(source, 0, len(source.encode()), 1, 'document')
            raise Invalid(reason, loc) from exc
    for index in range(len(template['stages'])):
        prefix = deepcopy(template); prefix['stages'] = prefix['stages'][:index+1]
        try:
            gate.compile_template(prefix, book, definition)
        except Exception as exc:
            reason = getattr(exc, 'reason', str(exc))
            loc = lowered['stage_spans'][index]
            raise Invalid(reason, loc) from exc
    gate.compile_template(template, book, definition)
    return dict(lowered, status='compiled_structural', state_sha256=core.digest(book), definition_sha256=core.digest(definition))


def assess_source(source, book, event, schemas, definition, call):
    lowered = compile_text(source, book, definition)
    return gate.assess(lowered['template'], book, event, schemas, definition, call)


def render_binding(value):
    kind = value['kind']
    fields = {'event_input': ['name'], 'event_metadata': ['field'], 'book_date': [],
              'period_end': [], 'memory_leaf': ['pointer'],
              'map_contains': ['pointer', 'key_input'],
              'map_field': ['pointer', 'key_input', 'field', 'after_stage']}
    args = [render_binding(value[k]) for k in ('left', 'right')] if kind == 'calendar_adjacent' else [j(value[k]) for k in fields[kind]]
    return '('+' '.join([kind]+args)+')'


def render(template):
    rows = []
    def add(word, *values):
        rows.append(word+' '+' '.join(j(x) for x in values)+';')
    add('ordered_eligibility', PROFILE, template['profile'], template['operation'])
    add('context', template['context'])
    for name, typ in template['input_types'].items():
        add('full_input', name, typ)
    for residual in template['residuals']:
        add('residual', residual)
    for stage in template['stages']:
        add('stage', stage['id'], stage['reason'])
        for name, binding in stage['bindings'].items():
            rows.append('bind '+j(name)+' '+render_binding(binding)+';')
        d = stage['manifest']
        add('begin_rules', d['profile'], d['method_id'], d['version'])
        exchange = dict(profile=rules.EXCHANGE, definition=d, selected_digest=core.digest(d), values={}, available_capabilities=[])
        rows.extend(rules.render(exchange).splitlines()[1:-2])
        rows.extend(['end_rules;', 'end_stage;'])
    rows.append('end_eligibility;')
    source = '\n'.join(rows)+'\n'
    need(core.canonical(lower(source)['template']) == core.canonical(template), 'render_roundtrip')
    return source
