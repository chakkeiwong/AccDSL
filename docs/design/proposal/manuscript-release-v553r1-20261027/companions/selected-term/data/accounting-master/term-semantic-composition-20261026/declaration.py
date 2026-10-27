from copy import deepcopy
import bundle as b
d=b.d;p=b.p;core=b.core;g=d.g

def common(state):
    book=state['book'];money=p.base.money_type(book)
    fields={'identity':p.guards.TEXT,'sale_event':p.guards.TEXT,'issued':p.guards.DATE,'remaining':money}
    rows=[g.rule('remaining_nonnegative',g.binary('le',g.const(money,'0/1'),g.ref('remaining')),['remaining']),
          g.rule('issued_by_book',g.binary('le',g.ref('issued'),g.ref('as_of')),['issued','as_of'])]
    declare=lambda typ,name:dict(type=deepcopy(typ),role='state',source_ref='explicit common term-state condition:'+name)
    per_row=dict(profile=b.t.c.guarded.PROFILE,method_id='term.common.row',version='1',
      inputs={k:declare(v,k) for k,v in dict(remaining=money,issued=p.guards.DATE,as_of=p.guards.DATE).items()},
      requirements=rows,required_known=[],capabilities=[],residual_prerequisites=['Common claim conditions only'])
    snapshot=dict(profile=b.guards.totals.snapshot.PROFILE,method_id='term.common',version='1',
      inputs={'as_of':declare(p.guards.DATE,'as_of'),'receivable':declare(money,'receivable')},
      collections={'claims':dict(fields={k:declare(v,k) for k,v in fields.items()}),'seen':dict(fields={'id':declare(p.guards.TEXT,'seen')})},
      constraints=[dict(id='claim_ids',op='unique',collection='claims',field='identity'),
        dict(id='sale_seen',op='references',source='claims',field='sale_event',target='seen',target_field='id'),
        dict(id='common_rows',op='each',collection='claims',definition=per_row,
             bindings={k:dict(scope='global' if k=='as_of' else 'row',field=k) for k in per_row['inputs']})],
      residual_prerequisites=['Complete supplied claims only'])
    total_manifest=dict(profile=b.t.c.guarded.PROFILE,method_id='term.common.total',version='1',
      inputs={k:declare(money,k) for k in ('total','receivable')},requirements=[g.rule('claim_receivable_sum',
       g.binary('eq',g.ref('total'),g.ref('receivable')),['total','receivable'])],required_known=[],capabilities=[],
      residual_prerequisites=['No source/accounting admission'])
    definition=dict(profile=b.guards.totals.PROFILE,method_id='term.common',version='1',snapshot=snapshot,assessment=total_manifest,
      bindings={'total':dict(kind='sum',collection='claims',field='remaining'),'receivable':dict(kind='global',input='receivable')},
      residual_prerequisites=['Historical assessment predicates are separate'])
    return dict(profile=b.guards.PROFILE,context=deepcopy(book['context']),definition=definition,
      globals={'as_of':dict(kind='date'),'receivable':dict(kind='balance',account=state['roles']['receivables'])},
      collections={'claims':dict(kind='memory_map',pointer='/claims',fields={k:dict(kind='key') if k=='identity' else dict(kind='field',pointer='/'+k) for k in fields}),
                   'seen':dict(kind='seen',fields={'id':dict(kind='value')})},
      residual_prerequisites=['Role selection, exact native schema and migration premise remain separate'])

def build(state):
    clock_manifest=dict(profile=b.t.c.guarded.PROFILE,method_id='term.clock',version='1',
      inputs={k:dict(type=p.guards.DATE,role='state',source_ref='explicit book date:'+k) for k in ('cursor','end')},
      requirements=[g.rule('cursor_period',g.binary('le',g.ref('cursor'),g.ref('end')),['cursor','end'])],
      required_known=[],capabilities=[],residual_prerequisites=['Date-only native cursor convention'])
    return dict(profile=b.PROFILE,context=deepcopy(state['book']['context']),common=common(state),
      clock=dict(manifest=clock_manifest,bindings={'cursor':dict(kind='book_field',pointer='/memory/collection_clock/cursor',type=p.guards.DATE),
        'end':dict(kind='book_field',pointer='/period/end_exclusive',type=p.guards.DATE)}),
      terms=d.term_template(state),assessments=d.assessment_template(state),summaries=d.f.group_spec(state),events=d.event_collections(state),
      residuals=['Native structural schema, roles/cost and migration premise require separate reviewed admission',
        'Synthetic supplied state only; actual history completeness and accounting treatment unadmitted'])

def populations(state,spec):
    book=state['book']
    return {'claims':dict(profile='SuppliedClaimPopulation/1',status='complete',map_pointer='/claims',book_sha256=core.digest(book),provenance='Explicit supplied semantic fixture'),
      'terms':p.population(spec['terms']['iteration'],book,'complete','Explicit supplied term rows'),
      'assessments':p.population(spec['assessments']['iteration'],book,'complete','Explicit supplied assessment rows')}

def run(state,spec,coverage=None,selection=None,call=None):
    coverage=populations(state,spec) if coverage is None else coverage;selection=core.digest(spec) if selection is None else selection
    args=(spec,state['book'],state['memory_definition'],state['schemas'],coverage,selection)
    return b.assess(*args,b.make_call(*args) if call is None else call)
