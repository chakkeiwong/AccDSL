"""Versioned receivable commands over the frozen declared-command grammar."""
from copy import deepcopy
import declared_company_text_v2 as syntax
import declared_receivable_lifecycle_v1 as lifecycle

PROFILE = 'DeclaredReceivableText/1'
CONFIG = 'DeclaredReceivableImports/1'
core = lifecycle.core
FIELDS = ['profile', 'memory_definition', 'roles', 'unit_cost_pointer', 'policy']


def translate_header(source, before, after):
    # Rewrite only the exact versioned header; never rewrite quoted user data.
    lines = source.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.strip():
            prefix = 'company_program ' + syntax.token(before)
            core.need(line.startswith(prefix + ' '), 'text_profile_header')
            lines[i] = 'company_program ' + syntax.token(after) + line[len(prefix):]
            return ''.join(lines)
    raise core.Invalid('empty_program')


def from_program(body):
    lifecycle.validate(body)
    config = {k: deepcopy(body[k]) for k in FIELDS if k != 'profile'}; config['profile'] = CONFIG
    objects = {'opening': body['opening'], 'schemas': body['schemas'], 'registry': config, 'mapping': body['mapping']}
    imports = {core.digest(v): deepcopy(v) for v in objects.values()}
    commands = deepcopy(body['commands'])
    for command in commands:
        if command['kind'] == 'event':
            for record in command['event']['inputs'].values(): record.pop('type')
        elif command['kind'] == 'carry': command['memory_policies'] = {}
    author = {'profile': syntax.PROFILE, 'name': body['name'],
              'imports': {k: core.digest(v) for k, v in objects.items()}, 'commands': commands}
    source = translate_header(syntax.render(author), syntax.PROFILE, PROFILE)
    return source, imports


def compile_text(source, imports):
    try:
        syntax.protected(); lifecycle.protected()
        author = syntax.lower(translate_header(source, PROFILE, syntax.PROFILE))
        core.need(type(imports) is dict and set(imports) == set(author['imports'].values()), 'exact_import_population')
        resolved = {}
        for name, key in author['imports'].items():
            value = imports[key]; lifecycle.engine.memory.bounded(value)
            core.need(core.digest(value) == key, 'import_digest_mismatch'); resolved[name] = deepcopy(value)
        config = resolved['registry']; lifecycle.engine.closed(config, FIELDS)
        core.need(config['profile'] == CONFIG, 'configuration_profile')
        commands = deepcopy(author['commands'])
        for command in commands:
            if command['kind'] == 'event':
                types = lifecycle.event_types(resolved['opening'], command['method_key'])
                core.need(set(command['event']['inputs']) == set(types), 'exact_event_inputs')
                for name, record in command['event']['inputs'].items(): record['type'] = deepcopy(types[name])
            elif command['kind'] == 'carry':
                core.need(command.pop('memory_policies') == {}, 'carry_policy_from_explicit_import')
        body = {'profile': lifecycle.PROFILE, 'name': author['name'], 'commands': commands,
                **{k: resolved[k] for k in ['opening', 'schemas', 'mapping']},
                **{k: config[k] for k in FIELDS if k != 'profile'}}
        lifecycle.validate(body)
        return {'profile': PROFILE, 'status': 'compiled', 'program': body, 'source_sha256': core.digest(source)}
    except Exception as exc: return {'profile': PROFILE, 'status': 'invalid', 'reason': str(exc)[:350]}


def execute_text(source, imports):
    compiled = compile_text(source, imports)
    return lifecycle.run(compiled['program']) if compiled['status'] == 'compiled' else compiled
