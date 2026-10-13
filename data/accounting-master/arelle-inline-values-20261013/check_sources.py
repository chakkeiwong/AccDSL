"""Static source evidence and exact constructed calculations; no Arelle import."""
import ast,hashlib,json,re
from decimal import Decimal as D
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2];checks={};findings=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):(U/name).write_text(json.dumps(obj,indent=2)+'\n')
def inspect(path,owner,name,verdict,needles):
    p=R/path;tree=ast.parse(p.read_text())
    scope=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==owner).body if owner else ast.walk(tree)
    node=next(n for n in scope if isinstance(n,ast.FunctionDef) and n.name==name)
    text='\n'.join(p.read_text().splitlines()[node.lineno-1:node.end_lineno]);symbol=(owner+'.' if owner else '')+name
    for i,needle in enumerate(needles):checks[symbol+':'+str(i)]=needle in text
    findings.append({'file':path,'sha256':sha(p),'symbol':symbol,'lines':[node.lineno,node.end_lineno],'finding':verdict})
    return text
for e in json.loads((U/'source-receipts.json').read_text()):
    checks['source:'+e['path']]=e['exit_code']==0 and e['curl_receipt'].startswith('200 ') and sha(R/e['path'])==e['sha256']
    checks['pin:'+e['path']]='/01f6a4656c2c6551d2f05f31c9d74366d133ee7e/' in e['url']
M='data/accounting-master/arelle-fact-identity-20261013/sources/ModelInstanceObject.py'
X=str((U/'sources/XmlUtil.py').relative_to(R));F=str((U/'sources/FunctionIxt.py').relative_to(R));V=str((U/'sources/XhtmlValidate.py').relative_to(R))
raw=inspect(M,'ModelInlineValueObject','rawValue','Assembled text reading excludes inline excluded text, follows nonNumeric continuations, supports escape/URI handling, and collapses whitespace if format exists. Not original bytes.',['XmlUtil.innerText','ixExclude=','ixContinuation=(self.elementQname == XbrlConst.qnIXbrl11NonNumeric)','strip = False','raw = collapseWhitespace(raw)'])
value=inspect(M,'ModelInlineValueObject','value','Cached reading; on first access marks unvalidated, dispatches registry/custom transform, then (for non-nil ordinary numeric path) Decimal conversion, scale and sign. Not a validation verdict.',['return self._ixValue','self.xValid = UNVALIDATED','v = self.rawValue','FunctionIxt.ixtNamespaceFunctions[f.namespaceURI][f.localName](v)','self.modelXbrl.modelManager.customTransforms[f](v)','if self.isNil:','negate = -1 if self.sign else 1','num = Decimal(v)','num *= 10 ** Decimal(scale)','num *= negate','self.setInvalid()'])
checks['transform_before_scale']=value.index('FunctionIxt.ixtNamespaceFunctions[f.namespaceURI][f.localName](v)')<value.index('num *= 10 ** Decimal(scale)')
checks['scale_before_sign']=value.index('num *= 10 ** Decimal(scale)')<value.index('num *= negate')
checks['nil_bypasses_numeric_branch']=value.index('if self.isNil:')<value.index('negate = -1')
inspect(M,'ModelInlineValueObject','textValue','Delegates to transformed value; not a raw text property.',['return self.value'])
inspect(M,'ModelInlineValueObject','stringValue','Delegates to transformed value; not raw descendant text.',['return self.value'])
inspect(M,'ModelInlineValueObject','setInvalid','Invalid transformation state includes sentinel value, INVALID and xValue None.',['self._ixValue = ModelValue.INVALIDixVALUE','self.xValid = INVALID','self.xValue = None'])
inspect(X,None,'innerText','Joins yielded fragments; catches AttributeError/TypeError and returns empty string. Empty output alone does not explain success or failure.',['"".join','except (AttributeError, TypeError):','return ""'])
inspect(X,None,'innerTextNodes','Excludes inline exclude children but preserves tail text; follows loader-attached continuation links, not the continuedAt attribute directly.',['child.localName == "exclude"','if child.tail:','getattr(element, "_continuationElement", None)','nested elements don\'t participate in continuation chain'])
inspect(X,None,'collapseWhitespace','Collapses only the inspected XML whitespace pattern, then strips spaces.',['_collapseWhitespacePattern.sub(" ", s).strip(" ")'])
inspect(X,None,'escapedNode','May rewrite URI attributes in generated markup; object codebase path can mutate the parsed element. Neither escaped markup nor tree serialization replaces original bytes.',['sorted(elt.items()','resolveHtmlUri','elt.set("codebase"'])
inspect(F,None,'numdotdecimal','The selected 2011 registry function accepts its declared pattern and removes comma/space/NBSP.',['numDotDecimalPattern.match(arg)','arg.replace(",", "").replace(" ", "").replace("\\u00A0", "")'])
source=(R/F).read_text();tree=ast.parse(source)
patternnode=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='numDotDecimalPattern' for t in n.targets))
pattern=ast.literal_eval(patternnode.value.args[0]);checks['constructed_literal_matches_selected_pattern']=re.match(pattern,'1,234') is not None
checks['registry2011_mapping']='2: "http://www.xbrl.org/inlineXBRL/transformation/2011-07-31"' in source and 'ixtNamespacesByVersion[2]: tr2Functions' in source
checks['function_in_registry2']='"numdotdecimal": numdotdecimal' in source[source.index('tr2Functions ='):source.index('tr3Functions =')]
findings.append({'file':F,'sha256':sha(R/F),'symbol':'2011 registry and numeric pattern','lines':[176,176],'additional_spans':[[1270,1301],[1451,1473]],'finding':'Constructed example selects exact2011 namespace and numdotdecimal function; other registries and custom transforms are not assumed equivalent.'})
inspect(V,None,'xhtmlValidate','Delegates inline schema checking to XmlValidate.lxmlSchemaValidate. This static inquiry has not performed that validation.',['XmlValidate.lxmlSchemaValidate(elt.modelDocument, inlineSchema)'])
L='docs/design/proposal/methods/preparation-20261005-v1/03-adapters/sources/upstream/arelle/arelle__ModelDocument.py'
dossier=json.loads((R/'data/accounting-master/taxonomy-reuse-20261007/adapter-dossier.json').read_text())
anchors=[v for v in dossier['source_anchors'].values() if v.get('path')==L]
checks['retained_loader_bound']=dossier['code_commit']=='01f6a4656c2c6551d2f05f31c9d74366d133ee7e' and any(v['sha256']==sha(R/L) for v in anchors)
inspect(L,None,'locateContinuation','Attaches known continuation elements, records missing/wrong target/cycle diagnostics, and breaks nested chains. Partial returned text does not prove a complete chain.',['contAt = element.get("continuedAt")','continuationMissing','continuationCycle','element._continuationElement = contElt','del chain[0]._continuationElement'])
literal='1,234';normal=literal.replace(',','');scaled=D(normal)*D(10)**D('-3');signed=-scaled;twice=-signed*D(10)**D('-3')
checks['normalize_1234']=normal=='1234';checks['scale_once']=scaled==D('1.234');checks['sign_once']=signed==D('-1.234');checks['double_application_wrong']=twice==D('0.001234') and twice!=signed
checks['whitespace_collapse_loses_spelling']=re.sub(r'[ \t\r\n]+',' ','  1,234\n ').strip(' ')==literal
checks['assembly_with_known_continuation']=''.join(['A','B','C'])=='ABC'
checks['incomplete_nonempty_text']=''.join(['A','B'])=='AB' and 'AB'!='ABC'
checks['exclusion_not_original_document']='ABC'!='AXBC'
save('constructed-cases.json',{'mode':'independent source-derived arithmetic/text examples; no Arelle objects or runtime behavior executed','numeric':{'format_namespace':'http://www.xbrl.org/inlineXBRL/transformation/2011-07-31','format_name':'numdotdecimal','literal':literal,'normalized':normal,'scale':'-3','sign':'-','value':str(signed),'incorrect_reapplication':str(twice)},'text':{'source_fragments':'A; excluded child X; child tail B; known continuation C','assembled':'ABC','without_known_continuation':'AB','prerequisite':'Hypothetical unescaped inline1.1 nonNumeric with validated/located continuation; no claim of XML validation or executed Arelle behavior'}})
save('source-findings.json',{'commit':dossier['code_commit'],'findings':findings,'arelle_executed':False})
b=json.loads((U/'baseline.json').read_text())
for group in ['candidate_files','dependencies','frozen']:
    for p,h in b[group].items():checks[group+':'+p]=sha(R/p)==h
failed=[k for k,v in checks.items() if not v];save('source-arithmetic-checks.json',{'checks':checks,'passed':sum(checks.values()),'failed':failed});print(json.dumps({'passed':sum(checks.values()),'failed':failed,'findings':len(findings),'arelle_executed':False}));raise SystemExit(bool(failed))
