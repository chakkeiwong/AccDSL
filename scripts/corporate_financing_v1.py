"""Bounded, exact AASB issuer compound-bond lifecycle (P08).

Eligibility and fair value/yield inputs are explicit synthetic assumptions, not
inferred accounting opinions. Annual calendar periods only; no market model.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
REGISTER = 'docs/design/research/p08-v1/authority-register.json'
REQUIRED = ('recognition', 'classification', 'split', 'measurement', 'interest',
            'redemption', 'conversion', 'note_carrying', 'note_interest')
ACCOUNTS = ('cash', 'liability', 'conversion_equity', 'share_equity',
            'opening_equity', 'interest_expense')


class Unsupported(ValueError):
    """A fact, source, or event is outside the explicitly supported slice."""


def rational(value):
    if isinstance(value, (bool, float)) or not isinstance(value, (str, int, Fraction)):
        raise Unsupported('amounts and rates require exact integer/rational inputs')
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise Unsupported('invalid rational') from exc


def iso(value):
    try:
        result = date.fromisoformat(value)
        if result.isoformat() != value:
            raise ValueError('noncanonical date')
        return result
    except (ValueError, TypeError) as exc:
        raise Unsupported('canonical ISO date required') from exc


def wire(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {key: wire(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [wire(val) for val in value]
    return value


def normal(value):
    return re.sub(r'\s+', ' ', value).strip()


class AuthorityBook:
    def __init__(self, root=ROOT, records=None):
        self.root = Path(root)
        self.records = deepcopy(records) if records is not None else json.loads(
            (self.root / REGISTER).read_text())
        self.validate()

    def validate(self):
        d = self.records
        if d.get('schema_version') != 'accdsl.p08.authority.v1':
            raise Unsupported('authority schema')
        self.sources = {r['id']: r for r in d['authorities']}
        self.claims = {r['id']: r for r in d['claims']}
        if len(self.sources) != len(d['authorities']) or len(self.claims) != len(d['claims']):
            raise Unsupported('duplicate authority or claim')
        for s in self.sources.values():
            if s['access_status'] != 'inspected_primary':
                continue
            if s.get('kind') != 'primary_standard' or not s.get('inspected_at'):
                raise Unsupported('uninspected or non-primary authority')
            for key in ('retained', 'text'):
                p = Path(s[key]['path'])
                if p.is_absolute() or '..' in p.parts or (self.root / p).is_symlink():
                    raise Unsupported('unsafe source path')
                try:
                    actual = sha256((self.root / p).read_bytes()).hexdigest()
                except OSError as exc:
                    raise Unsupported('missing source') from exc
                if actual != s[key]['sha256']:
                    raise Unsupported('source hash mismatch')
            iso(s['period_start_inclusive']); iso(s['period_start_exclusive'])
        for c in self.claims.values():
            s = self.sources.get(c['authority_id'])
            if not s or s['access_status'] != 'inspected_primary':
                raise Unsupported('claim lacks inspected primary source')
            pages = (self.root / s['text']['path']).read_text().split('\f')
            for a in c['anchors']:
                if type(a['pdf_page']) is not int or not 1 <= a['pdf_page'] <= len(pages):
                    raise Unsupported('invalid anchor page')
                page = normal(pages[a['pdf_page'] - 1])
                if normal(a['quote']) not in page or a['paragraph'] not in s['inspected_paragraphs']:
                    raise Unsupported('unresolvable quote/paragraph')
        if any(c not in self.claims for c in REQUIRED):
            raise Unsupported('missing lifecycle authority')
        if set(d['note_links']) != {'financing_carrying', 'financing_interest', 'financing_equity'}:
            raise Unsupported('note schema')
        for links in d['note_links'].values():
            if not links or any(link not in self.claims for link in links):
                raise Unsupported('unresolved note claim')

    def admit(self, contract):
        # Revalidate so a caller cannot bypass source checks by mutating records.
        self.validate()
        for key in REQUIRED:
            s = self.sources[self.claims[key]['authority_id']]
            if (contract.jurisdiction != s['jurisdiction'] or contract.basis != 'AASB'
                    or contract.tier != s['tier'] or contract.entity_scope != s['entity_scope']):
                raise Unsupported('authority jurisdiction/entity/tier mismatch')
            for year in range(iso(contract.issue_date).year,
                              iso(contract.issue_date).year + contract.years):
                start = date(year, 1, 1)
                if not iso(s['period_start_inclusive']) <= start < iso(s['period_start_exclusive']):
                    raise Unsupported('edition outside reporting-period start')


@dataclass(frozen=True)
class Contract:
    entity: str = 'SyntheticIssuer'
    book: str = 'statutory'
    currency: str = 'AUD'
    functional_currency: str = 'AUD'
    jurisdiction: str = 'AU'
    basis: str = 'AASB'
    tier: str = 'Tier 1'
    entity_scope: str = 'for-profit'
    issue_date: str = '2024-01-01'
    years: int = 2
    principal: str = '100'
    proceeds: str = '100'
    instrument_fair_value: str = '100'
    annual_coupon: str = '5'
    comparable_yield: str = '1/10'
    conversion_shares: int = 10
    conversion_right: str = 'maturity_only_fixed_for_fixed_nonputtable_ordinary'
    measurement: str = 'amortised_cost'
    unsupported_features: tuple = ()

    def validate(self):
        if not self.entity or not self.book or not re.fullmatch('[A-Z]{3}', self.currency):
            raise Unsupported('entity/book/currency required')
        if self.currency != self.functional_currency:
            raise Unsupported('FX unsupported')
        if (type(self.years) is not int or not 1 <= self.years <= 10
                or type(self.conversion_shares) is not int or self.conversion_shares <= 0):
            raise Unsupported('invalid term or shares')
        start = iso(self.issue_date)
        if (start.month, start.day) != (1, 1):
            raise Unsupported('annual calendar periods only')
        if self.conversion_right != 'maturity_only_fixed_for_fixed_nonputtable_ordinary':
            raise Unsupported('unsupported conversion terms')
        if self.measurement != 'amortised_cost' or self.unsupported_features:
            raise Unsupported('fees/tax/options/modifications/default and other features excluded')
        p, proceeds, fair, coupon, rate = map(rational, (
            self.principal, self.proceeds, self.instrument_fair_value,
            self.annual_coupon, self.comparable_yield))
        if p <= 0 or proceeds <= 0 or coupon < 0 or rate < 0 or proceeds != fair:
            raise Unsupported('positive principal/proceeds, fair-value proceeds and nonnegative coupon/yield required')
        liability = sum((coupon / (1 + rate) ** n for n in range(1, self.years + 1)), Fraction(0))
        liability += p / (1 + rate) ** self.years
        if liability > proceeds:
            raise Unsupported('negative residual equity: assumptions need reassessment')
        return liability

    def coupon_dates(self):
        y = iso(self.issue_date).year
        return [date(y + i, 12, 31).isoformat() for i in range(self.years)]


class BondBook:
    def __init__(self, contract, authority=None, opening_cash='20'):
        liability = contract.validate()
        self.authority = authority or AuthorityBook()
        self.authority.admit(contract)
        self.contract = contract
        self.initial_liability = liability
        opening = rational(opening_cash)
        if opening < 0:
            raise Unsupported('negative opening funding')
        self._ledger = {k: Fraction(0) for k in ACCOUNTS}
        self._ledger.update(cash=opening, opening_equity=-opening)
        self._journal = []
        self._used = set()
        self._position = 0
        self._shares = 0
        self._principal = Fraction(0)
        self._events = [('issue', contract.issue_date)]
        for day in contract.coupon_dates():
            self._events.extend([('accrue', day), ('coupon', day)])
        self._events.append(('settle', contract.coupon_dates()[-1]))

    @property
    def state(self):
        return deepcopy({'ledger': self._ledger, 'position': self._position,
                         'shares': self._shares, 'principal_outstanding': self._principal,
                         'journal': self._journal, 'used_event_ids': sorted(self._used)})

    def apply(self, event_id, kind, day):
        if not isinstance(event_id, str) or not event_id.strip() or event_id in self._used:
            raise Unsupported('missing/duplicate event identity')
        iso(day)
        if self._position >= len(self._events):
            raise Unsupported('already settled')
        expected, expected_day = self._events[self._position]
        if day != expected_day or (kind != expected and not (expected == 'settle' and kind in ('redeem', 'convert'))):
            raise Unsupported('out-of-order or conflicting event')
        c = self.contract
        ledger = deepcopy(self._ledger)
        shares, principal = self._shares, self._principal
        postings = {}
        claims = []
        if kind == 'issue':
            postings = {'cash': rational(c.proceeds), 'liability': -self.initial_liability,
                        'conversion_equity': -(rational(c.proceeds) - self.initial_liability)}
            principal = rational(c.principal)
            claims = ['recognition', 'classification', 'split']
        elif kind == 'accrue':
            interest = -ledger['liability'] * rational(c.comparable_yield)
            postings = {'interest_expense': interest, 'liability': -interest}
            claims = ['measurement', 'interest']
        elif kind == 'coupon':
            coupon = rational(c.annual_coupon)
            postings = {'liability': coupon, 'cash': -coupon}
            claims = ['measurement', 'redemption']
        elif kind in ('redeem', 'convert'):
            carrying = -ledger['liability']
            if carrying != rational(c.principal):
                raise Unsupported('maturity liability does not equal principal')
            postings = {'liability': carrying, 'cash' if kind == 'redeem' else 'share_equity': -carrying}
            if kind == 'convert':
                shares += c.conversion_shares
            principal = Fraction(0)
            claims = ['redemption' if kind == 'redeem' else 'conversion']
        else:
            raise Unsupported('unsupported event')
        for account, amount in postings.items():
            ledger[account] += amount
        if sum(postings.values()) or sum(ledger.values()) or ledger['cash'] < 0 or ledger['liability'] > 0:
            raise Unsupported('journal/state/funding invariant')
        # Commit only after all validation, including funding and measurement.
        entry = {'id': event_id, 'kind': kind, 'date': day, 'entity': c.entity,
                 'book': c.book, 'currency': c.currency, 'postings_debit_positive': postings,
                 'claims': claims, 'state_after': deepcopy(ledger)}
        self._ledger, self._shares, self._principal = ledger, shares, principal
        self._journal.append(entry)
        self._used.add(event_id)
        self._position += 1
        return deepcopy(entry)

    def notes(self):
        periods = []
        opening_carrying = Fraction(0)
        for year in range(iso(self.contract.issue_date).year,
                          iso(self.contract.issue_date).year + self.contract.years):
            rows = [x for x in self._journal if x['date'].startswith(str(year))]
            if not rows:
                continue
            def movement(kind, account):
                return sum((x['postings_debit_positive'].get(account, Fraction(0))
                            for x in rows if x['kind'] == kind), Fraction(0))
            issued = -movement('issue', 'liability')
            interest = movement('accrue', 'interest_expense')
            coupons = movement('coupon', 'liability')
            settled = movement('redeem', 'liability') + movement('convert', 'liability')
            closing = -rows[-1]['state_after']['liability']
            if opening_carrying + issued + interest - coupons - settled != closing:
                raise Unsupported('note roll-forward mismatch')
            periods.append({'period_start': f'{year}-01-01', 'period_end': f'{year}-12-31',
                            'opening_liability': opening_carrying, 'issue_liability': issued,
                            'interest_expense': interest, 'coupons': coupons, 'settlement_liability': settled,
                            'closing_liability': closing, 'event_ids': [x['id'] for x in rows]})
            opening_carrying = closing
        return {'periods': periods, 'links': deepcopy(self.authority.records['note_links']),
                'mandatory_disclosure_scope': 'selected carrying amount and interest only; not a complete AASB 7 note',
                'conversion_equity': -self._ledger['conversion_equity'],
                'issued_share_equity': -self._ledger['share_equity'], 'issued_shares': self._shares}


def run_case(contract=None, settlement='redeem', opening_cash='20', authority=None):
    c = contract or Contract()
    book = BondBook(c, authority, opening_cash)
    book.apply('issue', 'issue', c.issue_date)
    for i, day in enumerate(c.coupon_dates(), 1):
        book.apply(f'accrue-{i}', 'accrue', day)
        book.apply(f'coupon-{i}', 'coupon', day)
    book.apply('settlement', settlement, c.coupon_dates()[-1])
    return wire({'contract': vars(c), 'settlement': settlement, 'opening_cash': rational(opening_cash),
                 'initial_liability': book.initial_liability, 'state': book.state, 'notes': book.notes()})


def compare_same_facts(contract=None, authority=None):
    c = contract or Contract()
    facts = wire(vars(c))
    # Hash common economics without changing terms for an unavailable rule set.
    economic = {k: v for k, v in facts.items() if k not in ('basis', 'jurisdiction', 'tier', 'entity_scope', 'book')}
    digest = sha256(json.dumps(economic, sort_keys=True).encode()).hexdigest()
    case = run_case(c, authority=authority)
    rows = [{'standard': 'AASB', 'jurisdiction': 'AU', 'facts_sha256': digest,
             'status': 'supported_bounded', 'initial_liability': case['initial_liability'],
             'initial_equity': str(rational(c.proceeds) - rational(case['initial_liability'])),
             'total_interest': case['state']['ledger']['interest_expense'],
             'claims': list(REQUIRED)}]
    for standard, jurisdiction, missing in [
        ('US GAAP', 'US', 'Applicable ASC 470/815 and ASU 2020-06 text, adoption and exceptions uninspected; official PDF 403.'),
        ('ASBE', 'CN', 'Official CAS 22/37 text, applicable edition and entity transition uninspected; MoF route 502.'),
        ('EU-endorsed IFRS', 'EU', 'Applicable endorsed IAS 32/IFRS 9 text and amendments uninspected; EUR-Lex returned empty 202.')]:
        rows.append({'standard': standard, 'jurisdiction': jurisdiction, 'facts_sha256': digest,
                     'status': 'unresolved', 'initial_liability': None, 'initial_equity': None,
                     'total_interest': None, 'claims': [], 'missing': missing})
    return {'economic_facts': economic, 'rows': rows, 'supported_difference': None,
            'criterion_status': 'incomplete: no second inspected applicable standard',
            'interpretation': 'No numerical difference or equivalence is established; Australian adoption is not universal IFRS authority.'}
