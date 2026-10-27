"""Bounded static source inventory; never imports acquired code or expands DTDs."""
import ast
import hashlib
import itertools
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / 'data/accounting-master'
P = B / 'r06-textblock-policy-20261020'
PIN = '01f6a4656c2c6551d2f05f31c9d74366d133ee7e'
COMMAND = B / 'taxonomy-reuse-20261007/sources/arelle-cntlrcmdline-trusted.body'
CONTROLLER = B / 'taxonomy-reuse-20261007/sources/arelle-cntlr-trusted.body'
DISCLOSURE = B / 'native-loader-source-20261018/sources/DisclosureSystem.py'
VALIDATOR = P / 'sources/ValidateFilingText-sandbox.body'

def load(p):
    return json.loads(p.read_text())

def bind(p):
    return {'path': str(p.relative_to(R)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

def source(name):
    return U / 'sources' / (name + '-sandbox.body')

def uncomment(s):
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    assert '<!--' not in s and '-->' not in s, 'unclosed comment'
    return s

def entities(text):
    """Recognize only these files' simple internal declarations; fail on residue."""
    s = uncomment(text)
    pattern = re.compile(r'\s*<!ENTITY\s+([A-Za-z][A-Za-z0-9]*)\s+([\x22\x27])(.*?)\2\s*>', re.S)
    pos = 0
    out = {}
    while s[pos:].strip():
        match = pattern.match(s, pos)
        assert match, 'unsupported declaration or residue'
        name, _, value = match.groups()
        assert name not in out, 'duplicate entity'
        assert re.fullmatch(r'&#[0-9]+;(?:#[0-9]+;)?', value), 'unsupported replacement literal'
        out[name] = value
        pos = match.end()
    return out

def no_dtd_xml(path):
    text = path.read_text()
    assert '<!DOCTYPE' not in text and '<!ENTITY' not in uncomment(text)
    return ET.fromstring(text)

def function(path, name):
    tree = ast.parse(path.read_text())
    return next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)

def entity_inventory():
    rows = []
    combined = {}
    for name in ('xhtml-lat1', 'xhtml-symbol', 'xhtml-special'):
        values = entities(source(name).read_text())
        assert not (combined.keys() & values.keys())
        combined.update(values)
        rows.append({'file': name + '.ent', 'declarations': values,
                     'count': len(values), 'external_dependencies': []})
    node = next(n for n in ast.parse(VALIDATOR.read_text()).body
                if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'xhtmlEntities' for t in n.targets))
    literal = ast.literal_eval(node.value)
    expected = {'&' + name + ';': value for name, value in combined.items()}
    difference = {
        'whitelist_only': {k: literal[k] for k in sorted(literal.keys() - expected.keys())},
        'declaration_only': {k: expected[k] for k in sorted(expected.keys() - literal.keys())},
        'different_values': {k: [literal[k], expected[k]] for k in sorted(literal.keys() & expected.keys())
                             if literal[k] != expected[k]},
    }
    assert combined['amp'] == '&#38;#38;' and combined['lt'] == '&#38;#60;'
    dependencies = []
    pattern = re.compile(r'<!ENTITY\s+%\s+([A-Za-z0-9_]+)\s+PUBLIC\s+"([^"]+)"\s+"([^"]+)"\s*>', re.S)
    for name in ('edbody.dtd', 'xhtml1-strict-ix.dtd'):
        text = uncomment((P / 'sources' / (name + '-sandbox.body')).read_text())
        hits = pattern.findall(text)
        assert len(re.findall(r'\b(?:SYSTEM|PUBLIC)\b', text)) == len(hits) == 3
        assert {h[2] for h in hits} == {r['file'] for r in rows}
        dependencies.extend({'from': name, 'parameter': a, 'public_id': b, 'system_id': c} for a, b, c in hits)
    return {'files': rows, 'unique_entities': len(combined), 'whitelist_equal': literal == expected,
            'whitelist_difference': difference,
            'external_edges': dependencies, 'entity_expansion': 'not_executed',
            'closure_scope': 'two DTDs external entity declarations and the three retained simple entity files only'}

def caller_inventory():
    findings = []
    def require(test, name):
        assert test, name
        findings.append(name)
    manager = ast.unparse(function(source('ModelManager'), 'validate'))
    require('Validate.validate(self.modelXbrl)' in manager, 'manager_dispatches_Validate')
    dispatch = source('Validate').read_text()
    require('self.instValidator = ValidateXbrl.ValidateXbrl(modelXbrl)' in dispatch, 'dispatch_uses_ValidateXbrl')
    require('self.instValidator.validate(self.modelXbrl,' in dispatch, 'dispatch_invokes_instance_validator')
    core = source('ValidateXbrl').read_text()
    for hook in ('Validate.XBRL.Start', 'Validate.XBRL.Finally'):
        require('plugins.hooks("' + hook + '")' in core, hook)
    require('validateTextBlockFacts' not in core and 'validateTextBlockFacts' not in dispatch,
            'no_direct_named_call_in_two_inspected_dispatch_files')
    start = ast.unparse(function(source('FERC'), 'validateXbrlStart'))
    final = ast.unparse(function(source('FERC'), 'validateXbrlFinally'))
    require("val.validateDisclosureSystem and getattr(val.disclosureSystem, 'FERCplugin', False)" in start,
            'FERC_conjunctive_guard')
    require('if not val.validateFERCplugin:\n        return' in final, 'FERC_finally_early_return')
    require('if not modelDocument:\n        return' in final, 'FERC_requires_document')
    require('ValidateFilingText.validateTextBlockFacts(modelXbrl)' in final, 'FERC_actual_textblock_call')
    ferc = source('FERC').read_text()
    for fragment in ('"Validate.XBRL.Start": validateXbrlStart', '"Validate.XBRL.Finally": validateXbrlFinally',
                     '"DisclosureSystem.Types": disclosureSystemTypes', '"DisclosureSystem.ConfigURL": disclosureSystemConfigURL'):
        require(fragment in ferc, 'FERC_registration_' + fragment.split(':')[0])
    require('return (("FERC", "FERCplugin"),)' in ferc, 'FERC_type_registration')
    require('"config.xml"' in ast.unparse(function(source('FERC'), 'disclosureSystemConfigURL')).replace("'", '"'),
            'FERC_config_reference')
    command = COMMAND.read_text()
    require('self.modelManager.disclosureSystem.select("efm")' in command, 'command_selects_named_efm')
    require('self.modelManager.validateDisclosureSystem = False' in command, 'command_has_disabled_branch')
    base = no_dtd_xml(source('disclosuresystems'))
    active = [dict(e.attrib) for e in base.iter('DisclosureSystem')]
    require(not active, 'base_configuration_has_no_active_DisclosureSystem_elements')
    require('efm-strict' in source('disclosuresystems').read_text(), 'legacy_efm_text_is_present_but_commented')
    config = [dict(e.attrib) for e in no_dtd_xml(source('FERC-config')).iter('DisclosureSystem')]
    require(len(config) == 2 and all(x['validationType'] == 'FERC' for x in config), 'two_active_FERC_profiles')
    require(all('allowedExternalHrefPattern' not in x for x in config), 'FERC_no_explicit_external_href_pattern')
    require(all(json.loads(x['allowedImageTypes'])['img-file-extensions'] == [] for x in config),
            'FERC_image_file_extensions_empty')
    disclosure = DISCLOSURE.read_text()
    for fragment in ('self.allowedExternalHrefPattern = None', 'self.allowedImageTypes = None',
                     'self.validationType == typeName', 'if allowedImageTypes := dsElt.get("allowedImageTypes")'):
        require(fragment in disclosure, 'disclosure_' + fragment)
    loader = ast.unparse(function(VALIDATOR, 'loadDTD'))
    require('modelXbrl.modelDocument.type == ModelDocumentTypeINLINEXBRL' in loader,
            'DTD_loader_tests_single_inline_type_only')
    require('ModelDocumentType.INLINEXBRLDOCUMENTSET' in final, 'FERC_finally_treats_IXDS_as_inline')
    require('if isInlineDTD is None or isInlineDTD != _isInline:' in loader,
            'DTD_cache_guard_is_inline_type_only')
    model_document = source('ModelDocument').read_text()
    require('from arelle.ModelDocumentType import ModelDocumentType as _Type\nType = _Type' in model_document,
            'legacy_Type_is_ModelDocumentType_alias')
    type_class = next(n for n in ast.parse(source('ModelDocumentType').read_text()).body
                      if isinstance(n, ast.ClassDef) and n.name == 'ModelDocumentType')
    wanted = ('INSTANCE', 'INLINEXBRL', 'INLINEXBRLDOCUMENTSET')
    values = {n.target.id: ast.literal_eval(n.value) for n in type_class.body
              if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.target.id in wanted}
    require(values == {'INSTANCE': 4, 'INLINEXBRL': 5, 'INLINEXBRLDOCUMENTSET': 7},
            'document_type_constants_are_distinct')
    truth = [{'disclosure_validation': d, 'FERC_flag': f, 'document_present': m,
              'necessary_guard_pass': d and f and m}
             for d, f, m in itertools.product((False, True), repeat=3)]
    selection = [{'document_type': t, 'type_value': values[t],
                  'FERC_inline_branch': values[t] in (values['INLINEXBRL'], values['INLINEXBRLDOCUMENTSET']),
                  'textblock_inline_DTD': values[t] == values['INLINEXBRL']}
                 for t in ('INSTANCE', 'INLINEXBRL', 'INLINEXBRLDOCUMENTSET')]
    return {'findings': findings, 'active_base_profiles': active, 'FERC_profiles': config,
            'necessary_guard_truth_table': truth, 'document_type_selection': selection,
            'actual_filing_profile': 'not_selected_or_executed',
            'FERC_plugin_dependencies': ['inlineXbrlDocumentSet', 'configuration schema and UTR sources'],
            'call_graph_scope': 'one demonstrated profile caller; not a repository-wide caller search'}

def identities():
    tree = load(source('tree'))
    assert tree['sha'] == PIN and tree['truncated'] is False
    entries = {r['path']: r for r in tree['tree']}
    pairs = [(source(n), 'arelle/config/' + n + '.ent') for n in ('xhtml-lat1', 'xhtml-symbol', 'xhtml-special')]
    pairs += [(source(n), 'arelle/' + n + '.py') for n in
              ('ValidateXbrl', 'ModelManager', 'Validate', 'ModelDocument', 'ModelDocumentType')]
    pairs += [(source('FERC'), 'arelle/plugin/validate/FERC/__init__.py'),
              (source('FERC-config'), 'arelle/plugin/validate/FERC/config.xml'),
              (source('disclosuresystems'), 'arelle/config/disclosuresystems.xml'),
              (VALIDATOR, 'arelle/ValidateFilingText.py'), (COMMAND, 'arelle/CntlrCmdLine.py'),
              (CONTROLLER, 'arelle/Cntlr.py'), (DISCLOSURE, 'arelle/DisclosureSystem.py')]
    pairs += [(P / 'sources' / (n + '-sandbox.body'), 'arelle/config/' + n)
              for n in ('edbody.dtd', 'xhtml1-strict-ix.dtd')]
    out = []
    for path, name in pairs:
        raw = path.read_bytes()
        git_blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert entries[name]['sha'] == git_blob and entries[name]['size'] == len(raw), name
        out.append({'local': bind(path), 'git_path': name, 'git_blob': git_blob, 'bytes': len(raw)})
    return {'commit': PIN, 'tree_entries': len(entries), 'verified_blobs': out}

def fixtures():
    assert entities('<!-- <!ENTITY % ignored SYSTEM "remote"> --><!ENTITY amp "&#38;#38;">') == {'amp': '&#38;#38;'}
    assert entities('<!ENTITY a "&#65;">\n<!ENTITY b \'&#66;\'>') == {'a': '&#65;', 'b': '&#66;'}
    bad = ['<!ENTITY x SYSTEM "remote">', '<!ENTITY % x "&#65;">',
           '<!ENTITY x "&#65;"><!ENTITY x "&#65;">', '<!ENTITY x "&unknown;">',
           '<!ENTITY x "&#65;">unparsed', '<!-- unclosed', '<!ENTITY x "&#65;"',
           '<![INCLUDE[<!ENTITY x "&#65;">]]>']
    for text in bad:
        try:
            entities(text)
        except AssertionError:
            pass
        else:
            raise AssertionError('fixture should fail: ' + text)
    return {'positive': 2, 'rejected': len(bad)}

def retained_name_occurrences():
    """Literal membership diagnostic only; no entity or fragment evaluation."""
    path = B / 'r06-textblock-fragments-20261020/occurrences.json'
    rows = load(path)
    assert len(rows) == 56
    names = ('&there;', '&there4;')
    return {'source': bind(path), 'fragments': len(rows),
            'names': {name: [{'fact_id': r['fact_id'], 'literal_count': r['decoded_text'].count(name)}
                             for r in rows if name in r['decoded_text']]
                      for name in names},
            'interpretation': 'literal search in frozen decoded strings only; no runtime or display-impact inference'}

def derive():
    return {'entities': entity_inventory(), 'caller': caller_inventory(), 'identities': identities(),
            'fixtures': fixtures(), 'retained_name_occurrences': retained_name_occurrences(),
            'runtime_admitted': False, 'generic_validity': 'unadmitted'}

def check():
    ledger = load(U / 'source-ledger.json')
    count = 0
    for row in ledger['bindings']:
        assert bind(R / row['path']) == row
        count += 1
    for row in ledger['anchors']:
        p = R / row['source']['path']
        assert bind(p) == row['source']
        assert '\n'.join(p.read_text().splitlines()[row['first_line']-1:row['last_line']]) == row['excerpt']
        count += 2
    actual = derive()
    assert actual == load(U / 'dependencies.json')
    count += 1 + len(actual['caller']['findings']) + len(actual['identities']['verified_blobs'])
    receipts = sorted((U / 'sources').glob('*-receipt.json'))
    for p in receipts:
        row = load(p)
        final = row.get('final_result', row['result'])
        meta = json.loads(final['output'])
        assert final['exit_code'] == 0 and meta['http_code'] == 200
        assert (R / meta['filename_effective']).stat().st_size == meta['size_download']
        count += 2
    return {'checks': count, 'source_anchors': len(ledger['anchors']), 'input_bindings': len(ledger['bindings']),
            'acquisitions': len(receipts), 'source_findings': len(actual['caller']['findings']),
            'unique_entity_declarations': actual['entities']['unique_entities'], 'external_entity_edges': 6,
            'git_blobs_verified': len(actual['identities']['verified_blobs']),
            'guard_cases': 8, 'document_type_cases': 3, 'parser_fixtures': actual['fixtures'],
            'upstream_executed': False, 'DTD_expansion': 'not_run', 'whole_rows_closed': 0}
