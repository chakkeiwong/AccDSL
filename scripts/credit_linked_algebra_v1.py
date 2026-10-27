"""Bounded exact rational Laurent expressions at a specified positive root.

Reduction modulo z**365-a certifies zero; nonzero does not certify inequality.
This is a scalar helper, not a general algebraic-number or monetary type.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha256
import json

MAX_BITS = 1024
MAX_TERMS = 365
MAX_POWER = 7305
CONTEXT_KEYS = {'entity','book','currency','unit','rule','contract','calendar'}


class Refusal(Exception):
    def __init__(self, reason, status='rejected'):
        self.reason, self.status = reason, status
        super().__init__(reason)


def need(condition, reason, status='rejected'):
    if not condition:
        raise Refusal(reason, status)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


def rational(value):
    need(type(value) in (int, str, Q), 'rational_encoding')
    if type(value) is str:
        need(len(value) <= 640, 'coefficient_budget', 'unsupported')
        try:
            result = Q(value)
        except (ValueError, ZeroDivisionError):
            raise Refusal('rational_encoding')
        need(str(result) == value, 'rational_encoding')
    else:
        result = Q(value)
    need(max(abs(result.numerator).bit_length(), result.denominator.bit_length()) <= MAX_BITS,
         'coefficient_budget', 'unsupported')
    return result


@dataclass(frozen=True)
class Root:
    context: tuple
    rate: Q

    def __post_init__(self):
        need(type(self.context) is tuple and len(self.context) == len(CONTEXT_KEYS), 'root_context')
        need(all(type(p) is tuple and len(p) == 2 for p in self.context), 'root_context')
        need({p[0] for p in self.context} == CONTEXT_KEYS, 'root_context')
        need(all(type(v) is str and 0 < len(v) <= 1024 for _, v in self.context), 'root_context')
        need(tuple(sorted(self.context)) == self.context, 'root_context_order')
        object.__setattr__(self, 'rate', rational(self.rate))
        need(self.rate > -1, 'positive_root_domain')
        rational(1 + self.rate)

    @classmethod
    def create(cls, context, rate):
        need(type(context) is dict and set(context) == CONTEXT_KEYS, 'root_context')
        return cls(tuple(sorted(context.items())), rational(rate))

    @property
    def base(self):
        return 1 + self.rate

    def wire(self):
        return {'profile':'CreditPositiveDayRoot/1', 'context':dict(self.context),
                'rate':str(self.rate), 'degree':365, 'base':str(self.base),
                'root_selection':'unique_positive', 'zero_rate_special_case':self.rate == 0}

    @property
    def identity(self):
        return digest(self.wire())

    def value(self, value):
        q = rational(value)
        return Expr(self, ((0,q),) if q else ())

    def power(self, exponent):
        need(type(exponent) is int, 'power_encoding')
        need(abs(exponent) <= MAX_POWER, 'power_budget', 'unsupported')
        q, s = divmod(exponent, 365)
        if self.rate == 0:
            return self.value(1)
        return Expr(self, ((s, rational(self.base ** q)),))


@dataclass(frozen=True)
class Expr:
    root: Root
    terms: tuple

    def __post_init__(self):
        need(type(self.root) is Root and type(self.terms) is tuple, 'expression_shape')
        need(len(self.terms) <= MAX_TERMS, 'term_budget', 'unsupported')
        last = -1
        for term in self.terms:
            need(type(term) is tuple and len(term) == 2, 'term_shape')
            p, q = term
            need(type(p) is int and last < p < 365, 'canonical_power_order')
            need(type(q) is Q and q != 0, 'canonical_coefficient')
            rational(q)
            need(self.root.rate != 0 or p == 0, 'zero_rate_canonical')
            last = p

    @classmethod
    def normalized(cls, root, terms):
        need(type(terms) is dict, 'term_mapping')
        need(len(terms) <= MAX_TERMS, 'term_budget', 'unsupported')
        out = {}
        for exponent, coefficient in terms.items():
            power = root.power(exponent)
            coefficient = rational(coefficient)
            for p, q in power.terms:
                out[p] = out.get(p, Q(0)) + coefficient * q
        return cls(root, tuple((p,rational(q)) for p,q in sorted(out.items()) if q))

    def coerce(self, other):
        if type(other) is Expr:
            need(self.root == other.root, 'mixed_root_context_or_rate')
            return other
        return self.root.value(other)

    def __add__(self, other):
        other = self.coerce(other); result = dict(self.terms)
        for p, q in other.terms:
            result[p] = result.get(p, Q(0)) + q
        return Expr(self.root, tuple((p,rational(q)) for p,q in sorted(result.items()) if q))

    __radd__ = __add__

    def __neg__(self):
        return Expr(self.root, tuple((p,-q) for p,q in self.terms))

    def __sub__(self, other):
        return self + -self.coerce(other)

    def __rsub__(self, other):
        return self.coerce(other) + -self

    def __mul__(self, other):
        other = self.coerce(other); out = {}
        for p, c in self.terms:
            for s, d in other.terms:
                quotient, remainder = divmod(p+s, 365)
                out[remainder] = out.get(remainder, Q(0)) + c*d*self.root.base**quotient
        return Expr(self.root, tuple((p,rational(q)) for p,q in sorted(out.items()) if q))

    __rmul__ = __mul__

    def __truediv__(self, other):
        need(type(other) is not Expr, 'polynomial_division_unsupported', 'unsupported')
        q = rational(other); need(q != 0, 'division_by_zero')
        return self * rational(1/q)

    def shift(self, exponent):
        return self * self.root.power(exponent)

    @property
    def zero(self):
        return not self.terms

    def equality_certificate(self, other):
        return 'certified_equal' if (self-other).zero else 'not_certified'

    def rational_projection(self):
        if not self.terms:
            return Q(0)
        if len(self.terms) == 1 and self.terms[0][0] == 0:
            return self.terms[0][1]
        raise Refusal('rational_projection_not_certified', 'unsupported')

    def wire(self):
        return {'root_sha256':self.root.identity,
                'terms':[{'power':p,'coefficient':str(q)} for p,q in self.terms]}

    @classmethod
    def from_wire(cls, root, value):
        need(type(value) is dict and set(value) == {'root_sha256','terms'}, 'expression_wire_shape')
        need(value['root_sha256'] == root.identity, 'expression_root_binding')
        rows = value['terms']
        need(type(rows) is list, 'terms_encoding')
        need(len(rows) <= MAX_TERMS, 'term_budget', 'unsupported')
        out = []
        for row in rows:
            need(type(row) is dict and set(row) == {'power','coefficient'}, 'term_wire_shape')
            need(type(row['coefficient']) is str, 'coefficient_wire_encoding')
            out.append((row['power'], rational(row['coefficient'])))
        return cls(root, tuple(out))
