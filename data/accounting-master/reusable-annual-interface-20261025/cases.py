from copy import deepcopy
from examples import m,assessment,payment,deferred,carry,scenario,repeated_scenario,start

def cases():
    rows=[];q=scenario();r=m.run(q);state=r['period_book'];origin=q['root_request']
    def add(name,body,status='complete_provisional',stop=None):
        rows.append({'case':name,'request':deepcopy(body),'expected_status':status,'expected_stop':stop})
    add('empty_program',m.request(origin,[]))
    add('first_three_vintages',m.request(origin,q['operations'][:1]))
    add('three_vintage_payment',m.request(origin,q['operations'][:2]))
    add('cumulative_replacement',q)
    repeat=repeated_scenario();rr=m.run(repeat);later=rr['period_book']
    add('four_vintages_new_period',repeat)
    add('four_vintage_payment',m.request(origin,repeat['operations']+[payment(later,['1/1','1/1','1/1','1/1'],'four-pay','2028-12-31')]))
    tail=deepcopy(repeat['operations']);d=deferred(later,'next-deferred');after=m.transition(later,d)['after']
    tail += [d,carry(after,'next-carry','2030-01-01')]
    add('same_carry_repeated',m.request(origin,tail))
    current=assessment(state,'12/1','year-end','replace','2028-01-01')
    endpoint=m.transition(state,current)['after'];d=deferred(endpoint)
    add('fresh_deferred',m.request(origin,q['operations']+[current,d]))
    for name,mutate,stop in [
        ('negative_rate',lambda e:e['information']['rate'].update(value='-1/4'),'invalid'),
        ('unknown_rate',lambda e:e['information'].update(rate={'status':'unknown','reason':'No rate'}),'unresolved'),
        ('foreign_jurisdiction',lambda e:e['information']['jurisdiction'].update(value='another'),'invalid'),
        ('shortened_assessment',lambda e:e['interval'].update(end_exclusive='2027-06-01',activity_through='2027-05-31'),'invalid'),
        ('wrong_start',lambda e:e['interval'].update(start='2027-01-02'),'invalid'),
        ('wrong_mode',lambda e:e.update(mode='first'),'invalid'),
        ('duplicate_id',lambda e:e.update(id='annual-first'),'invalid'),
        ('model_unknown',lambda e:e['model'].update(selected={'status':'unknown','reason':'No choice'}),'unresolved'),
        ('model_false',lambda e:e['model']['selected'].update(value=False),'unsupported'),
        ('unsupported_model',lambda e:e['model'].update(profile='inferred_tax_v1'),'unsupported'),
        ('missing_allocation',lambda e:e.update(allocations=[]),'invalid')]:
        bad=deepcopy(current);mutate(bad['event']);add(name,m.request(origin,q['operations']+[bad]),'stopped_provisional',stop)
    bad=assessment(state,'4/1','refund-needed','replace')
    add('refund_required',m.request(origin,q['operations']+[bad]),'stopped_provisional','unsupported')
    add('deferred_without_current',m.request(origin,[deferred(m.seed(r['root_result']))]),'stopped_provisional','unresolved')
    add('carry_without_deferred',m.request(origin,q['operations']+[current,carry(endpoint)]),'stopped_provisional','unresolved')
    assessed=m.transition(endpoint,d)['after']
    pay=payment(assessed,['0/1','0/1','1/1'],'after-measurement','2027-12-31')
    add('stale_deferred_carry',m.request(origin,q['operations']+[current,d,pay,carry(assessed)]),'stopped_provisional','unresolved')
    for name,mutate,stop in [
        ('unknown_capacity',lambda e:e.update(recovery_capacity={'status':'unknown','reason':'No fresh capacity'}),'unresolved'),
        ('insufficient_capacity',lambda e:e['recovery_capacity'].update(value='1/1'),'invalid'),
        ('missing_item',lambda e:e['items'].pop(),'invalid'),
        ('stale_measurement',lambda e:e['measurement'].update(state_sha256='0'*64),'invalid'),
        ('unsupported_oci',lambda e:e['items'][0]['route'].update(value='oci'),'unsupported')]:
        bad=deepcopy(d);mutate(bad['event']);add(name,m.request(origin,q['operations']+[current,bad]),'stopped_provisional',stop)
    for name,mutate in [('gap',lambda e:e['next_period'].update(start='2028-01-02')),
                        ('duplicate_carry_id',lambda e:e.update(id='annual-first'))]:
        bad=carry(assessed);mutate(bad['event']);add(name,m.request(origin,q['operations']+[current,d,bad]),'stopped_provisional','invalid')
    _,initial=start(origin);high=assessment(initial,'2000/1');high_state=m.transition(initial,high)['after']
    add('actual_cash_shortage',m.request(origin,[high,payment(high_state,['0/1','0/1','400/1'])]),'stopped_provisional','funding_failure')
    for name,mutate in [('unknown_vintage',lambda e:e['allocations'][0].update(vintage_id='missing')),
                        ('duplicate_allocation',lambda e:e['allocations'].append(deepcopy(e['allocations'][0]))),
                        ('overpay_vintage',lambda e:e['allocations'][0].update(amount='100/1')),
                        ('prior_event_id',lambda e:e.update(id='period-payment')),
                        ('endpoint_payment',lambda e:e.update(date='2028-01-01'))]:
        bad=payment(state,['1/1','1/1','0/1']);mutate(bad['event']);add(name,m.request(origin,q['operations']+[bad]),'stopped_provisional','invalid')
    bad=deepcopy(q);bad['root_sha256']='0'*64;add('stale_root',bad,'invalid')
    bad=deepcopy(q);bad['operations'][0]['event']['information']['rate']['value']=0.25;add('nonportable_float',bad,'invalid')
    return rows
