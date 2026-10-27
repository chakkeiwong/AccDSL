"""Bounded, exact DemoDebt execution over validated Core0.1 IR.

This synthetic method is not an accounting-standard implementation. All
frontends use execute(); no expected-result section is read by execution.
"""
from __future__ import annotations

import copy
from dataclasses import replace
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re

import core0_ir_v1 as ir
from core0_frontends_v1 import compile_source

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'docs/design/fixtures/demo-debt-package.json'
FIXTURES = ROOT / 'docs/design/fixtures/p11'
REASON = 'Fixed-rate proportion not disclosed'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def round_money(value):
    """Exact cent half-even, including negative ties (no binary floats)."""
    scaled = F(value) * 100
    q, r = divmod(scaled.numerator, scaled.denominator)
    if 2*r > scaled.denominator or (2*r == scaled.denominator and q % 2):
        q += 1
    return F(q, 100)


def make_bindings(principal=100, cash=None, renamed=False, interior=False, package_path=PACKAGE):
    p = F(str(principal))
    cash = p-5 if cash is None else F(str(cash))
    b = ir.CompileBindings.demo(principal=p, opening_balances={
        'Cash': cash, 'Debt': -p, 'InterestExpense': 0, 'Retained': p-cash})
    # The inherited demo helper lacks system_as_of; explicit synthetic evidence
    # must be visible at its recorded acceptance time (same as P03 fixtures).
    readings = [replace(r, system_as_of=r.cutoff) for r in b.readings]
    book, sym = ('Statutory', 'share') if renamed else ('Local', 'alpha')
    names = ('fixed', 'floating') if renamed else ('allFixed', 'allFloating')
    if interior:
        names += ('conditioned',)
    return replace(b, readings=readings,
        packages=[replace(b.packages[0], digest=hashlib.sha256(Path(package_path).read_bytes()).hexdigest())],
        openings=[ir.OpeningBinding('after-2025-close', '2025-12-31',
                  dict(b.openings[0].balances), book=book)],
        admissions=[replace(b.admissions[0], name=sym)],
        alternatives=[ir.AlternativeBinding(n, 'synthetic-fixture-author', readings[0].cutoff,
                       'Explicit condition; no probability assigned') for n in names],
        entity_perimeter='Beta-only' if renamed else 'Acme-only')


def source_program(principal=100, stress='0.07', renamed=False, interior=False):
    source = (FIXTURES / 'borrowing.acc').read_text()
    source = source.replace('100 USD', f'{principal} USD').replace('0.07 per year', f'{stress} per year')
    if interior:
        source = source.replace('scenario rateShock', 'alternative conditioned { assume alpha == 0.25; }\nscenario rateShock')
    if renamed:
        names = dict(zip(('BorrowingExample','note7','Acme','Local','after2025','debt','alpha',
                          'loans','allFixed','allFloating','rateShock','statements'),
                         ('FinancingStudy','disclosure','Beta','Statutory','carried','borrowing','share',
                          'facility','fixed','floating','shock','financials')))
        # Replace identifiers outside quoted strings only; external keys stay fixed.
        source = re.sub(r'"(?:[^"\\]|\\.)*"|\b[A-Za-z_][A-Za-z_0-9]*\b',
                        lambda m: names.get(m[0], m[0]), source)
    return source


def typed_program(principal=100, stress='0.07', renamed=False, interior=False):
    """Independent constructor input; never parses source or authored IR."""
    mod, src, ent, book, opening, obs, sym, contract, fixed, floating, scenario, report = (
        ('FinancingStudy','disclosure','Beta','Statutory','carried','borrowing','share','facility',
         'fixed','floating','shock','financials') if renamed else
        ('BorrowingExample','note7','Acme','Local','after2025','debt','alpha','loans',
         'allFixed','allFloating','rateShock','statements'))
    ds = [ir.SourceDecl(src, 'synthetic-note-7'), ir.EntityDecl(ent, 'USD'),
          ir.BookDecl(book, ent, 'DemoDebt', '1')]
    ds += [ir.AccountDecl(n, role, book) for n, role in
           [('Cash','Asset'),('Debt','Liability'),('InterestExpense','Expense'),('Retained','Equity')]]
    ds += [ir.OpeningDecl(opening, book, 'after-2025-close'),
           ir.ObservationDecl(obs, 'Money<USD>', '2025-12-31', ir.Literal(F(str(principal)), unit='USD'), src),
           ir.SymbolDecl(sym, 'Real', ir.Literal(F(0)), ir.Literal(F(1)), REASON),
           ir.ContractDecl(contract, 'DebtMix', book, [
               ('principal', ir.Call('value', [ir.Ref(obs)])), ('fixed_fraction', ir.Ref(sym)),
               ('fixed_rate', ir.Literal(F(1,20), unit='per year')),
               ('initial_floating_rate', ir.Literal(F(1,20), unit='per year'))])]
    for name, value in [(fixed,F(1)),(floating,F(0))] + ([('conditioned', F(1,4))] if interior else []):
        ds.append(ir.AlternativeDecl(name, [ir.Binary('==', ir.Ref(sym), ir.Literal(value))]))
    ds += [ir.ScenarioDecl(scenario, [('market_rate', ir.Call('constant', [ir.Literal(F(stress), unit='per year')]))]),
           ir.ReportDecl(report, book, ir.External('DemoDebt.statements.v1'))]
    return ir.Program(mod, '1', ds, [ir.UseDecl('DemoDebt', '1')])


class EventBook:
    """Local atomic posting/replay primitive; no durable storage claim."""
    def __init__(self, balances):
        self.balances = {k:F(v) for k,v in balances.items()}
        self.events = {}

    def commit(self, event_id, payload, postings):
        normalized = {k:F(v) for k,v in postings.items()}
        fingerprint = digest({'payload':payload, 'postings':{k:str(v) for k,v in normalized.items()}})
        if event_id in self.events:
            if self.events[event_id]['digest'] != fingerprint:
                raise ValueError('EventConflict')
            return False
        if sum(normalized.values()) != 0 or set(normalized)-set(self.balances):
            raise ValueError('InvalidPosting')
        updated = dict(self.balances)
        for account, amount in normalized.items():
            updated[account] += amount
        self.balances = updated
        self.events[event_id] = {'digest':fingerprint, 'payload':copy.deepcopy(payload),
                                'postings':{k:str(v) for k,v in normalized.items()}}
        return True


def execute(model, bindings, *, assignments, alternative, scenario=None, package_path=PACKAGE):
    validation = ir.validate_ir(model, bindings)
    if not validation.ok:
        raise ValueError('InvalidIR: ' + repr(validation.diagnostics))
    raw = Path(package_path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != model['packages'][0]['digest']:
        raise ValueError('PackageDigestMismatch')
    package = json.loads(raw)
    reference = json.loads(PACKAGE.read_bytes())
    # Implemented method semantics are frozen; expected outputs are non-executable.
    for value in (package, reference):
        value.pop('expected', None)
    if package != reference:
        raise ValueError('UnsupportedPackageSemantics')
    if (bindings.calendar_id, bindings.calendar_name, bindings.horizon_start, bindings.horizon_end) != (
            'DemoCalendar@1','Gregorian','2026-01-01','2027-01-01'):
        raise ValueError('UnsupportedCalendarOrHorizon')
    if set(assignments) != {s['id'] for s in model['symbols']}:
        raise ValueError('ExplicitCompleteConditionRequired')
    symbols = {k:F(v) for k,v in assignments.items()}
    for s in model['symbols']:
        domain = s['domain']
        if not ir.parse_rational(domain['lower']) <= symbols[s['id']] <= ir.parse_rational(domain['upper']):
            raise ValueError('SymbolDomainViolation')
    alternatives = {a['id']:a for a in model['alternatives']}
    if alternative not in alternatives:
        raise ValueError('UnknownAlternative')
    active_scopes = {alternative, model['modelScopes'][0]['id']}
    ev = lambda expression: ir.evaluate_expression(model, expression, symbols)
    for c in model['constraints']:
        if c['scope'] in active_scopes and ev(c['expression']) is not True:
            raise ValueError('BranchConstraintViolation')
    scenarios = {s['id']:s for s in model['scenarios']}
    scenario = scenario or next(iter(scenarios))
    if scenario not in scenarios:
        raise ValueError('UnknownScenario')
    contract = model['contracts'][0]
    fields = {f['name']:ev(f['expression']) for f in contract['fields']}
    principal, alpha = fields['principal'], fields['fixed_fraction']
    rate = ev(scenarios[scenario]['drivers'][0]['expression'])
    if not (principal >= 0 and 0 <= alpha <= 1 and rate >= 0 and
            fields['fixed_rate'] >= 0 and fields['initial_floating_rate'] >= 0):
        raise ValueError('InvalidContractState')
    opening = model['states'][0]
    book = EventBook({b['account']:ir.parse_rational(b['signed_amount']) for b in opening['balances']})
    if (set(book.balances) != {'Cash','Debt','InterestExpense','Retained'} or
            sum(book.balances.values()) != 0 or book.balances['InterestExpense'] != 0 or
            book.balances['Debt'] != -principal):
        raise ValueError('UnsupportedOpening')
    terms = package['DebtMix']['additional_terms']
    year_fraction = F(terms['year_fraction'])
    interest = round_money(principal*(alpha*fields['fixed_rate']+(1-alpha)*rate)*year_fraction)
    run_id = digest({'model':ir.semantic_projection(model),'assignments':{k:str(v) for k,v in symbols.items()},
                     'alternative':alternative,'scenario':scenario})
    book.commit(run_id+':reset', {'operation':'reset','date':terms['accrual_period'][0],
                                'market_rate':str(rate)}, {})
    opening_equity = -book.balances['Retained']
    failed = book.balances['Cash'] < interest
    if not failed:
        book.commit(run_id+':settlement', {'operation':'accrue_and_pay','date':terms['pay_date'],
                    'interest':str(interest)}, {'InterestExpense':interest,'Cash':-interest})
        book.commit(run_id+':close', {'operation':'close','date':terms['pay_date']},
                    {'Retained':interest,'InterestExpense':-interest})
    profit = F(0) if failed else -interest
    reports = {'cash':str(book.balances['Cash']), 'debt':str(-book.balances['Debt']),
               'equity':str(-book.balances['Retained']), 'profit':str(profit),
               'comprehensive_income':str(profit), 'operating_cash_flow':str(profit),
               'opening_equity':str(opening_equity)}
    if sum(book.balances.values()) != 0:
        raise ValueError('UnbalancedResult')
    return {'status':'Defaulted' if failed else 'Completed',
            'report_status':'Incomplete_unpaid_obligation' if failed else 'Complete_for_DemoDebt',
            'run_id':run_id, 'alternative':alternative, 'scenario':scenario,
            'condition':{k:str(v) for k,v in symbols.items()}, 'probability':None,
            'principal':str(principal),'fixed_fraction':str(alpha),'market_rate':str(rate),
            'interest':str(interest), 'unpaid_interest':str(interest if failed else 0),
            'reports':reports,'balances':{k:str(v) for k,v in book.balances.items()},
            'events':copy.deepcopy(book.events), 'currency':'USD', 'calendar':bindings.calendar_id,
            'year_fraction':str(year_fraction),'rounding':'cent_half_even'}


def matched_case(**options):
    runtime_options = {k:options.pop(k) for k in list(options) if k in ('cash','package_path')}
    b = make_bindings(**{k:v for k,v in options.items() if k != 'stress'}, **runtime_options)
    source = source_program(**options)
    typed = typed_program(**options)
    textual = compile_source(source, b)
    constructed = ir.compile_program(typed, b)
    if not textual.ok or not constructed.ok:
        raise ValueError(repr((textual.diagnostics, constructed.diagnostics)))
    if ir.semantic_projection(textual.ir) != ir.semantic_projection(constructed.ir):
        raise ValueError('FrontendSemanticMismatch')
    return source, typed, b, textual.ir, constructed.ir
