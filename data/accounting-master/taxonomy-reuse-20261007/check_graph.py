#!/usr/bin/env python3
"""Independent lxml checks of source graph, namespace/ID targets and instance references."""
import hashlib
import json
import time
from collections import Counter
from pathlib import Path
from lxml import etree

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
start = time.monotonic()
g = json.loads((OUT/'graph-final.json').read_text())
checks = []


def check(label, ok):
    checks.append({'check':label,'passed':bool(ok)})


ns = {'xs':'http://www.w3.org/2001/XMLSchema','xlink':'http://www.w3.org/1999/xlink',
      'xsi':'http://www.w3.org/2001/XMLSchema-instance','xdt':'http://xbrl.org/2005/xbrldt',
      'xml':'http://www.w3.org/XML/1998/namespace','xbrli':'http://www.xbrl.org/2003/instance'}
trees = {}
definitions = set()
for n in g['nodes']:
    p = ROOT/n['path']
    check(n['uri']+' hash',hashlib.sha256(p.read_bytes()).hexdigest()==n['sha256'])
    tree = etree.parse(str(p),etree.XMLParser(no_network=True,resolve_entities=False))
    trees[n['uri']] = tree
    root = tree.getroot()
    check(n['uri']+' namespace',root.get('targetNamespace')==n['target_namespace'])
    attrs = tree.xpath('//@xlink:href | //@xdt:typedDomainRef | //@xsi:noNamespaceSchemaLocation | //xs:import/@schemaLocation | //xs:include/@schemaLocation | //xs:redefine/@schemaLocation',namespaces=ns)
    count = len(attrs)+sum(len(x.split())//2 for x in tree.xpath('//@xsi:schemaLocation',namespaces=ns))
    check(n['uri']+' independent reference denominator',count==sum(e['source']==n['uri'] for e in g['edges']))
    for el in root.findall('{'+ns['xs']+'}element'):
        if el.get('name') and n['target_namespace']:
            definitions.add('{'+n['target_namespace']+'}'+el.get('name'))
for n,e in enumerate(g['edges']):
    target = trees.get(e['resolved_node'])
    check(str(n)+' resolved target',target is not None and e['status']=='resolved')
    if target is None:
        continue
    if e['expected_namespace']:
        check(str(n)+' import/hint namespace',target.getroot().get('targetNamespace')==e['expected_namespace'])
    if e['fragment']:
        hits=target.xpath('//*[@id=$v or @xml:id=$v]',v=e['fragment'],namespaces=ns)
        check(str(n)+' exact fragment exists once',len(hits)==1)
inst = trees['archive/aapl-20240928_htm.xml']
contexts = {x.get('id') for x in inst.xpath('/xbrli:xbrl/xbrli:context',namespaces=ns)}
units = {x.get('id') for x in inst.xpath('/xbrli:xbrl/xbrli:unit',namespaces=ns)}
facts = inst.xpath('//*[@contextRef]')
for n,f in enumerate(facts):
    check('instance fact '+str(n)+' declared concept',f.tag in definitions)
    check('instance fact '+str(n)+' context target',f.get('contextRef') in contexts)
    if f.get('unitRef'):
        check('instance fact '+str(n)+' unit target',f.get('unitRef') in units)
check('no source/traversal errors or unresolved edges',not g['errors'] and not g['frontier'])
result={'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),
        'instance_facts':len(facts),'contexts':len(contexts),'units':len(units),
        'checks':checks,'wall_seconds':time.monotonic()-start,
        'limits':'Reference, declaration and identity checks only; no XML Schema/XBRL/full accounting validation or runtime compatibility claim.'}
(OUT/'graph-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:result[k] for k in ['passed','failed','instance_facts','contexts','units','wall_seconds']})
assert result['failed']==0,[c for c in checks if not c['passed']]
