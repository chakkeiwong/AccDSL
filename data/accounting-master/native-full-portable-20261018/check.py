"""Full pinned-source documentary correspondence; not an installed importer."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
import json
import platform
import subprocess
import time
import xml.etree.ElementTree as ET
from model import *
sys.path.insert(0, str(OUT))
from prepare import construct_packet, VALUE_REASON, INVENTORY

def validate(packet, records, adjunct, material, expected_packet, expected_records):
    checks = []
    def check(label, condition):
        require(condition, label); checks.append(label)
    check('EXACT_PACKET', packet == expected_packet)
    check('FULL_SELECTION', (len(packet['facts']), len(packet['contexts']), len(packet['units']), len(packet['source_links'])) == (1127,193,7,1))
    check('RECORD_COUNT', len(records) == 3788)
    declared, by_key, by_ref = profile(), {}, {}
    for record in records:
        key, kind = record['key'], record['kind']
        check('ENVELOPE:' + key, set(record) == set(declared['envelope_fields']))
        check('KEY:' + key, key not in by_key)
        check('SCHEMA:' + key, record['schema'] == declared['records'][kind]['schema'])
        check('REVISION:' + key, type(record['revision']) is int and record['revision'] == 0)
        typed(record['body'], declared['records'][kind]['body_type'], declared)
        check('TYPED:' + key, True)
        check('DEPENDENCIES:' + key, record['dependencies'] == ref_set(refs(record['body'])))
        by_key[key], by_ref[canonical(record_ref(record))] = record, record
    def body(key): return by_key[key]['body']
    reference_cache = {k: record_ref(r) for k,r in by_key.items()}
    def ref(key): return reference_cache[key]
    for record in records:
        for dependency in record['dependencies']:
            check('CLOSED:' + record['key'] + ':' + dependency['digest'][:8], canonical(dependency) in by_ref)
    raw, root, xml_ids, ns, locate = material
    check('SOURCE_BLOB', body('source')['original_bytes_ref'] == blob(ROOT / packet['source']['path']))
    check('PACKET_BLOB', body('import')['original_bytes_ref'] == blob(PACKET) and body('import')['original_bytes_ref'] != body('source')['original_bytes_ref'])
    check('NAMESPACE_EVIDENCE', body('source')['namespace_bindings'] == packet['namespace_bindings'])
    owners = {'source': ''}
    wrapper = '<root ' + ' '.join(('xmlns' + (':' + n['prefix'] if n['prefix'] else '') + '="' + n['namespace_uri'] + '"') for n in packet['namespace_bindings']) + '>'
    reader = reader_module()
    for group in ['contexts', 'units', 'facts']:
        for i, entry in enumerate(packet[group]):
            key, owner = entry['id'], '/' + group + '/' + str(i)
            owners['occ-' + key] = owner
            occ = body('occ-' + key)
            check('LOCATOR:' + key, occ['locator'] == locator(entry) and occ['source_ref'] == ref('source'))
            span = occ['locator']
            check('ORIGINAL_BYTES:' + key, sha(raw[span['byte_start']:span['byte_end']]) == entry['span']['slice_sha256'])
            if group == 'contexts':
                owners['source-' + key] = owner
                evidence = body('source-' + key)
                check('CONTEXT_REF:' + key, evidence['occurrence_ref'] == ref('occ-' + key))
                check('PERIOD:' + key, evidence['period'] == period(entry))
                check('DIMENSIONS:' + key, evidence['dimensions'] == dimensions(entry, packet))
                for j, dimension in enumerate(evidence['dimensions']):
                    ds = dimension['source_span']
                    check('DIMENSION_CONTAINMENT:' + key + ':' + str(j), span['byte_start'] <= ds['byte_start'] < ds['byte_end'] <= span['byte_end'])
                    parsed = ET.fromstring(wrapper.encode() + raw[ds['byte_start']:ds['byte_end']] + b'</root>')[0]
                    check('DIMENSION_SUBTREE:' + key + ':' + str(j), reader.tree_reading(parsed) == entry['dimensions_and_qualifiers'][j]['reading'])
            elif group == 'units':
                owners['source-' + key] = owner
                evidence = body('source-' + key)
                check('UNIT_REF:' + key, evidence['occurrence_ref'] == ref('occ-' + key))
                for side in ['numerator', 'denominator']:
                    check('UNIT_' + side.upper() + ':' + key, evidence[side] == [{'token': m['token'], 'qname': qname(m['expanded_name'])} for m in entry[side]])
            else:
                owners['ctx-' + key] = owners['fact-' + key] = owner
                assertion, context, element = body('fact-' + key), body('ctx-' + key), xml_ids[key]
                check('CHARACTERS:' + key, assertion['reported_text'] == (element.text or ''))
                check('ATTRIBUTES:' + key, assertion['source_attributes'] == [{'name': k, 'value': v} for k,v in sorted(element.attrib.items())])
                check('CONCEPT:' + key, assertion['concept'] == qname(element.tag))
                check('CONTEXT_JOIN:' + key, context['source_context_ref'] == ref('source-' + element.get('contextRef')))
                expected_unit = ref('source-' + element.get('unitRef')) if element.get('unitRef') else unknown('No unitRef; applicability/type not established')
                check('UNIT_JOIN:' + key, context['source_unit_ref'] == expected_unit)
                check('FACT_JOINS:' + key, assertion['occurrence_refs'] == [ref('occ-' + key)] and assertion['context_ref'] == ref('ctx-' + key))
                check('FINANCIAL_UNKNOWN:' + key, all(context[k]['tag'] == 'Unknown' for k in ['legal_entity','book','perimeter','basis','currency_or_unit','time','calendar','dimensions']))
                check('CANDIDATE:' + key, assertion['interpretation_status'] == context['interpretation_status'] == 'candidate' and entry['taxonomy_type'] == 'Unknown')
                for target, attr in [('context_id_token','contextRef'),('unit_id_token','unitRef'),('decimals','decimals'),('precision','precision'),('explicit_language',reader.XML+'lang')]:
                    check('RAW:' + key + ':' + target, assertion[target] == raw_field(element.attrib, attr))
                check('LANGUAGE_UNKNOWN:' + key, assertion['effective_language']['tag'] == 'Unknown')
                if element.get(reader.XS + 'nil') == 'true':
                    expected = {'tag':'Nil'}
                elif entry['lexical_class'] == 'decimal_lexical_candidate':
                    number = Fraction(element.text)
                    expected = {'tag':'Decimal','rational':{'n':str(number.numerator),'d':str(number.denominator)}} if element.get('unitRef') else unknown(VALUE_REASON)
                else: expected = {'tag':'Text','text':element.text}
                check('VALUE:' + key, assertion['value'] == expected)
    owners['occ-link-1'] = '/source_links/0'
    check('LINK_NULL_ID', body('occ-link-1')['locator']['element_id'] is None)
    check('LINK_ADJUNCT', adjunct == link_adjunct(packet, records))
    mapping = body('mapping')
    check('OUTPUT_MEMBERSHIP', mapping['outputs'] == ref_set([ref(k) for k in owners]))
    coverage = set()
    for item in mapping['field_mappings']:
        target = by_ref[canonical(item['target_ref'])]
        key, path = target['key'], item['target_path']
        check('FIELD:' + key + ':' + path, key in owners and path.startswith('/body/') and path.count('/') == 2 and path[6:] in target['body'])
        check('UNIQUE_MAPPING:' + key + ':' + path, (key,path) not in coverage)
        coverage.add((key,path)); owner = owners[key]
        check('OWNER:' + key + ':' + path, item['source_path'] == owner or item['source_path'].startswith(owner + '/'))
        value = pointer(packet, item['source_path'])
        if item['relation'] == 'equal_decoded_value':
            check('EQUALITY:' + key + ':' + path, value == pointer(target, path))
        else:
            is_text = target['kind'] == 'ReportedAssertion' and path == '/body/value' and pointer(packet, owner)['candidate_value']['tag'] == 'UnvalidatedText'
            check('CONVERSION:' + key + ':' + path, item['source_path'] == owner and item['conversion_method_ref'] == ref('method-text' if is_text else 'method-general'))
    check('TOTAL_COVERAGE', coverage == {(k,'/body/'+f) for k in owners for f in body(k)})
    for expected in expected_records:
        check('SPECIFICATION_RECORD:' + expected['key'], by_key[expected['key']] == expected)
    return checks

def mutate(records, key, edit):
    changed, replacements = [], {}
    def replace(value):
        if isinstance(value, dict):
            if set(value) == {'kind','schema','digest'}: return replacements.get(canonical(value),value)
            return {k:replace(v) for k,v in value.items()}
        return [replace(v) for v in value] if isinstance(value,list) else value
    for original in records:
        row = deepcopy(original)
        if row['key'] == key: edit(row)
        row['body'] = replace(row['body'])
        if row['key'] == 'mapping': row['body']['outputs'] = ref_set(row['body']['outputs'])
        if row['key'] == 'comparison':
            mapping = next(r['body'] for r in changed if r['key']=='mapping')
            row['body']['output_digests'] = sorted(r['digest'] for r in mapping['outputs'])
            row['body']['field_mapping_count'] = len(mapping['field_mappings'])
        row['dependencies'] = ref_set(refs(row['body']))
        replacements[canonical(record_ref(original))] = record_ref(row)
        changed.append(row)
    return changed

def negatives(packet,records,adjunct,material,expected_packet,expected_records):
    by_key = {r['key']:r for r in records}
    tests = [
        ('nil-as-zero','fact-f-192',lambda r:r['body'].__setitem__('value',{'tag':'Decimal','rational':{'n':'0','d':'1'}}),'VALUE:f-192'),
        ('unitless-identifier-numeric','fact-f-59',lambda r:r['body'].__setitem__('value',{'tag':'Decimal','rational':{'n':'320193','d':'1'}}),'VALUE:f-59'),
        ('leading-zeros-lost','fact-f-59',lambda r:r['body'].__setitem__('reported_text','320193'),'CHARACTERS:f-59'),
        ('typed-member-flattened','source-c-61',lambda r:r['body']['dimensions'][0].__setitem__('member_token','2027-09-26'),'DIMENSIONS:c-61'),
        ('unit-denominator-lost','source-usdPerShare',lambda r:r['body'].__setitem__('denominator',[]),'UNIT_DENOMINATOR:usdPerShare'),
        ('repeat-merged','fact-f-256',lambda r:r['body'].__setitem__('occurrence_refs',[record_ref(by_key['occ-f-207'])]),'FACT_JOINS:f-256'),
        ('eps-scaled','fact-f-105',lambda r:r['body'].__setitem__('value',{'tag':'Decimal','rational':{'n':'611','d':'1'}}),'VALUE:f-105'),
        ('financial-date-inferred','ctx-f-147',lambda r:r['body'].__setitem__('time',{'tag':'Instant','date':'2024-09-28'}),'FINANCIAL_UNKNOWN:f-147'),
        ('markup-truncated','fact-f-356',lambda r:r['body'].__setitem__('value',{'tag':'Text','text':'Inventory policy'}),'VALUE:f-356'),
        ('schema-source-id-invented','occ-link-1',lambda r:r['body']['locator'].__setitem__('element_id','schema'),'LINK_NULL_ID'),
        ('mapping-omitted','mapping',lambda r:r['body']['field_mappings'].pop(),'TOTAL_COVERAGE')]
    def text_method_lost(row):
        target = record_ref(by_key['fact-f-356'])
        item = next(m for m in row['body']['field_mappings'] if m['target_ref']==target and m['target_path']=='/body/value')
        item['conversion_method_ref'] = record_ref(by_key['method-general'])
    tests.append(('unvalidated-text-caveat-lost','mapping',text_method_lost,'CONVERSION:fact-f-356:/body/value'))
    results = []
    for name,key,edit,expected in tests:
        changed=mutate(records,key,edit)
        try: validate(packet,changed,link_adjunct(packet,changed),material,expected_packet,expected_records)
        except ValueError as error:
            require(str(error)==expected,'WRONG_NEGATIVE:'+name+':'+str(error))
            results.append({'case':name,'rejected':str(error),'dependent_refs_rebuilt':True})
        else: raise ValueError('ACCEPTED:'+name)
    return results

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--record',action='store_true'); mode.add_argument('--check-only',action='store_true')
    parser.add_argument('--positive-only',action='store_true')
    args=parser.parse_args(); tick=time.monotonic()
    require(not args.positive_only or args.check_only,'POSITIVE_ONLY_DEBUG')
    packet=read(PACKET); expected_packet=construct_packet(); material=reader_module().source_material()
    expected_records=construct(packet)
    records=expected_records if args.record or args.check_only else read(OUT/'portable-records.json')
    adjunct=link_adjunct(packet,records) if args.record or args.check_only else read(OUT/'source-link-adjunct.json')
    checks=validate(packet,records,adjunct,material,expected_packet,expected_records)
    corruptions=[] if args.positive_only else negatives(packet,records,adjunct,material,expected_packet,expected_records)
    counts={'facts':1127,'contexts':193,'units':7,'source_links':1,'records':len(records),
        'field_mappings':len(next(r for r in records if r['key']=='mapping')['body']['field_mappings']),
        'checks':len(checks),'rejected_corruptions':len(corruptions),
        'value_tags':dict(Counter(r['body']['value']['tag'] for r in records if r['kind']=='ReportedAssertion'))}
    findings={'counts':counts,'checks':checks,'negative_cases':corruptions,'upstream_executed':False,'profile_registered':False}
    if args.record:
        for name in ['portable-records.json','source-link-adjunct.json','checks.json','run-manifest.json']:
            require(not (OUT/name).exists(),'ALREADY_RECORDED:'+name)
        write_once(OUT/'portable-records.json',records); write_once(OUT/'source-link-adjunct.json',adjunct); write_once(OUT/'checks.json',findings)
        predecessor=ROOT/'data/accounting-master/native-hazard-portable-20261018'
        inherited=json.loads((predecessor/'run-manifest.json').read_bytes())['protected_inputs']
        protected=inherited+[binding(p) for p in [PLAN,SPEC,INVENTORY,predecessor/'checks.json',predecessor/'completion.json',predecessor/'run-manifest.json']]
        manifest={'recorded_utc':datetime.now(timezone.utc).isoformat(),
            'command':'timeout 300 python3 data/accounting-master/native-full-portable-20261018/check.py --record',
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'environment':{'executable':sys.executable,'python':platform.python_version(),'conda_env':'tfgpu','cpu_gpu':'CPU standard-library source checks only; no numerical framework/GPU'},
            'data_version':binding(INVENTORY),'random_seeds':'N/A: deterministic','wall_seconds':time.monotonic()-tick,
            'plan_file':str(PLAN.relative_to(ROOT)),'result_file':str((OUT/'result.md').relative_to(ROOT)),
            'protected_inputs':protected,'artifacts':[binding(OUT/n) for n in ['model.py','prepare.py','check.py','native-packet.json','portable-records.json','source-link-adjunct.json','checks.json']]}
        write_once(OUT/'run-manifest.json',manifest)
    elif not args.check_only:
        require(findings==read(OUT/'checks.json'),'REPLAY_CHANGED')
        manifest=json.loads((OUT/'run-manifest.json').read_bytes())
        for row in manifest['protected_inputs']+manifest['artifacts']:
            require(binding(ROOT/row['path'])==row,'PROTECTED:'+row['path'])
    print(json.dumps({'mode':'debug_positive_only' if args.positive_only else 'check_only' if args.check_only else 'record' if args.record else 'read_only_replay',**counts,'status':'pass'}))

if __name__=='__main__':main()
