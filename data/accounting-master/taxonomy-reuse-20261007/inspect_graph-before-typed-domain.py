#!/usr/bin/env python3
"""Inventory actual XML dependency edges, retaining the unresolved frontier."""
import argparse
import hashlib
import json
import posixpath
import time
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urldefrag, urljoin, unquote
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--stage', required=True)
args = parser.parse_args()
start = time.monotonic()
XSD = 'http://www.w3.org/2001/XMLSchema'
XLINK = 'http://www.w3.org/1999/xlink'
XML = 'http://www.w3.org/XML/1998/namespace'
archive = ROOT/'docs/design/cases/apple/continuation-20261007/sources/annual-2024-taxonomy-trusted-v1.zip'
nodes, elements, aliases, errors = {}, {}, {}, []


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def add(uri, path, receipt=None, declared_namespace=None):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        errors.append({'uri':uri,'error':'XML parse: '+str(exc)})
        return
    ns = root.get('targetNamespace')
    if declared_namespace is not None and (root.tag != '{'+XSD+'}schema' or ns != declared_namespace):
        errors.append({'uri':uri,'error':'wrong declared namespace/schema kind','expected':declared_namespace,'actual':ns})
        return
    ids = [x.get('id') or x.get('{'+XML+'}id') for x in root.iter() if x.get('id') or x.get('{'+XML+'}id')]
    if len(ids) != len(set(ids)):
        errors.append({'uri':uri,'error':'duplicate XML IDs'})
    nodes[uri] = {'uri':uri,'path':str(path.relative_to(ROOT)),'sha256':sha(path),'root_tag':root.tag,
                  'target_namespace':ns,'receipt':receipt,'id_count':len(ids)}
    elements[uri] = (root, set(ids))
    aliases[uri] = uri


(OUT/'archive').mkdir(exist_ok=True)
with zipfile.ZipFile(archive) as z:
    for name in z.namelist():
        assert Path(name).name == name
        p = OUT/'archive'/name
        if p.exists():
            assert p.read_bytes() == z.read(name)
        else:
            p.write_bytes(z.read(name))
        add('archive/'+name,p)
receipts = []
for p in sorted((OUT/'sources').glob('*.receipt.json')):
    r = json.loads(p.read_text());receipts.append(r)
    if r['exit_code'] != 0 or r['http_status'] != 200:
        continue
    body = ROOT/r['body'];assert sha(body)==r['sha256']
    if r['request'].get('role') == 'terms':
        continue
    uri = r['effective_url']
    add(uri,body,str(p.relative_to(ROOT)),r['request'].get('expected_namespace'))
    if uri in nodes:
        aliases[r['request']['url']] = uri
        # Explicit same-resource alternate retrieval is declared in its queue.
        if r['request'].get('alternate_for'):
            aliases[r['request']['alternate_for']] = uri


def resolve(base, href):
    if base.startswith('archive/'):
        if href.startswith(('http://','https://')):
            return href
        file, frag = urldefrag(href)
        target = posixpath.normpath(posixpath.join(posixpath.dirname(base),file)) if file else base
        return target + ('#'+frag if frag else '')
    return urljoin(base,href)


edges = []
for uri,(root, ids) in elements.items():
    def visit(el, base, indices):
        base = resolve(base,el.get('{'+XML+'}base')) if el.get('{'+XML+'}base') else base
        local = el.tag.split('}')[-1]
        rawrefs = []
        if el.tag in ['{'+XSD+'}import','{'+XSD+'}include','{'+XSD+'}redefine']:
            if el.get('schemaLocation'):
                rawrefs.append(('schemaLocation',el.get('schemaLocation'),el.get('namespace')))
            elif el.tag == '{'+XSD+'}import':
                errors.append({'uri':uri,'error':'import without location','namespace':el.get('namespace')})
        if el.get('{'+XLINK+'}href'):
            rawrefs.append(('xlink:href',el.get('{'+XLINK+'}href'),None))
        if el.get('{'+XML+'}schemaLocation'):
            errors.append({'uri':uri,'error':'unexpected xml:schemaLocation'})
        # xsi:schemaLocation can provide additional source hints; retain all pairs.
        hints = el.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation')
        if hints:
            tokens = hints.split()
            if len(tokens)%2:
                errors.append({'uri':uri,'error':'odd xsi:schemaLocation token count'})
            for n in range(0,len(tokens)-1,2):
                rawrefs.append(('xsi:schemaLocation',tokens[n+1],tokens[n]))
        for attr,href,expected in rawrefs:
            resolved = resolve(base,href)
            resource, fragment = urldefrag(resolved)
            target = aliases.get(resource)
            status = 'unresolved_resource'
            if target:
                status = 'resolved'
                if expected and nodes[target]['target_namespace'] != expected:
                    status = 'namespace_mismatch'
                elif fragment and unquote(fragment) not in elements[target][1]:
                    status = 'unsupported_fragment' if '(' in fragment else 'missing_fragment_id'
            edges.append({'source':uri,'element_path':indices,'element':local,'attribute':attr,
                          'declared_reference':href,'resolved_reference':resolved,'target_resource':resource,
                          'expected_namespace':expected,'fragment':fragment or None,'resolved_node':target,'status':status})
        for n,child in enumerate(el):
            visit(child,base,indices+[n])
    visit(root,uri,[])
front = defaultdict(list)
for e in edges:
    if e['status'] != 'resolved':
        front[e['target_resource']].append(e)
frontier = [{'uri':uri,'edge_count':len(es),'statuses':sorted(set(e['status'] for e in es)),
             'expected_namespaces':sorted(set(e['expected_namespace'] for e in es if e['expected_namespace'])),
             'first_declared_at':{'source':es[0]['source'],'element_path':es[0]['element_path'],'attribute':es[0]['attribute']}}
            for uri,es in sorted(front.items())]
out={'archive':str(archive.relative_to(ROOT)),'archive_sha256':sha(archive),'nodes':list(nodes.values()),'aliases':aliases,
     'edges':edges,'frontier':frontier,'errors':errors,
     'summary':{'nodes':len(nodes),'external_nodes':sum(not u.startswith('archive/') for u in nodes),
                'edges':len(edges),'statuses':dict(Counter(e['status'] for e in edges)),'frontier_resources':len(frontier),'errors':len(errors)},
     'traversal':'xs import/include/redefine, all xlink href attributes, xsi schemaLocation hints; inherited xml:base; URL resolution, target namespace and plain fragment IDs checked',
     'limits':'Static discovery only, not XML Schema/XBRL validity, label/reference completeness, arithmetic, accounting, publication vintage or distribution permission.',
     'wall_seconds':time.monotonic()-start}
(OUT/('graph-'+args.stage+'.json')).write_text(json.dumps(out,indent=2)+'\n')
queue=[]
for f in frontier:
    if f['statuses'] == ['unresolved_resource'] and f['uri'].startswith(('http://','https://')):
        ns=f['expected_namespaces']
        assert len(ns)<=1, f
        row={'id':'dep-'+hashlib.sha256(f['uri'].encode()).hexdigest()[:12],
             'url':f['uri'],'discovered_from':f['first_declared_at'],'declared_uri':f['uri']}
        if ns:row['expected_namespace']=ns[0]
        queue.append(row)
(OUT/('queue-'+args.stage+'.json')).write_text(json.dumps(queue,indent=2)+'\n')
print(out['summary'])
print('frontier',[f['uri'] for f in frontier])
