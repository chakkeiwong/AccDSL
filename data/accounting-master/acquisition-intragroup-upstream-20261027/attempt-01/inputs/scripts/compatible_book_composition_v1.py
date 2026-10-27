"""Read-only common-chart worksheet from two separately valid synthetic books."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import company_book_transition_v1 as engine
import company_world_envelope_v1 as world

core=engine.core
PROFILE='CompatibleBookComposition/1'
PINS={'company_book_transition_v1.py':'3f46df2d4c7b65f344c0a1234177503a0869b9162b4a85bdda224c2eddbea8ff',
      'company_world_envelope_v1.py':'a048be2290e1d6631e40887f625d387608191c400e96b0bb5300f6c52fb73b2a'}
FLAGS={**engine.FLAGS,'executed':False,'consolidation_complete':False,'control_assessed':False,
       'references_resolved':False,'sector_methods_composed':False}
CLASSES=['asset','liability','equity','income','expense']
number=engine.monetary.rational
fmt=engine.monetary.fmt

def add(a,b):return engine.monetary.bounded(a+b)
def total(values):
    result=Fraction(0)
    for value in values:result=add(result,value)
    return result

def validate(body):
    for filename,h in PINS.items():
        core.need(sha256(Path(__file__).with_name(filename).read_bytes()).hexdigest()==h,'dependency_hash:'+filename)
    engine.protected();engine.binding.bounded(body);engine.memory.bounded(body)
    core.closed(body,['profile','world','books','schemas','chart','account_maps','eliminations','compatibility','control_edge_id'],'composition')
    core.need(body['profile']==PROFILE,'composition_profile');world.validate(body['world'])
    w=body['world'];books=body['books'];schemas=body['schemas'];chart=body['chart'];maps=body['account_maps']
    core.need(w['context']['mode']=='synthetic','synthetic_world_required')
    core.need(type(books) is dict and len(books)==2 and set(books)==set(w['books']),'exact_two_books')
    core.need(not w['obligations'],'unresolved_world_obligations')
    core.need(len(w['components'])==2 and {c['owner'] for c in w['components'].values()}==set(books),'exact_book_components')
    core.need(all(c['status']=='conditional' and not c['obligation_ids'] for c in w['components'].values()),'unresolved_components')
    core.need(type(schemas) is dict,'schema_registry')
    for h,shape in schemas.items():
        core.need(h==core.digest(shape),'schema_digest');engine.memory.check_schema(shape)
    compatibility=body['compatibility']
    core.closed(compatibility,['measurement_basis','accounting_policies','full_ownership_premise','elimination_scope'],'compatibility')
    for key,value in compatibility.items():world.text(value,'compatibility_'+key)
    core.need(type(chart) is dict and 0<len(chart)<=engine.monetary.MAX_ENTRIES,'common_chart_limit')
    for key,row in chart.items():
        world.text(key,'common_account');core.closed(row,['classification'],'common_account')
        core.need(row['classification'] in CLASSES,'common_classification')
    core.need(type(maps) is dict and set(maps)==set(books),'exact_book_maps')
    first=books[sorted(books)[0]];entities=set();used_targets=set()
    for key,book in books.items():
        engine.validate_book(book,schemas);handle=w['books'][key];context=book['context']
        core.need(handle['sector']=='corporate','corporate_books_only')
        core.need(handle['state_ref']==core.digest(book),'book_state_binding')
        core.need(all(handle[k]==context[k] for k in ['entity','book','currency']),'book_identity_binding')
        core.need(context['entity'] not in entities,'distinct_legal_entities');entities.add(context['entity'])
        core.need(context['case_id']==w['context']['case_id'],'book_case_binding')
        core.need(book['period']==first['period'] and book['date']==first['date'],'book_time_compatibility')
        mapping=maps[key]
        core.need(type(mapping) is dict and set(mapping)==set(book['accounts']),'complete_account_map')
        for local,target in mapping.items():
            core.need(type(target) is str and target in chart,'common_account_target')
            core.need(book['accounts'][local]['classification']==chart[target]['classification'],'account_classification_compatibility')
            used_targets.add(target)
    core.need(used_targets==set(chart),'unused_common_accounts')
    core.need(len(w['control_edges'])==1,'single_control_edge')
    edge=w['control_edges'][0]
    core.need(edge['id']==body['control_edge_id'],'control_edge_binding')
    core.need({edge['parent'],edge['child']}==entities,'control_parties')
    core.need(number(edge['ownership_fraction'])==1,'full_ownership_only')
    core.need(edge['start']<=first['date']<edge['end_exclusive'],'control_at_snapshot')
    core.need(edge['control_premise']==compatibility['full_ownership_premise'],'supplied_control_premise')
    eliminations=body['eliminations']
    core.need(type(eliminations) is list and len(eliminations)<=128,'elimination_limit')
    return first,edge

def compose(body):
    try:
        first,edge=validate(body);books=body['books'];chart=body['chart'];maps=body['account_maps']
        raw={k:Fraction(0) for k in chart};deltas={k:Fraction(0) for k in chart}
        contributions=[]
        for owner,book in books.items():
            for account,amount in book['balances'].items():
                target=maps[owner][account];raw[target]=add(raw[target],number(amount))
                contributions.append({'owner':owner,'account':account,'target':target,'amount':amount})
        used=set();ids=set();entries=[]
        for row in body['eliminations']:
            core.closed(row,['id','kind','positive','negative','premise'],'elimination')
            for key in ['id','kind','premise']:world.text(row[key],'elimination_'+key)
            core.need(row['id'] not in ids,'duplicate_elimination_id');ids.add(row['id'])
            core.need(row['kind'] in ['receivable_payable','investment_equity'],'elimination_kind')
            pair=[]
            for name in ['positive','negative']:
                ref=row[name];core.closed(ref,['owner','account','expected_balance'],'elimination_reference')
                for key in ['owner','account']:world.text(ref[key],'elimination_'+key)
                core.need(ref['owner'] in books,'elimination_owner');book=books[ref['owner']]
                core.need(ref['account'] in book['accounts'],'elimination_account')
                identity=(ref['owner'],ref['account']);core.need(identity not in used,'reused_elimination_account');used.add(identity)
                amount=number(ref['expected_balance'])
                core.need(ref['expected_balance']==book['balances'][ref['account']],'stale_elimination_balance')
                pair.append((book,ref,amount))
            positive,negative=pair
            core.need(positive[1]['owner']!=negative[1]['owner'],'cross_book_elimination_required')
            core.need(positive[2]>0 and negative[2]<0 and add(positive[2],negative[2])==0,'opposite_full_balances_required')
            expected=['asset','liability' if row['kind']=='receivable_payable' else 'equity']
            for item,classification in zip(pair,expected):
                book,ref,amount=item
                core.need(book['accounts'][ref['account']]['classification']==classification,'elimination_classification')
                core.need(ref['account']!=book['cash_account'],'cash_elimination_unsupported')
            if row['kind']=='investment_equity':
                core.need(positive[0]['context']['entity']==edge['parent'] and negative[0]['context']['entity']==edge['child'],'investment_control_direction')
            journal={k:Fraction(0) for k in chart}
            for book,ref,amount in pair:
                target=maps[ref['owner']][ref['account']];journal[target]=add(journal[target],-amount)
                deltas[target]=add(deltas[target],-amount)
            core.need(total(journal.values())==0,'elimination_unbalanced')
            entries.append({**deepcopy(row),'journal':{k:fmt(v) for k,v in journal.items()}})
        adjusted={k:add(raw[k],deltas[k]) for k in chart}
        core.need(total(raw.values())==0 and total(adjusted.values())==0,'worksheet_unbalanced')
        def totals(balances):
            values={kind:total(v for k,v in balances.items() if chart[k]['classification']==kind) for kind in CLASSES}
            profit=add(-values['income'],-values['expense']);equity=add(-values['equity'],profit)
            return {'assets':fmt(values['asset']),'liabilities':fmt(-values['liability']),
                    'equity_including_profit':fmt(equity),'profit':fmt(profit),
                    'balance_check':fmt(total([values['asset'],values['liability'],-equity]))}
        return {'profile':PROFILE,**FLAGS,'status':'worksheet_composed','request_sha256':core.digest(body),
            'date':first['date'],'period':deepcopy(first['period']),'world':deepcopy(body['world']),
            'books':deepcopy(books),'chart':deepcopy(chart),'account_maps':deepcopy(maps),
            'compatibility':deepcopy(body['compatibility']),'contributions':contributions,'eliminations':entries,
            'raw_balances':{k:fmt(v) for k,v in raw.items()},'elimination_deltas':{k:fmt(v) for k,v in deltas.items()},
            'adjusted_balances':{k:fmt(v) for k,v in adjusted.items()},'raw_totals':totals(raw),'adjusted_totals':totals(adjusted),
            'scope':'Supplied two-book snapshot and paired full-balance eliminations only',
            'unresolved':['Accounting-policy equivalence is supplied, not assessed','Elimination population completeness',
                          'Actual sources and control assessment','NCI, goodwill, tax, FX and intragroup profit',
                          'Period cash flows, equity movements and complete consolidated statements'],
            'dependency_sha256':deepcopy(PINS),'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
    except Exception as exc:return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350] or type(exc).__name__}

def verify(body,result):
    try:
        engine.binding.bounded(result)
        return core.canonical(compose(body))==core.canonical(result)
    except Exception:return False
