"""Independent dimensional rules and protected v1 lowering comparisons."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import method_requirements_v1 as old
import method_requirements_v2 as new
import core0_ir_v1 as core0

CONTEXT={'entity':'Sample','book_role':'legal','at':'2025-01-01'}


def rational(dimensions=None,scale='1/1',context=None):
    return {'kind':'rational','context':deepcopy(CONTEXT if context is None else context),
            'dimensions':dimensions or {},'scale':scale}


def ref(key):
    return {'op':'ref','id':key}


def op(name,a,b):
    return {'op':name,'left':a,'right':b}


def constant(value,t):
    return {'op':'const','type':deepcopy(t),'value':value}


def known(value):
    return {'status':'known','value':value}


def manifest(types,predicate):
    return {'profile':new.PROFILE,'method_id':'independent.products','version':'2',
        'inputs':{key:{'type':deepcopy(t),'role':'assumption','source_ref':'constructed:'+key}
                  for key,t in types.items()},
        'requirements':[{'id':'equation','predicate':predicate,'requires':sorted(types),
                         'admission_refs':[],'on_false':'invalid','on_unknown':'unresolved'}],
        'capabilities':['products'],'residual_prerequisites':['Full method and source admission remain separate.']}


def run(spec,values,caps=None):
    h=old.digest(spec)
    return new.assess({h:spec},h,values,['products'] if caps is None else caps)


class DimensionalTests(unittest.TestCase):
    def test_units_times_price(self):
        units=rational({'goods:unit':1})
        price=rational({'currency:USD':1,'goods:unit':-1})
        cash=rational({'currency:USD':1})
        spec=manifest({'units':units,'price':price,'cash':cash},op('eq',ref('cash'),op('mul',ref('units'),ref('price'))))
        result=run(spec,{'units':known('2/1'),'price':known('20/1'),'cash':known('40/1')})
        self.assertEqual(result['status'],'requirements_satisfied')
        product=next(iter(result['products'].values()))
        self.assertEqual(product['type'],cash)
        self.assertEqual(product['binding'],known('40/1'))
        self.assertEqual(result['findings'][0]['dependencies'],['cash','price','units'])

    def test_rate_times_amount_and_signed_values(self):
        cash=rational({'currency:USD':1})
        spec=manifest({'amount':cash,'rate':rational()},
            op('eq',op('mul',ref('amount'),ref('rate')),constant('-5/2',cash)))
        result=run(spec,{'amount':known('-10/1'),'rate':known('1/4')})
        self.assertEqual(result['status'],'requirements_satisfied')

    def test_dimensions_scales_and_context_are_checked(self):
        usd=rational({'currency:USD':1})
        bad=[rational({'currency:EUR':1}),rational({'currency:USD':2}),
             rational({'currency:USD':1},'1000000/1'),
             rational({'currency:USD':1},context={**CONTEXT,'book_role':'consolidated'}),
             rational({'currency:USD':1},context={**CONTEXT,'entity':'Other'}),
             rational({'currency:USD':1},context={**CONTEXT,'at':'2025-12-31'})]
        for t in bad:
            result=run(manifest({'a':usd,'b':t},op('eq',ref('a'),ref('b'))),
                       {'a':known('1/1'),'b':known('1/1')})
            self.assertEqual(result['status'],'invalid')
        spec=manifest({'a':usd,'b':usd},op('eq',op('mul',ref('a'),ref('b')),constant('1/1',usd)))
        self.assertEqual(run(spec,{'a':known('1/1'),'b':known('1/1')})['status'],'invalid')

    def test_scale_product_and_dimension_cancellation(self):
        count=rational({'goods:unit':1},'1000/1')
        price=rational({'currency:USD':1,'goods:unit':-1},'1/100')
        expected=rational({'currency:USD':1},'10/1')
        self.assertEqual(new.product_type(count,price),expected)
        spec=manifest({'a':count,'b':price},op('eq',op('mul',ref('a'),ref('b')),constant('6/1',expected)))
        self.assertEqual(run(spec,{'a':known('2/1'),'b':known('3/1')})['status'],'requirements_satisfied')

    def test_unknown_times_zero_and_repeated_identity(self):
        t=rational()
        for expression in [op('mul',ref('x'),constant('0/1',t)),op('mul',ref('x'),ref('x'))]:
            spec=manifest({'x':t},op('eq',expression,constant('0/1',t)))
            result=run(spec,{'x':{'status':'unknown','reason':'not observed'}})
            self.assertEqual(result['status'],'unresolved')
            self.assertEqual(result['findings'][0]['dependencies'],['x'])
            self.assertEqual(result['findings'][0]['unresolved_inputs'],{'x':'not observed'})
            self.assertNotIn('@product/',str(result['findings']))
        result=run(manifest({'x':t},op('eq',op('mul',ref('x'),ref('x')),constant('0/1',t))),{})
        self.assertEqual(result['findings'][0]['unresolved_inputs'],{'x':'missing_input'})

    def test_nested_products_and_decisive_boolean_dependencies(self):
        t=rational()
        p=op('mul',ref('x'),op('mul',ref('x'),ref('y')))
        spec=manifest({'x':t,'y':t},op('eq',p,constant('12/1',t)))
        result=run(spec,{'x':known('2/1'),'y':known('3/1')})
        self.assertEqual(result['status'],'requirements_satisfied')
        self.assertEqual(len(result['products']),2)
        spec['requirements'][0]['predicate']={'op':'any','args':[constant(True,old.BOOL),spec['requirements'][0]['predicate']]}
        result=run(spec,{'x':known('2/1'),'y':{'status':'unknown','reason':'not supplied'}})
        self.assertEqual(result['status'],'requirements_satisfied')
        self.assertEqual(result['findings'][0]['unresolved_inputs'],{'y':'not supplied'})

    def test_exact_known_coefficient_comparator(self):
        # Core 0 is used only for known scalar arithmetic, not dimensional admission.
        for a,b in [('2/1','20/1'),('1/3','7/4'),('-5/2','4/7'),('0/1','11/1')]:
            expected=Fraction(a)*Fraction(b)
            ir={'expressions':[
                {'id':'a','op':'literal','rational':core0.rational(a),'type':'Real','text':None},
                {'id':'b','op':'literal','rational':core0.rational(b),'type':'Real','text':None},
                {'id':'p','op':'multiply','args':['a','b']}]}
            self.assertEqual(core0.evaluate_expression(ir,'p'),expected)
            t=rational()
            spec=manifest({'a':t,'b':t},op('eq',op('mul',ref('a'),ref('b')),
                  constant(f'{expected.numerator}/{expected.denominator}',t)))
            self.assertEqual(run(spec,{'a':known(a),'b':known(b)})['status'],'requirements_satisfied')

    def test_no_product_matches_v1_semantics(self):
        t=rational({'currency:USD':1})
        spec=manifest({'a':t},op('le',ref('a'),constant('10/1',t)))
        lowered,products,_=new.compile_manifest(spec)
        self.assertEqual(products,{})
        for value in [known('9/1'),known('11/1'),{'status':'unknown','reason':'missing'}]:
            result=run(spec,{'a':value})
            h=old.digest(lowered)
            expected=old.assess({h:lowered},h,{'a':value},['products'])
            self.assertEqual(result['status'],expected['status'])
            self.assertEqual(result['findings'],expected['findings'])

    def test_no_admission_identity_and_input_immutability(self):
        t=rational()
        spec=manifest({'a':t},op('eq',op('mul',ref('a'),ref('a')),constant('4/1',t)))
        values={'a':known('2/1')}
        before=deepcopy((spec,values))
        result=run(spec,values)
        self.assertEqual(before,(spec,values))
        for key in ['executed','source_admission','accounting_admission','method_eligible']:
            self.assertFalse(result[key])
        self.assertEqual(run(spec,values,[])['status'],'unsupported')
        h=old.digest(spec)
        changed=deepcopy(spec)
        changed['version']='3'
        self.assertEqual(new.assess({h:changed},h,values,[])['status'],'invalid')

    def test_invalid_type_definitions_and_private_names(self):
        t=rational()
        for edit in [lambda x:x.update(scale='0/1'),lambda x:x.update(scale='-1/1'),
                     lambda x:x.update(scale='2/2'),lambda x:x.update(dimensions={'USD':0}),
                     lambda x:x.update(dimensions={'USD':True}),lambda x:x.update(dimensions={'USD':33}),
                     lambda x:x['context'].update(unit='USD'),lambda x:x['context'].update(currency='USD'),
                     lambda x:x['context'].update({'@scale':'1/1'}),lambda x:x.update(extra=True)]:
            bad=deepcopy(t)
            edit(bad)
            with self.assertRaises(ValueError):
                new.typed(bad)
        spec=manifest({'@product/0':t},op('eq',ref('@product/0'),constant('1/1',t)))
        self.assertEqual(run(spec,{'@product/0':known('1/1')})['status'],'invalid')
        spec=manifest({'a':t},op('eq',op('mul',ref('a'),ref('a')),constant('1/1',t)))
        for value in [1,True,'2/2',1.0]:
            self.assertEqual(run(spec,{'a':known(value)})['status'],'invalid')


if __name__=='__main__':
    unittest.main()
