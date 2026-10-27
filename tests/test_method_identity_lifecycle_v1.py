"""Ordered identities, conservative unknowns and event-local atomicity."""
from copy import deepcopy
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import method_identity_lifecycle_v1 as lifecycle
import method_collections_v1 as snapshots


def known(value):return {'status':'known','value':value}
def unknown():return {'status':'unknown','reason':'not observed'}
def decl():return {'type':{'kind':'text','context':{'entity':'Example'}},'role':'state','source_ref':'constructed:identity'}
def fixture():
    fields={'initial':{'fields':{'id':decl()}},'retired':{'fields':{'id':decl()}},
            'events':{'fields':{'id':decl(),'action':decl(),'key':decl(),'second':decl()}}}
    snapshot={'profile':snapshots.PROFILE,'method_id':'identity.snapshot','version':'1','inputs':{},
              'collections':fields,'constraints':[{'id':'event.ids','op':'unique','collection':'events','field':'id'}],
              'residual_prerequisites':['Identity state checked separately.']}
    actions=[{'tag':op,'operations':[{'op':op,'pool':'stock','key':{'scope':'row','field':'key'}}]}
             for op in ['create','require','consume']]
    d={'profile':lifecycle.PROFILE,'method_id':'independent.identity','version':'1','snapshot':snapshot,
       'events':'events','action_field':'action',
       'pools':{'stock':{'live':{'collection':'initial','field':'id'},
                         'retired':{'collection':'retired','field':'id'}}},'actions':actions,
       'residual_prerequisites':['No monetary state or accounting admission.']}
    rows=[{'id':known(str(i)),'action':known(action),'key':known('lot')} for i,action in enumerate(['create','require','consume'])]
    values={'globals':{},'collections':{'initial':{'status':'complete','rows':[]},
        'retired':{'status':'complete','rows':[]},'events':{'status':'complete','rows':rows}}}
    return d,values


def run(d,v):return lifecycle.assess(d,v,[])


class IdentityTests(unittest.TestCase):
    def test_complete_trace_preserves_inputs_and_no_admission(self):
        d,v=fixture();before=deepcopy((d,v));r=run(d,v)
        self.assertEqual(r['status'],'identity_requirements_satisfied')
        self.assertEqual(r['identity_status'],'complete')
        self.assertEqual([x['action'] for x in r['trace']],['create','require','consume'])
        self.assertEqual(r['state']['stock'],{'live':[],'retired':['lot']})
        self.assertEqual(before,(d,v))
        for flag in ['executed','method_eligible','source_admission','accounting_admission']:
            self.assertFalse(r[flag])

    def test_consume_requires_prior_creation_and_no_reuse(self):
        d,v=fixture();v['collections']['events']['rows'].reverse()
        r=run(d,v);self.assertEqual(r['reason'],'identity_not_live');self.assertEqual(r['stopped_index'],0)
        d,v=fixture();rows=v['collections']['events']['rows']
        rows.append({'id':known('3'),'action':known('consume'),'key':known('lot')})
        r=run(d,v);self.assertEqual(r['reason'],'identity_not_live');self.assertEqual(len(r['trace']),3)
        rows[-1]['action']=known('create')
        r=run(d,v);self.assertEqual(r['reason'],'identity_already_used');self.assertEqual(len(r['trace']),3)

    def test_initial_retired_identity_blocks_recreation(self):
        d,v=fixture();v['collections']['retired']['rows']=[{'id':known('lot')}]
        r=run(d,v);self.assertEqual(r['reason'],'identity_already_used')
        v['collections']['initial']['rows']=[{'id':known('lot')}]
        r=run(d,v);self.assertEqual(r['reason'],'invalid_initial_identity')
        self.assertEqual(r['details']['violations'][0]['reason'],'initial_live_retired_overlap')

    def test_initial_duplicates_dominate_unknowns(self):
        d,v=fixture();v['collections']['initial']['rows']=[{'id':known('a')},{'id':known('a')},{'id':unknown()}]
        r=run(d,v);self.assertEqual(r['status'],'invalid')
        self.assertTrue(r['details']['unknown'])

    def test_unknown_stops_without_later_execution(self):
        for key in ['action','key']:
            d,v=fixture();v['collections']['events']['rows'][1][key]=unknown()
            r=run(d,v);self.assertEqual(r['status'],'unresolved');self.assertEqual(r['stopped_index'],1)
            self.assertEqual(len(r['trace']),1);self.assertEqual(r['state']['stock']['live'],['lot'])
            self.assertEqual(r['unprocessed_indices'],[1,2])

    def test_partial_initial_or_sequence_stops_before_first_event(self):
        for name in ['initial','retired','events']:
            d,v=fixture();v['collections'][name].update(status='partial',reason='missing rows')
            r=run(d,v);self.assertEqual(r['status'],'unresolved');self.assertEqual(r['trace'],[])
            d,v=fixture();v['collections'].pop(name)
            self.assertEqual(run(d,v)['status'],'unresolved')

    def test_failed_and_unknown_event_operations_are_atomic(self):
        for value,reason in [(known('absent'),'identity_not_live'),(unknown(),'event_key_unknown')]:
            d,v=fixture();d['actions'][0]['operations'].append(
                {'op':'consume','pool':'stock','key':{'scope':'row','field':'second'}})
            v['collections']['events']['rows'][0]['second']=value
            r=run(d,v);self.assertEqual(r['reason'],reason)
            self.assertEqual(r['state']['stock'],{'live':[],'retired':[]});self.assertEqual(r['trace'],[])

    def test_later_known_action_and_type_errors_are_not_hidden(self):
        d,v=fixture();v['collections']['events']['rows'][0]['action']=unknown()
        v['collections']['events']['rows'][2]['action']=known('callback')
        self.assertEqual(run(d,v)['reason'],'unmapped_action_tag:callback')
        v['collections']['events']['rows'][2]['action']=known('consume')
        v['collections']['events']['rows'][2]['key']=known(12)
        self.assertEqual(run(d,v)['status'],'invalid')

    def test_definition_closure_mappings_and_key_types(self):
        edits=[lambda d:d['actions'].append(deepcopy(d['actions'][0])),
               lambda d:d['actions'][0]['operations'][0].update(op='call'),
               lambda d:d['actions'][0]['operations'][0].update(pool='absent'),
               lambda d:d['actions'][0]['operations'][0]['key'].update(field='absent'),
               lambda d:d['snapshot']['collections']['events']['fields']['key']['type']['context'].update(entity='Other'),
               lambda d:d['pools']['stock']['retired'].update(field='absent')]
        for edit in edits:
            d,v=fixture();edit(d);self.assertEqual(run(d,v)['status'],'invalid')

    def test_snapshot_unknown_does_not_invent_an_identity_failure(self):
        d,v=fixture();v['collections']['events']['rows'][0]['id']=unknown()
        r=run(d,v)
        self.assertEqual(r['identity_status'],'complete');self.assertEqual(len(r['trace']),3)
        self.assertEqual(r['status'],'unresolved')
        v['collections']['events']['rows'][0]['id']=known('1')
        r=run(d,v);self.assertEqual(r['reason'],'snapshot_precondition_failed');self.assertEqual(r['trace'],[])

    def test_limits_are_explicit(self):
        d,v=fixture();action=deepcopy(d['actions'][1]);d['actions']=[]
        for i in range(lifecycle.MAX_ACTIONS):
            item=deepcopy(action);item['tag']=str(i);d['actions'].append(item)
        v['collections']['events']['rows']=[]
        self.assertEqual(run(d,v)['status'],'identity_requirements_satisfied')
        d['actions'].append({**action,'tag':'extra'})
        self.assertEqual(run(d,v)['reason'],'action_limit')
        d,v=fixture();d['actions'][1]['operations']*=lifecycle.MAX_OPERATIONS
        lifecycle.validate(d)
        d['actions'][1]['operations'].append(deepcopy(d['actions'][1]['operations'][0]))
        self.assertEqual(run(d,v)['reason'],'operation_limit')
        d,v=fixture();pool=deepcopy(d['pools']['stock'])
        d['pools'].update({str(i):deepcopy(pool) for i in range(lifecycle.MAX_POOLS-1)})
        lifecycle.validate(d)
        d['pools']['extra']=pool
        self.assertEqual(run(d,v)['reason'],'pool_limit')


if __name__=='__main__':unittest.main()
