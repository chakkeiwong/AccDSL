"""Local exact token/LCS audit; never loads pylcs or acquired build code."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import unicodedata

UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]


def split_boundary(data):
    # Local model of the inspected boundary rule, not a UTF-8 validator.
    groups=[];left=0
    for right in range(1,len(data)+1):
        if right==len(data) or data[right]&0xc0!=0x80:
            groups.append(data[left:right]);left=right
    return groups


def lcs(a,b):
    prev=[0]*(len(b)+1)
    for x in a:
        row=[0]
        for j,y in enumerate(b):
            row.append(prev[j]+1 if x==y else max(prev[j+1],row[-1]))
        prev=row
    return prev[-1]


def oracle(a,b):
    def all_subs(s):
        return {tuple(s[i] for i in inds) for n in range(len(s)+1)
                for inds in itertools.combinations(range(len(s)),n)}
    return max(map(len,all_subs(a)&all_subs(b)))


def score(a,b):
    if a==b:return '1'
    return str(Fraction(2*lcs(a,b),len(a)+len(b)))


def calculate():
    pairs=[('chinese','收入','税收入'),('canonical-equivalence','é','e\u0301'),
        ('emoji-codepoints','👩\u200d💻','👩'),('embedded-nul','A\0B','A\0C'),
        ('one-empty','','收'),('both-empty','','')]
    examples=[]
    for name,a,b in pairs:
        ga,gb=split_boundary(a.encode('utf8')),split_boundary(b.encode('utf8'))
        assert ga==[x.encode('utf8') for x in a] and gb==[x.encode('utf8') for x in b]
        length=lcs(ga,gb);assert length==lcs(a,b)==oracle(a,b)
        examples.append({'name':name,'a':a,'b':b,'python_lengths':[len(a),len(b)],
            'byte_lengths':[len(a.encode('utf8')),len(b.encode('utf8'))],
            'lcs_codepoints':length,'wrapper_reward':score(a,b),
            'nfc_reward_explanatory_only':score(unicodedata.normalize('NFC',a),unicodedata.normalize('NFC',b))})
    values=[0,0x7f,0x80,0x7ff,0x800,0xd7ff,0xe000,0xffff,0x10000,0x10ffff,0x301,0x200d,0x1f469,0x1f4bb]
    strings=[chr(x) for x in values]+[''.join(map(chr,values))]
    for s in strings:assert split_boundary(s.encode('utf8'))==[c.encode('utf8') for c in s]
    malformed=[]
    for raw in (b'\x80a',b'\xc0\xaf'):
        try:raw.decode('utf8',errors='strict')
        except UnicodeDecodeError:valid=False
        else:valid=True
        assert not valid
        malformed.append({'hex':raw.hex(),'boundary_groups':[x.hex() for x in split_boundary(raw)],
                          'strict_utf8_valid':False,'public_binding_acceptance':'not checked'})
    return {'examples':examples,'scalar_values':values,'boundary_strings_checked':len(strings),
            'malformed':malformed,'upstream_executed':False,'release_source_equivalence':False,
            'binding_conversion_checked':False,'normalization_policy_selected':False}


def check():
    n=0
    def require(value,label):
        nonlocal n
        assert value,label;n+=1
    load=lambda name:json.loads((UNIT/name).read_text())
    ledger=load('source-ledger.json')
    require(len(ledger['acquisitions'])==6,'requests')
    for r in ledger['acquisitions']:
        for field in ('body','headers','receipt','invocation'):
            item=r[field];require(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],field)
        receipt=json.loads((ROOT/r['receipt']['path']).read_text())
        require(receipt['http_code']==200 and receipt['exitcode']==0,'success')
        require(receipt['size_download']==(ROOT/r['body']['path']).stat().st_size,'bytes')
    tree=load('sources/03-tree.body');require(not tree['truncated'],'tree flag')
    for i,name in enumerate(load('source-selection.json'),4):
        data=(UNIT/'sources'/f'{i:02d}-source.body').read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        entry=next(x for x in tree['tree'] if x['path']==name)
        require(blob==entry['sha'] and len(data)==entry['size'],name)
    for r in ledger['passages']:
        require(r['quote'] in (ROOT/r['path']).read_text().splitlines()[r['line']-1],r['id'])
    computed=calculate();require(computed==load('witnesses.json'),'exact finite replay')
    mutations=[
        ('bytes confused with codepoints',lambda w:w['examples'][0].update(lcs_codepoints=6)),
        ('normalization assumed',lambda w:w['examples'][1].update(wrapper_reward='1')),
        ('grapheme equality assumed',lambda w:w['examples'][2].update(wrapper_reward='1')),
        ('release equality invented',lambda w:w.update(release_source_equivalence=True)),
        ('binding checked invented',lambda w:w.update(binding_conversion_checked=True)),
        ('normalization adopted',lambda w:w.update(normalization_policy_selected=True)),
    ]
    for label,edit in mutations:
        changed=deepcopy(computed);edit(changed);require(changed!=computed,label)
    for name in ('source-support','citation-venue','backward-snowball','forward-snowball','claim-support','omission-risk'):
        require(bool(load(name+'-ledger.json')),name)
    return {'status':'passed','acquisitions':6,'source_anchors':len(ledger['passages']),'assertions':n,
            'string_pairs':len(computed['examples']),'scalar_boundary_strings':15,
            'malformed_byte_examples':2,'rejected_controls':len(mutations),'whole_rows_closed':0}
