"""Source-only inspection and constructed arithmetic; never imports Arelle."""
import ast
import hashlib
import json
from decimal import Decimal as D, ROUND_HALF_EVEN
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
checks = {}
findings = []
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, data):
    (U / name).write_text(json.dumps(data, indent=2) + '\n')
def method(file, owner, name):
    p = U / 'sources' / file
    tree = ast.parse(p.read_text())
    scope = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == owner).body if owner else tree.body
    node = next(n for n in scope if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
    lines = p.read_text().splitlines()
    text = '\n'.join(lines[node.lineno-1:node.end_lineno])
    return node, text, {'file':str(p.relative_to(R)), 'sha256':sha(p), 'symbol':(owner+'.' if owner else '')+name, 'lines':[node.lineno,node.end_lineno]}
def finding(file, owner, name, verdict, needles):
    node, text, anchor = method(file, owner, name)
    for i, needle in enumerate(needles):
        checks[anchor['symbol']+':'+str(i)] = needle in text
    findings.append(dict(anchor, finding=verdict))
    return node,text

for entry in json.loads((U/'source-receipts.json').read_text()):
    checks['source:'+entry['path']] = entry['exit_code']==0 and entry['curl_receipt'].startswith('200 ') and sha(R/entry['path'])==entry['sha256']
    checks['pin:'+entry['path']] = '/01f6a4656c2c6551d2f05f31c9d74366d133ee7e/' in entry['url']
checks['retained_source_matches_pin'] = (U/'sources/ModelInstanceObject.py').read_bytes()==(R/'docs/design/research/software/Arelle_Arelle-arelle_ModelInstanceObject.py').read_bytes()
M='ModelInstanceObject.py'; V='ValidateDuplicateFacts.py'; C='ValidateXbrlCalcs.py'
finding(M,'ModelFact','value','Base value can replace empty text with concept default/fixed; inline subclasses require their own transformation analysis.',['self.textValue','self.concept.default','self.concept.fixed'])
finding(M,'ModelFact','effectiveValue','Display view rounds and formats; nil and errors can become strings. It is not a lossless typed/lexical record.',['Effective value for views','roundValue(val, self.precision, dec)','Locale.format','return "(nil)"','return str(ex)'])
finding(M,'ModelFact','vEqValue','Numeric conversion uses binary float; distinct exact integers can collide.',['return float(self.value)'])
node,text=finding(M,'ModelFact','isVEqualTo','No qname comparison in this method; nil branch precedes context equality. Non-nil numeric path depends on context/unit, interval flag, calculation mode and rounding arguments.',['if self.isNil:', 'return other.isNil','if not self.context.isEqualTo(other.context):','numericIntervalConsistency','ValidateCalcsMode.XBRL_v2_1_INFER_PRECISION','roundValue(self.value, precision=p, decimals=d)'])
checks['v_equality_no_concept_comparison'] = '.qname' not in text
checks['nil_branch_precedes_context_comparison'] = text.index('return other.isNil') < text.index('if not self.context.isEqualTo')
finding(M,'ModelFact','isDuplicateOf','Item path tests qname/parent/context/unit, not item value. Tuple child path is different and compares matching-qname child values.',['self == other','self.qname != other.qname','dimensionalAspectModel=False','child1.isVEqualTo'])
finding(V,None,'getAspectEqualFacts','Hash buckets undergo actual qname/context/unit comparison; language is lowercased for OIM text fact types when useLang is true.',['fact.qname','(fact.xmlLang or "").lower()','fact.concept.type.isOimTextFactType','fact.context.isEqualTo(context)','fact.unit.isEqualTo(unit)'])
finding(V,None,'getHashEquivalentFactGroups','Nil or validated values with context/concept/type are hash grouped; others receive singleton buckets. Singleton bucketing is not validation or guaranteed downstream preservation.',['f.isNil','>= XmlValidateConst.VALID','f.context is not None','f.concept.type is not None','hashDict[object()].append(f)'])
finding(V,None,'getFactValueEqualityKey','After nil/NaN/language/DateTime cases, key uses fact.value, not general xValue equality.',['xValue is None or fact.isNil','FactValueEqualityType.LANGUAGE','xValue.dateOnly','return FactValueEqualityType.DEFAULT, (fact.value,)'])
finding(V,'DuplicateFactSet','areAllComplete','Classification combines raw decimals equality and the value-key comparison.',['self.areAllDecimalsEqual and self.areAllValueEqual'])
finding(V,'DuplicateFactSet','deduplicateCompleteSubsets','Reduction uses decimals and typed xValue, retaining the first item per key; it can merge lexical forms that areAllComplete distinguishes.',['key = (fact.decimals, xValue)','seenKeys.add(key)','results.append(fact)'])
finding(V,'DuplicateFactSet','getDecimals','If fact.decimals is absent this helper returns None, not inferredPrecision; numeric consistency paths assert a decimals result.',['None if fact.decimals is None else inferredDecimals(fact)'])
finding(V,'DuplicateFactSet','getRange','Uses default non-truncating rangeValue and discards inclusion flags.',['lower, upper, __, __ = rangeValue(fact.xValue, self.getDecimals(fact))'])
finding(C,None,'rangeValue','Finite decimals d with default truncate=False gives inclusive bounds v +/- 0.5*10**(-d); truncation has different endpoint rules.',['truncate: bool = False','dd /= TWO','return (vDecimal - dd, vDecimal + dd, True, True)','return (vDecimal, vDecimal + dd, True, False)'])
finding(V,'DuplicateFactSet','areWithinRoundingError','All-set numeric consistency rejects unequal typed values at identical inferred decimals and requires a common interval intersection.',['if value != decimalValues[decimals]:','return False','if minUpper < maxLower:'])
finding(V,'DuplicateFactSet','deduplicateConsistentPairs','Pair reduction can discard a coarse occurrence agreeing separately with mutually inconsistent precise occurrences. It does not establish all-set consistency.',['facts = self.deduplicateCompleteSubsets()','if lowerB <= upperA and upperB >= lowerA:','results.remove(factA)'])
finding(V,'DuplicateFactSet','deduplicateConsistentSet','Fully consistent numeric sets select highest inferred decimals; inconsistent sets fall back to complete-subset reduction plus message.',['if not self.areAllConsistent:','"Set has inconsistent facts"','if decimals > maxDecimals:'])
finding(V,None,'getDeduplicatedFacts','Actual entry point builds aspect-equal sets and dispatches explicitly among three reduction methods.',['getDuplicateFactSets(modelXbrl.facts, includeSingles=True)','deduplicateCompleteSubsets','deduplicateConsistentPairs','deduplicateConsistentSet'])
finding(V,None,'saveDeduplicatedInstance','Export removes omitted fact nodes from the original model tree before saving.',['duplicateFacts = set(modelXbrl.facts) - deduplicatedFacts','parent.remove(fact)','modelXbrl.saveInstance'])
caller=R/'data/accounting-master/taxonomy-reuse-20261007/sources/arelle-cntlrcmdline-trusted.body'
lines=caller.read_text().splitlines(); span='\n'.join(lines[2258:2285])
checks['caller_default_complete'] = 'DeduplicationType.COMPLETE' in span
checks['caller_warns_mutation'] = 'leaves the model in an undefined state' in span
checks['caller_rejects_keep_open'] = 'if options.keepOpen:' in span and 'success = False' in span
findings.append({'file':str(caller.relative_to(R)),'sha256':sha(caller),'lines':[2259,2285],'symbol':'CntlrCmdLine.run export branch','finding':'saveDeduplicatedInstance defaults to COMPLETE when reduction type absent; controller warns mutation leaves model undefined and makes keepOpen unsuccessful.'})

# These calculations reproduce no library objects or execution. They are
# independent exact witnesses for conclusions read in the source above.
def bounds(value, decimals):
    half=D('0.5') * D(10) ** (-decimals)
    return (D(value)-half,D(value)+half)
def overlaps(a,b):
    return max(a[0],b[0]) <= min(a[1],b[1])
checks['float_collision_distinct_exact_integers'] = D('9007199254740992')!=D('9007199254740993') and float('9007199254740992')==float('9007199254740993')
checks['lexical_forms_differ'] = '1' != '1.0'
checks['typed_values_equal'] = D('1') == D('1.0')
checks['typed_reduction_key_equal'] = ('0',D('1'))==('0',D('1.0'))
checks['default_rounding_same'] = D('1').quantize(D('1'),rounding=ROUND_HALF_EVEN)==D('1.0').quantize(D('1'),rounding=ROUND_HALF_EVEN)
checks['touching_default_bounds'] = bounds('0',0)==(D('-.5'),D('.5')) and bounds('1',0)==(D('.5'),D('1.5')) and overlaps(bounds('0',0),bounds('1',0))
checks['same_decimals_values_different'] = D('0') != D('1')
a,b,c = bounds('100',0),bounds('99.6',1),bounds('100.4',1)
checks['coarse_overlaps_both'] = overlaps(a,b) and overlaps(a,c)
checks['precise_values_disagree'] = not overlaps(b,c) and D('99.6')!=D('100.4')
checks['three_way_intersection_empty'] = max(a[0],b[0],c[0])>min(a[1],b[1],c[1])
checks['complete_duplicate_occurrences_remain_distinct'] = ('doc-sha','/fact[1]')!=('doc-sha','/fact[2]')
checks['nil_not_numeric_zero'] = None != D('0')
cases=[
 {'case':'binary float collision','inputs':['9007199254740992','9007199254740993'],'exact_values_equal':False,'binary_float_values_equal':True},
 {'case':'lexical versus typed reduction key','values':['1','1.0'],'decimals':['0','0'],'key_strings_equal':False,'typed_decimals_keys_equal':True,'source_consequence':'areAllComplete false; complete-subset reduction retains first, assuming valid ordinary numeric facts with identical aspects'},
 {'case':'touching intervals','values':['0','1'],'decimals':[0,0],'intervals':[['-0.5','0.5'],['0.5','1.5']],'overlap':True,'source_consequence':'isVEqualTo numericIntervalConsistency=True admits overlap under required aspects; areWithinRoundingError rejects same-decimals unequal values'},
 {'case':'pairwise consistency is not set consistency','values':['100','99.6','100.4'],'decimals':[0,1,1],'intervals':[[str(x) for x in pair] for pair in (a,b,c)],'source_consequence':'coarse fact can be removed in pair mode; two disagreeing precise facts remain; set mode reports inconsistent set'},
 {'case':'occurrence identity','occurrences':['doc-sha:/fact[1]','doc-sha:/fact[2]'],'identical_reported_values_allowed':True,'source_consequence':'even a consistent reduction loses source-location multiplicity unless membership is separately retained'}]
save('source-findings.json',{'commit':'01f6a4656c2c6551d2f05f31c9d74366d133ee7e','mode':'static source inspection, no Arelle import or execution','findings':findings})
save('constructed-cases.json',{'scope':'hypothetical valid ordinary numeric facts sharing concept/context/unit unless explicitly stated; not issuer data and not runtime tests','cases':cases})
baseline=json.loads((U/'baseline.json').read_text())
for group in ['candidate_files','frozen','dependencies']:
    for path,digest in baseline[group].items():
        checks[group+':'+path]=sha(R/path)==digest
failed=[k for k,v in checks.items() if not v]
save('source-arithmetic-checks.json',{'checks':checks,'passed':sum(checks.values()),'failed':failed})
print(json.dumps({'passed':sum(checks.values()),'failed':failed,'findings':len(findings),'constructed_cases':len(cases),'arelle_executed':False}))
raise SystemExit(bool(failed))
