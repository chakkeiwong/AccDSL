"""Inspect four actual concepts, not a generic adapter or schema validator."""
import ast,hashlib,json,re,zipfile
from decimal import Decimal as D
from pathlib import Path
from lxml import etree
U=Path(__file__).resolve().parent;R=U.parents[2];checks={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(U/n).write_text(json.dumps(x,indent=2)+'\n')
b=json.loads((U/'baseline.json').read_text())
for group in ['dependencies','candidate_files','frozen']:
    for p,h in b[group].items():checks[group+':'+p]=sha(R/p)==h
ip='docs/design/cases/apple/interim-2025q1.html';ap='data/accounting-master/taxonomy-reuse-20261007/archive/aapl-20240928_htm.xml'
manifest=json.loads((R/'docs/design/cases/apple/manifest.json').read_text())
checks['interim_receipt']=next(x for x in manifest['documents'] if x['local_path']==ip)['sha256']==sha(R/ip)
dossier=json.loads((R/'data/accounting-master/taxonomy-reuse-20261007/adapter-dossier.json').read_text())
checks['instance_receipt']=dossier['proposed_input']['uri_map']['archive/aapl-20240928_htm.xml']['sha256']==sha(R/ap)
archive_receipt_path=R/'docs/design/cases/apple/continuation-20261007/sources/annual-2024-taxonomy-trusted-v1.receipt.json'
archive_receipt=json.loads(archive_receipt_path.read_text());archive=R/archive_receipt['path']
checks['archive_receipt_hash']=sha(archive)==archive_receipt['sha256']==dossier['proposed_input']['archive_sha256']
with zipfile.ZipFile(archive) as z:
    checks['instance_is_exact_archive_member']=z.read('aapl-20240928_htm.xml')==(R/ap).read_bytes()
renders=json.loads((R/'data/accounting-master/apple-interim-network-20261013/source-renders.json').read_text())
checks['source_render_same_bytes']=renders['source_sha256']==sha(R/ip)
views=[x for x in renders['images'] if x['statement'] in ['balance','equity']]
for x in views:checks['inspected_render:'+x['statement']]=sha(R/x['image'])==x['sha256']
save('source-review.json',{'reviewer':'author-agent; independent acceptance pending','views':[dict(x,inspected=True) for x in views],'type':renders['type'],'review':'Selected comparative balance values, loss parentheses and repeated beginning equity read in both derived views; not browser screenshots.','archive_receipt':str(archive_receipt_path.relative_to(R)),'archive_receipt_sha256':sha(archive_receipt_path)})
receipt=json.loads((U/'source-receipt.json').read_text());checks['decimal_source_receipt']=receipt['exit_code']==0 and receipt['curl_receipt'].startswith('200 ') and sha(R/receipt['path'])==receipt['sha256']
fmtpath='data/accounting-master/arelle-inline-values-20261013/sources/FunctionIxt.py';ft=(R/fmtpath).read_text()
def pattern(path,name):
    tree=ast.parse((R/path).read_text());node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id==name for x in n.targets))
    return re.compile(ast.literal_eval(node.value.args[0]))
tr4=pattern(fmtpath,'numDotDecimalTR4Pattern');canonical=pattern(fmtpath,'numCanonicalizationPattern');decimal=pattern(receipt['path'],'decimalPattern')
checks['registry4_mapping']='4: "http://www.xbrl.org/inlineXBRL/transformation/2020-02-12"' in ft and 'ixtNamespacesByVersion[4]: tr4Functions' in ft and '"num-dot-decimal": numdotdecimalTR4' in ft
parser=lambda:etree.XMLParser(resolve_entities=False,no_network=True,recover=False)
roots={'interim':etree.fromstring((R/ip).read_bytes(),parser()),'annual_instance':etree.fromstring((R/ap).read_bytes(),parser())}
X='http://www.xbrl.org/2003/instance';IX='http://www.xbrl.org/2013/inlineXBRL';GAAP='http://fasb.org/us-gaap/2024';ISO='http://www.xbrl.org/2003/iso4217'
concepts=['Assets','Liabilities','StockholdersEquity','AccumulatedOtherComprehensiveIncomeLossNetOfTax']
def expand(node,value):
    if ':' in value:pre,local=value.split(':',1);return '{'+node.nsmap[pre]+'}'+local
    return '{'+node.nsmap.get(None,'')+'}'+value
def structure(e,root=False):
    text=(e.text or '').strip()
    if e.tag=='{'+X+'}measure':text=expand(e,text)
    attrs={k:v for k,v in e.attrib.items() if not(root and k=='id')}
    return {'tag':e.tag,'attributes':attrs,'text':text,'children':[structure(c) for c in e if isinstance(c.tag,str)]}
def simple_context(c):
    # This task permits only this fully inspected unsegmented instant shape.
    ns={'x':X};entity=c.find('x:entity',ns);period=c.find('x:period',ns)
    return len(c)==2 and entity is not None and len(entity)==1 and entity[0].tag=='{'+X+'}identifier' and period is not None and len(period)==1 and period[0].tag=='{'+X+'}instant'
def occurrence(root,e,source):
    row=e.xpath('ancestor::*[local-name()="tr"][1]')
    return {'source':source,'source_sha256':sha(R/(ip if source=='interim' else ap)),'id':e.get('id'),'xpath':root.getroottree().getpath(e),'attributes':dict(e.attrib),'literal':''.join(e.itertext()),'row_text':' '.join(''.join(row[0].itertext()).split()) if row else None,'line':e.sourceline,'node_xml':etree.tostring(e,encoding='unicode',with_tail=False)}
inventory={};selected={};contexts={};units={}
for source,root in roots.items():
    cs={e.get('id'):e for e in root.iter('{'+X+'}context')};us={e.get('id'):e for e in root.iter('{'+X+'}unit')};contexts[source]=cs;units[source]=us;inventory[source]=[];selected[source]=[]
    for e in root.iter():
        if not isinstance(e.tag,str):continue
        if source=='interim':
            if e.tag!='{'+IX+'}nonFraction':continue
            name=expand(e,e.get('name'))
        else:name=e.tag
        if name not in {'{'+GAAP+'}'+c for c in concepts}:continue
        ctx=cs.get(e.get('contextRef'));assert ctx is not None
        item=occurrence(root,e,source);item['expanded_concept']=name;item['context_structure']=structure(ctx,True);item['selected']=simple_context(ctx) and ctx.findtext('{'+X+'}period/{'+X+'}instant')=='2024-09-28'
        item['disposition']='selected comparative endpoint' if item['selected'] else 'other period or dimensional population; retained in inventory'
        inventory[source].append(item)
        if not item['selected']:continue
        uid=e.get('unitRef');unit=us[uid];item['unit_structure']=structure(unit,True)
        checks[source+':'+e.get('id')+':USD']=len(unit)==1 and unit[0].tag=='{'+X+'}measure' and expand(unit[0],unit[0].text)=='{'+ISO+'}USD'
        checks[source+':'+e.get('id')+':reported_accuracy']=e.get('decimals')=='-6' and e.get('precision') is None
        checks[source+':'+e.get('id')+':nonnull']=e.get('{http://www.w3.org/2001/XMLSchema-instance}nil') not in ['true','1']
        if source=='interim':
            literal=item['literal'];fmt=expand(e,e.get('format'))
            checks[e.get('id')+':exact_transform']=fmt=='{http://www.xbrl.org/inlineXBRL/transformation/2020-02-12}num-dot-decimal'
            checks[e.get('id')+':simple_text']=len(e)==0 and e.get('continuedAt') is None and e.get('escape') is None
            checks[e.get('id')+':transform_pattern']=bool(tr4.match(literal))
            normalized=literal.replace(',','').replace(' ','').replace('\u00a0','');checks[e.get('id')+':decimal_pattern']=bool(decimal.match(normalized));m=canonical.match(normalized);assert m
            canonical_value=(m.group(1) or '0')+(m.group(4) or '')
            checks[e.get('id')+':scale']=e.get('scale')=='6';checks[e.get('id')+':sign']=e.get('sign') in [None,'-']
            value=D(canonical_value)*D(10)**int(e.get('scale'))*(-1 if e.get('sign')=='-' else 1)
            item.update(format_expanded=fmt,canonical_value=canonical_value,reported_amount=str(value),algorithm='Selected inspected TR4 string/pattern steps plus exact Decimal arithmetic; no Arelle execution')
        else:item['reported_amount']=str(D(item['literal']))
        selected[source].append(item)
save('occurrence-inventory.json',{'selection':'four concepts, all contexts inventoried; only unsegmented28September2024 instant selected','sources':inventory})
checks['interim_selected5']=len(selected['interim'])==5;checks['instance_selected5']=len(selected['annual_instance'])==5
for source in roots:checks[source+':unique_selected_ids']=len({e['id'] for e in selected[source]})==len(selected[source])
joins=[]
for item in selected['interim']:
    matches=[a for a in selected['annual_instance'] if all(a[k]==item[k] for k in ['expanded_concept','context_structure','unit_structure','reported_amount']) and a['attributes']['decimals']==item['attributes']['decimals']]
    checks[item['id']+':counterpart']=bool(matches)
    joins.append({'interim_id':item['id'],'annual_counterpart_ids':[a['id'] for a in matches],'reported_amount':item['reported_amount'],'context_ids':[item['attributes']['contextRef'],*[a['attributes']['contextRef'] for a in matches]],'matching_basis':'expanded concept, entire selected unsegmented context structure, expanded unit structure, reported decimals and exact amount; not occurrence identity'})
vals={c:{D(a['reported_amount']) for a in selected['interim'] if a['expanded_concept']=='{'+GAAP+'}'+c} for c in concepts};checks['each_concept_one_reported_amount']=all(len(x)==1 for x in vals.values());v={k:next(iter(x)) for k,x in vals.items()}
checks['accounting_identity_reported']=v['Assets']==v['Liabilities']+v['StockholdersEquity'];checks['signed_loss']=v['AccumulatedOtherComprehensiveIncomeLossNetOfTax']==D('-7172000000')
equity=[a for a in selected['interim'] if a['expanded_concept']=='{'+GAAP+'}StockholdersEquity'];double=sum(D(a['reported_amount']) for a in equity)
checks['repeated_equity_not_additive']=double==D('113900000000') and double!=v['StockholdersEquity']
checks['context_ids_differ']=all(x['context_ids'][0]=='c-18' and set(x['context_ids'][1:])=={'c-21'} for x in joins)
out={'comparison':'cross-filing endpoint comparison, not same-filing extraction round trip','schema_validated':False,'arelle_executed':False,'selected':selected,'joins':joins,'reported_USD':{k:str(x) for k,x in v.items()},'incorrect_sum_repeated_equity_USD':str(double),'accuracy':'decimals=-6 retained; scaled dollar strings do not imply unit-dollar economic precision'}
save('trace.json',out)
annualhtml=R/'docs/design/cases/apple/p02-v1/annual-2024-official.html';t=annualhtml.read_text();save('source-format-repair.json',{'path':str(annualhtml.relative_to(R)),'sha256':sha(annualhtml),'inline_numeric_tags':len(re.findall(r'<ix:nonfraction\b',t,re.I)),'inline_namespace_present':IX in t,'converter_header':'EDGAR Online LLC','disposition':'valid retained converted HTML, unsuitable for planned inline trace; replaced by explicit cross-filing endpoint comparison'})
save('source-code-anchors.json',{'commit':'01f6a4656c2c6551d2f05f31c9d74366d133ee7e','sources':[{'path':fmtpath,'sha256':sha(R/fmtpath),'spans':[[177,177],[194,194],[414,418],[1174,1179],[1433,1433],[1451,1473]]},{'path':receipt['path'],'sha256':receipt['sha256'],'spans':[[140,140]]}],'execution':'static source plus local independent selected arithmetic; no Arelle imports'})
failed=[k for k,x in checks.items() if not x];save('source-arithmetic-checks.json',{'checks':checks,'passed':sum(checks.values()),'failed':failed});print(json.dumps({'passed':sum(checks.values()),'failed':failed,'inventory':{k:len(v) for k,v in inventory.items()},'selected':{k:len(v) for k,v in selected.items()},'joins':joins,'reported_USD':out['reported_USD']}));raise SystemExit(bool(failed))
