"""Explicit selected-condition projections; residual full-method checks remain open."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
import method_requirements_v1 as core


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ref(key):
    return {'op':'ref', 'id':key}


def binary(op, left, right):
    return {'op':op, 'left':left, 'right':right}


class Builder:
    def __init__(self, method_id, body, source):
        self.body = body
        self.source = source
        self.values = {}
        self.spec = {'profile':core.PROFILE, 'method_id':method_id, 'version':'1',
                     'inputs':{}, 'requirements':[], 'capabilities':[method_id],
                     'residual_prerequisites':[
                         'Original profile schema, source hash and source binding.',
                         'Unselected state, account, temporal, event and allocation conditions.',
                         'Accounting authority and source admission assessed separately.',
                         'Full method execution, reporting and state transition verification.']}

    def field(self, path, kind, context, role='state'):
        key = '/'.join(path)
        value = self.body
        for part in path:
            value = value[part]
        self.spec['inputs'][key] = {'type':{'kind':kind, 'context':context},
                                    'role':role, 'source_ref':self.source+'#/'+key}
        self.values[key] = ({'status':'unknown', 'reason':'legacy_explicit_unknown'}
                            if value == 'unknown' else {'status':'known', 'value':value})
        return ref(key)

    def constant(self, expression, value):
        t = self.spec['inputs'][expression['id']]['type']
        return {'op':'const', 'type':deepcopy(t), 'value':value}

    def require(self, key, predicate, on_false='invalid', admission_refs=None):
        _, refs = core.expression(predicate, self.spec['inputs'])
        self.spec['requirements'].append({'id':key,'predicate':predicate,'requires':sorted(refs),
            'admission_refs':admission_refs or [], 'on_false':on_false, 'on_unknown':'unresolved'})

    def finish(self):
        core.validate_manifest(self.spec)
        return self.spec, self.values


def operations_requirements(body):
    b = Builder('company.operations.selected', body,
                'data/accounting-master/company-operations-20261023/example.json')
    ratio = {'unit':'ratio','scope':'declared_method_parameter'}
    for path in [('tax','rate'),('debt','floating_share')]:
        x = b.field(path,'rational',ratio,'assumption')
        b.require('/'.join(path)+'.lower',binary('le',b.constant(x,'0/1'),x))
        b.require('/'.join(path)+'.upper',binary('le',x,b.constant(x,'1/1')))
    for path, unit, value in [(('debt','coupon_years'),'years','1/1'),
                               (('facility','drawn'),'currency','0/1'),
                               (('loan','fee'),'currency','0/1')]:
        context = {'unit':unit,'book_role':'legal','scope':'selected_case'}
        x = b.field(path,'rational',context)
        b.require('/'.join(path)+'.nonnegative',binary('le',b.constant(x,'0/1'),x))
        b.require('/'.join(path)+'.scope',binary('eq',x,b.constant(x,value)),'unsupported')
    for path, expected in [(('inventory','method'),'homogeneous_cost'),
                           (('depreciation_method',),'straight_line_full_year'),
                           (('loan','day_count'),'ACT365_calendar'),
                           (('loan','interest_cash_class'),'operating'),
                           (('tax','method'),'immediate_deductible')]:
        x = b.field(path,'text',{'meaning':'method_selection'},'assumption')
        b.require('/'.join(path),binary('eq',x,b.constant(x,expected)),'unsupported')
    b.spec['residual_prerequisites'].append(
        'Legacy global-unknown short circuit differs from this all-findings summary on mixed inputs.')
    return b.finish()


def return_requirements(body, findings):
    b = Builder('company.returns.selected', body,
                'data/accounting-master/company-return-schema-20261023/retained_fixture.py')
    rate = b.field(('tax','rate'),'rational',{'unit':'ratio'},'assumption')
    b.require('rate.nonnegative',binary('le',b.constant(rate,'0/1'),rate))
    b.require('rate.at_most_one',binary('le',rate,b.constant(rate,'1/1')))
    units = {'unit':'inventory_units','entity':body['context']['entity'],
             'component':body['component']['id']}
    sold = b.field(('component','sold_units'),'rational',units)
    expected = b.field(('component','expected_units'),'rational',units,'assumption')
    for name, value in [('sold',sold),('expected',expected)]:
        b.require(name+'.nonnegative',binary('le',b.constant(value,'0/1'),value))
    b.require('returns.within_sales',binary('le',expected,sold))
    for key in findings:
        p = b.field(('tax',key),'boolean',{},'caller_finding')
        b.require('finding.'+key,p,'unsupported',['caller-review:tax/'+key])
    for key in ['refund_tax_base','recovery_tax_base']:
        p = b.field(('tax',key),'rational',{'currency':body['context']['currency'],
                                        'entity':body['context']['entity'],'book_role':'legal'})
        b.require(key+'.nonnegative',binary('le',b.constant(p,'0/1'),p))
        b.require(key+'.selected_zero_base',binary('eq',p,b.constant(p,'0/1')),'unsupported')
    return b.finish()


def compare():
    native = HERE.parent/'company-operations-20261023'
    operations = load('method_requirement_legacy_operations',native/'operations.py')
    body = json.loads((native/'example.json').read_text())
    source = (ROOT/body['source']['path']).read_bytes()
    returns = HERE.parent/'company-return-schema-20261023'
    sys.path.insert(0,str(returns))
    import return_schema
    import retained_fixture
    returned, raw = retained_fixture.fixture()
    observations, examples = [], {}

    def trial(label, base, build, legacy, edits, expected, full_pass):
        value = deepcopy(base)
        for path, replacement in edits:
            target = value
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = replacement
        before = deepcopy(value)
        spec, inputs = build(value)
        key = core.digest(spec)
        answer = core.assess({key:spec},key,inputs,spec['capabilities'])
        old = legacy(value)
        mapped = 'requirements_satisfied' if old['status']==full_pass else old['status']
        observations.append({'case':label,'expected':expected,'legacy_status':old['status'],
            'selected_status':answer['status'],'matched':mapped==answer['status']==expected,
            'input_unchanged':value==before,'result':answer})
        if not edits:
            examples[label] = {'manifest':spec,'values':inputs,'selected_digest':key}

    op_cases = [('baseline',[],'requirements_satisfied'),
        ('tax_over_one',[(('tax','rate'),'2/1')],'invalid'),
        ('negative_tax',[(('tax','rate'),'-1/10')],'invalid'),
        ('unknown_tax',[(('tax','rate'),'unknown')],'unresolved'),
        ('floating_over_one',[(('debt','floating_share'),'2/1')],'invalid'),
        ('unknown_floating',[(('debt','floating_share'),'unknown')],'unresolved'),
        ('nonannual_coupon',[(('debt','coupon_years'),'1/2')],'unsupported'),
        ('unknown_coupon',[(('debt','coupon_years'),'unknown')],'unresolved'),
        ('nonzero_fee',[(('loan','fee'),'1/1')],'unsupported'),
        ('unknown_fee',[(('loan','fee'),'unknown')],'unresolved')]
    for path in [('inventory','method'),('depreciation_method',),('loan','day_count'),
                 ('loan','interest_cash_class'),('tax','method')]:
        op_cases.append(('/'.join(path),[(path,'other_method')],'unsupported'))
    for label,edits,expected in op_cases:
        trial('operations.'+label,body,operations_requirements,
              lambda b:operations.validate(b,source),edits,expected,'validated')

    ret_cases = [('baseline',[],'requirements_satisfied'),
        ('tax_over_one',[(('tax','rate'),'2/1')],'invalid'),
        ('unknown_tax',[(('tax','rate'),'unknown')],'unresolved'),
        ('excess_returns',[(('component','expected_units'),'100/1')],'invalid'),
        ('unknown_expected',[(('component','expected_units'),'unknown')],'unresolved'),
        ('unknown_sold',[(('component','sold_units'),'unknown')],'unresolved'),
        ('tax_basis',[(('tax','refund_tax_base'),'1/1')],'unsupported'),
        ('false_and_unknown',[(('tax','rate'),'unknown'),(('tax','recovery_supported'),False)],'unsupported'),
        ('invalid_and_unknown',[(('tax','rate'),'unknown'),(('component','expected_units'),'100/1')],'invalid'),
        ('invalid_and_false',[(('tax','rate'),'2/1'),(('tax','recovery_supported'),False)],'invalid')]
    for key in return_schema.FINDINGS:
        ret_cases.extend([(key+'.false',[(('tax',key),False)],'unsupported'),
                          (key+'.unknown',[(('tax',key),'unknown')],'unresolved')])
    for label,edits,expected in ret_cases:
        trial('returns.'+label,returned,lambda b:return_requirements(b,return_schema.FINDINGS),
              return_schema.assess,edits,expected,'statically_eligible')

    # A deliberately mixed case exposes a real pre-existing precedence difference.
    mixed = deepcopy(body)
    mixed['tax']['rate'] = 'unknown'
    mixed['debt']['floating_share'] = '2/1'
    spec,values = operations_requirements(mixed)
    key = core.digest(spec)
    difference = {'case':'operations.unknown_tax_and_invalid_floating',
        'legacy_status':operations.validate(mixed,source)['status'],
        'selected_status':core.assess({key:spec},key,values,spec['capabilities'])['status'],
        'meaning':'Legacy early unknown masks a later contradiction; new selected assessment retains both.',
        'legacy_unchanged':True,'global_equivalence_claim':False}
    dependencies = {Path(module.__file__).resolve() for module in list(sys.modules.values())
                    if getattr(module,'__file__',None) and
                    Path(module.__file__).resolve().is_relative_to(ROOT)}
    dependencies |= {native/'operations.py',native/'example.json',ROOT/body['source']['path'],
                     retained_fixture.PACKET,retained_fixture.PACKET.with_name('validation-01.json')}
    return observations, examples, difference, sorted(dependencies)
