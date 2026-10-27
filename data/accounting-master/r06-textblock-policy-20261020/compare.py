"""Static policy evidence and authored transformation witnesses; no validator."""
import ast
from collections import Counter
import hashlib,json,re
from pathlib import Path
import xml.etree.ElementTree as ET
U=Path(__file__).resolve().parent;R=U.parents[2];B=R/'data/accounting-master'
SOURCE=U/'sources/ValidateFilingText-sandbox.body'
TEXT=B/'r06-text-semantics-20261020/occurrences.json'
def load(p):return json.loads(p.read_text())
def bind(p):return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def parse_text(s):return ''.join(ET.fromstring('<body>'+s+'</body>').itertext())

def authored_projection(s):
    # Authored ASCII-name subset, used only on explicitly listed literals.
    # It is not the upstream regex package or a generic Unicode match claim.
    return re.sub(r'&[A-Za-z_][A-Za-z0-9_.:-]*;','',s).replace('&','&amp;')

def examples():
 rows=[]
 cases=[('named_amp','R&amp;D','RD','R&D'),
  ('numeric_amp','R&#38;D','R&amp;#38;D','R&D'),
  ('named_quot','&quot;value&quot;','value','"value"'),
  ('encoded_markup','&lt;b&gt;literal&lt;/b&gt;','bliteral/b','<b>literal</b>'),
  ('plain_text','plain text','plain text','plain text'),
  ('markup_text','<span>A&amp;B</span>','<span>AB</span>','A&B')]
 for name,original,wanted,original_text in cases:
  projected=authored_projection(original);assert projected==wanted
  assert parse_text(original)==original_text
  rows.append({'name':name,'original':original,'authored_validation_projection':projected,
    'original_parsed_text':original_text,'projected_parsed_text':parse_text(projected),
    'source_text_changed':original!=projected})
 row=next(x for x in load(TEXT) if x['fact_id']=='f-684');content=row['decoded_text']
 assert 'R&amp;D' in content and 'R&amp;amp;D' in row['source_span']['raw_utf8']
 rows.append({'name':'real_f684_conditional_value_input','fact':'f-684','occurrences_of_literal':content.count('R&amp;D'),
   'source_xml_literal':'R&amp;amp;D','decoded_stored_literal':'R&amp;D',
   'preserved_xml_character_result':parse_text('R&amp;D'),
   'authored_validation_projection':parse_text(authored_projection('R&amp;D')),
   'runtime_value_equivalence':'not_executed'})
 # A neutral wrapper and both inspected caller templates can all be XML-well-
 # formed despite different DTD rules; these are XML shapes, not validation.
 for label,wrapper in [('neutral','<fragment>{}</fragment>'),('noninline','<body>{}</body>'),('inline','<body><div>{}</div></body>')]:
  root=ET.fromstring(wrapper.format('plain <span>text</span>'))
  rows.append({'name':label+'_wrapper','root':root.tag,'children':[e.tag for e in root],
    'xml_character_text':''.join(root.itertext()),'DTD_validated':False})
 return rows

def static_checks():
 t=SOURCE.read_text();tree=ast.parse(t);out=[]
 defs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
 remove=defs['removeEntities']
 ret=next(n for n in remove.body if isinstance(n,ast.Return))
 assert ast.unparse(ret.value)=="namedEntityPattern.sub('', text).replace('&', '&amp;')";out.append('entity_deletion_then_amp_escape')
 loadnode=defs['loadDTD'];assert 'modelXbrl.modelManager.cntlr.configDir' in ast.unparse(loadnode);out.append('runtime_config_directory')
 assert "'xhtml1-strict-ix.dtd' if _isInline else 'edbody.dtd'" in ast.unparse(loadnode);out.append('document_type_selects_DTD')
 v=ast.unparse(defs['validateTextBlockFacts'])
 for term in ["f1.xsiNil != 'true'",'concept.isTextBlock','XMLpattern.match(f1.value)','CDATApattern.findall(f1.value)',
              'XML(xmlBodyWithoutEntities)','edbodyDTD.validate(textblockXml)','allowedExternalHrefPattern','allowedImageTypes',
              "elt.iterancestors('table')"]:
  assert term in v,term;out.append(term)
 assert "f1.xValid" not in v;out.append('no_explicit_xValid_guard_in_this_function')
 assert '<body><div>\\n{0}\\n</div></body>\\n' in t;out.append('inline_div_wrapper')
 assert '<body>\\n{0}\\n</body>\\n' in t;out.append('noninline_body_wrapper')
 ed=(U/'sources/edbody.dtd-sandbox.body').read_text();ix=(U/'sources/xhtml1-strict-ix.dtd-sandbox.body').read_text()
 assert 'modified to limit permitted tags' in ed;out.append('edbody_is_modified_profile')
 assert '<!ELEMENT body %Flow;>' in ed;out.append('edbody_body_mixed_flow')
 assert '<!ELEMENT body %Block;>' in ix;out.append('inline_body_block_only')
 assert '<!ELEMENT div %Flow;>' in ed and '<!ELEMENT div %Flow;>' in ix;out.append('both_div_mixed_flow')
 for s in (ed,ix):
  for ent in ('xhtml-lat1.ent','xhtml-symbol.ent','xhtml-special.ent'):assert ent in s;out.append('external_entity_dependency_'+ent)
 dtr=(U/'sources/DTR.visible.txt').read_text()
 for text in ('Candidate Recommendation 17 January 2018','xsd:documentation','Software vendors are NOT obliged',
              'release version, rather than a list of individual data types.'):
  assert text in dtr;out.append(text)
 assert 'textBlockItemType' not in dtr;out.append('structure_document_does_not_define_textBlock')
 return out

def derive():
 dtr={'edition':'Candidate Recommendation 17 January 2018','role':'exact linked OIM dependency; not claimed latest',
  'definition_location':'schema xsd:documentation annotation','base_spec_support_implies_DTR_support':False,
  'generic_textblock_XHTML_fragment_algorithm':'not_supplied_in_this_structure_document'}
 duties=[
  ('DTR semantic content','retained type annotations','additional to schema grammar','not_fully_validated'),
  ('supported DTR release/types','DTR section6 and OIM supported types','must be named independently of base specification support','unselected_runtime'),
  ('source value provenance','prior inline/occurrence evidence','bind actual f.value against retained source before applying helper','runtime_not_checked'),
  ('document type','loadDTD','inline versus noninline controls DTD and wrapper','runtime_not_checked'),
  ('configuration identity','loadDTD configDir','bind actual DTD files and parser environment','runtime_not_checked'),
  ('entity dependencies','two DTD headers','three external entity files remain unacquired here','pending_source'),
  ('selection coverage','validateTextBlockFacts guard','nil spelling, concept type, XMLpattern determine which facts are checked','source_only'),
  ('validation projection','removeEntities','deletes named entities and escapes remaining ampersands; preserve original separately','source_and_witnesses'),
  ('fragment wrapper','htmlBodyTemplate','body Flow versus body/div Block adaptation','source_only'),
  ('DTD validation','edbodyDTD.validate','selected profile check rather than generic DTR acceptance','not_run'),
  ('additional restrictions','validateTextBlockFacts loops','links, active content, images and nested tables exceed DTD checks','not_run'),
  ('caller activation','external caller','execution depends on selected disclosure/profile/call path','not_checked'),
  ('full XHTML validity','prior XHTML source','edition/fragment interpretation remains distinct from whole-document rules','unresolved'),
  ('financial meaning','mission requirements','rendered data and financial assertions need separate evidence','unadmitted')]
 return {'DTR':dtr,'duties':[dict(zip(('duty','source','requirement','status'),x)) for x in duties],
  'source_findings':static_checks(),'witnesses':examples(),'generic_validity_claim':False,'upstream_executed':False}

def check():
 ledger=load(U/'source-ledger.json');n=0
 for b in ledger['bindings']:assert bind(R/b['path'])==b;n+=1
 for a in ledger['anchors']:
  p=R/a['source']['path'];assert bind(p)==a['source'];n+=1
  assert chr(10).join(p.read_text().splitlines()[a['first_line']-1:a['last_line']])==a['excerpt'];n+=1
 actual=derive();assert actual==load(U/'policy.json');n+=1+len(actual['source_findings'])+len(actual['witnesses'])
 for name in ('DTR','ValidateFilingText','edbody.dtd','xhtml1-strict-ix.dtd'):
  r=load(U/'sources'/(name+'-receipt.json'));res=r.get('final_result',{}).get('value',r['result'])
  meta=json.loads(res['output']);assert meta['http_code']==200 and res['exit_code']==0;n+=1
  assert (U/'sources'/(name+'-sandbox.body')).stat().st_size==meta['size_download'];n+=1
 return {'assertions':n,'source_findings':len(actual['source_findings']),'authored_witnesses':len(actual['witnesses']),
  'duties':len(actual['duties']),'source_anchors':len(ledger['anchors']),'input_bindings':len(ledger['bindings']),
  'acquisitions':4,'upstream_executed':False,'DTD_validation':'not_run','full_XHTML_DTR_validity':'unadmitted','whole_rows_closed':0}
