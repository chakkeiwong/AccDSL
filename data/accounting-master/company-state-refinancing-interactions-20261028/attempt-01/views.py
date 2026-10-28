"""Scoped teaching tax/share views with explicit complete dependencies."""
from copy import deepcopy
from fractions import Fraction as Q
import fixture as f


def derive(book, schemas, roles, policy):
    if set(policy) != set(f.TAX):
        return dict(status='unresolved', reason='complete_explicit_tax_premises_required')
    if any(v is None for v in policy.values()):
        return dict(status='unresolved', reason='unknown_tax_premise')
    if any(type(policy[k]) is not bool for k in ['fee_deductible','interest_deductible','recognition']):
        return dict(status='invalid',reason='boolean_tax_premises_required')
    if any(policy[k] != f.TAX[k] for k in ['profile','fee_deductible','interest_deductible','recognition','basis']):
        return dict(status='unsupported', reason='outside_supplied_tax_treatment')
    try:
        f.program.engine.validate_book(book,schemas)
        if len(set(roles.values())) != len(roles) or any(v not in book['accounts'] for v in roles.values()):
            raise ValueError('invalid_roles')
        expected={'cash':'asset','debt':'liability','new_debt':'liability','fee':'expense',
                  'interest':'expense','revenue':'income','current_tax':'expense','tax_payable':'liability','capital':'equity'}
        if any(book['accounts'][roles[k]]['classification'] != v for k,v in expected.items()):
            raise ValueError('role_classification')
        if isinstance(policy['rate'],(float,bool)) or not isinstance(policy['source'],str) or not policy['source']:
            raise ValueError('explicit_exact_policy')
        rate=Q(policy['rate'])
        if rate<0:raise ValueError('nonnegative_rate')
        money=f.program.engine.money_type(book)
        share_type={**deepcopy(money),'dimensions':{'equity:share':1}}
        if any(book['memory_types'].get('/ownership/'+k)!=share_type for k in ['old','new']):
            raise ValueError('share_units')
        balances=book['balances'];old=Q(book['memory']['ownership']['old']);new=Q(book['memory']['ownership']['new'])
        if old<=0 or new<0:raise ValueError('share_population')
        for key in ['old','new']:
            if Q(book['memory']['finance'][key+'_debt'])!=Q(balances[roles['debt' if key=='old' else 'new_debt']]):
                raise ValueError('instrument_debt_mismatch')
        if Q(balances[roles['current_tax']]) or Q(balances[roles['tax_payable']]):
            return dict(status='unsupported',reason='pre_accrual_view_only')
        supported={roles[k] for k in ['revenue','fee','interest','current_tax']}
        if any(Q(balances[k]) for k,a in book['accounts'].items()
               if a['classification'] in ['income','expense'] and k not in supported):
            return dict(status='unsupported',reason='unmodeled_income_or_expense')
        pretax=-sum(Q(balances[roles[k]]) for k in ['revenue','fee','interest'])
        dependency=dict(book=deepcopy(book),schemas=deepcopy(schemas),roles=deepcopy(roles),policy=deepcopy(policy))
        return dict(status='conditional',dependencies=dependency,dependency_sha256=f.program.digest(dependency),
                    pretax=f.fmt(pretax),tax=f.fmt(max(Q(0),pretax)*rate),
                    old_fraction=f.fmt(old/(old+new)),new_fraction=f.fmt(new/(old+new)),
                    source_admission=False,accounting_admission=False)
    except (ValueError,KeyError,TypeError,ZeroDivisionError) as exc:
        return dict(status='invalid',reason=str(exc))


def reuse(saved,book,schemas,roles,policy):
    fresh=derive(book,schemas,roles,policy)
    if fresh.get('status')!='conditional':return fresh
    if saved!=fresh:return dict(status='stale',reason='dependency_or_result_changed')
    return deepcopy(fresh)


def complete(body,roles,policy,saved=None):
    prefix=f.program.run(body)
    if prefix['status']!='complete_provisional':
        return dict(status='prefix_refused',prefix=prefix)
    args=(prefix['current'],body['schemas'],roles,policy)
    view=derive(*args) if saved is None else reuse(saved,*args)
    if view['status']!='conditional':return dict(status=view['status'],view=view,prefix=prefix)
    joined=f.finish(body,roles,view['tax'])
    return dict(status='evaluated',view=view,program=joined,result=f.program.run(joined))
