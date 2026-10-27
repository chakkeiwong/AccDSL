"""Explicit ordered source declarations; frozen evaluators own all semantics."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json,sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'term-structural-admission-20261026'))
import structure as s
sys.path.insert(0,str(HERE.parent/'ordered-eligibility-source-20261026'))
import eligibility_text as syntax

PROFILE='SelectedTermStateText/1'
Invalid=syntax.Invalid;need=syntax.need;core=s.core
def j(value):
    return json.dumps(value,separators=(',',':'),ensure_ascii=False,allow_nan=False)
STRING='string';VALUE='value';WORD='word';EXPR='expression'
def block(name):return ('block',name)
def mapping(word,item):return ('map',word,item)
def sequence(word,item):return ('list',word,item)
STRINGS=sequence('item',STRING)

# Scalar JSON is restricted to named data/type/context fields. Algorithm-bearing
# declarations always have dedicated schemas and cannot be passed as JSON.
SCHEMAS={
 'contract':('SelectedTermStateContract/1',dict(context=VALUE,roles=mapping('role',STRING),
   unit_cost_pointer=STRING,structure=block('structure'),semantics=block('semantics'),residuals=STRINGS)),
 'structure':('SelectedStateStructure/1',dict(normalization=mapping('rename',STRING),
   template=block('admission'),projections=mapping('projection',block('projection')),
   checks=sequence('check',block('structure_check')),residuals=STRINGS)),
 'admission':('DeclaredOpeningAdmission/1',dict(context=VALUE,dependency_pins=sequence('dependency',block('dependency')),
   stages=sequence('stage',block('stage')),residuals=STRINGS)),
 'dependency':(None,dict(file=STRING,sha256=STRING,reason=STRING)),
 'stage':(None,dict(id=STRING,op=WORD,reason=STRING,path=VALUE,fields=VALUE,values=VALUE,
   value=VALUE,label=STRING,roles=VALUE,classes=sequence('class',block('role_class')),role=STRING,
   type=VALUE,maximum=VALUE,manifest=block('rules'),bindings=mapping('binding',block('opening_binding')))),
 'role_class':(None,dict(role=STRING,classification=STRING)),
 'opening_binding':(None,dict(kind=WORD,path=VALUE,role=STRING,type=VALUE)),
 'structure_check':(None,dict(id=STRING,op=WORD,reason=STRING,path=VALUE,projection=STRING,field=STRING)),
 'semantics':('TermStateSemanticBundle/1',dict(context=VALUE,common=block('common'),clock=block('clock'),
   terms=block('nested'),assessments=block('nested'),summaries=block('nested'),events=block('events'),residuals=STRINGS)),
 'projection':('NestedMapProjection/1',dict(context=VALUE,parent_pointer=STRING,child_pointer=STRING,
   fields=mapping('field',block('capture')),residuals=STRINGS)),
 'capture':(None,dict(kind=WORD,pointer=STRING,type=VALUE)),
 'nested':('NestedQueryInvariantTemplate/1',dict(context=VALUE,iteration=block('projection'),mode=WORD,
   captures=mapping('capture',block('capture')),template=block('guarded_queries'),
   slots=sequence('slot',block('slot')),residuals=STRINGS)),
 'slot':(None,dict(kind=WORD,query=STRING,capture=STRING,target=STRING)),
 'guarded_queries':('QueryGuardedInvariant/1',dict(context=VALUE,manifest=block('rules'),
   queries=mapping('query',block('query_entry')),bindings=mapping('binding',block('query_binding')),residuals=STRINGS)),
 'query_entry':(None,dict(projection=block('projection'),query=block('query'),on_ambiguous=WORD)),
 'query':('GroupedRowQuery/1',dict(context=VALUE,mode=WORD,group=block('group'),field=STRING,
   allow_empty=VALUE,value=block('typed_value'),upper_bound=block('typed_value'))),
 'group':(None,dict(parent_key=STRING,parent_path=STRING,child_map_path=STRING)),
 'typed_value':(None,dict(type=VALUE,binding=block('known_value'),inclusive=VALUE)),
 'known_value':(None,dict(status=WORD,value=VALUE)),
 'query_binding':(None,dict(kind=WORD,query=STRING,field=STRING)),
 'rules':('MethodRequirements/3',dict(method_id=STRING,version=STRING,inputs=mapping('input',block('input')),
   requirements=sequence('requirement',block('requirement')),required_known=VALUE,capabilities=STRINGS,
   residual_prerequisites=STRINGS)),
 'input':(None,dict(type=VALUE,role=WORD,source_ref=STRING)),
 'requirement':(None,dict(id=STRING,guard=EXPR,guard_requires=VALUE,predicate=EXPR,requires=VALUE,
   admission_refs=VALUE,on_false=WORD,on_unknown=WORD)),
 'common':('BookStateInvariant/1',dict(context=VALUE,definition=block('totals'),
   globals=mapping('global',block('global_binding')),collections=mapping('collection',block('common_collection')),
   residual_prerequisites=STRINGS)),
 'totals':('MethodCollectionTotals/1',dict(method_id=STRING,version=STRING,snapshot=block('collections'),
   assessment=block('rules'),bindings=mapping('binding',block('total_binding')),residual_prerequisites=STRINGS)),
 'collections':('MethodCollections/1',dict(method_id=STRING,version=STRING,
   inputs=mapping('input',block('input')),collections=mapping('collection',block('collection_type')),
   constraints=sequence('constraint',block('constraint')),residual_prerequisites=STRINGS)),
 'collection_type':(None,dict(fields=mapping('field',block('input')))),
 'constraint':(None,dict(id=STRING,op=WORD,collection=STRING,field=STRING,source=STRING,target=STRING,
   target_field=STRING,definition=block('rules'),bindings=mapping('binding',block('row_binding')))),
 'row_binding':(None,dict(scope=WORD,field=STRING)),
 'global_binding':(None,dict(kind=WORD,account=STRING,pointer=STRING)),
 'common_collection':(None,dict(kind=WORD,pointer=STRING,fields=mapping('field',block('field_binding')))),
 'field_binding':(None,dict(kind=WORD,pointer=STRING)),
 'total_binding':(None,dict(kind=WORD,collection=STRING,field=STRING,input=STRING)),
 'clock':(None,dict(manifest=block('rules'),bindings=mapping('binding',block('capture')))),
 'events':('ProjectedStateCollections/1',dict(context=VALUE,definition=block('collections'),
   sources=mapping('source',block('projection')),bindings=mapping('binding',block('event_binding')),residuals=STRINGS)),
 'event_binding':(None,dict(kind=WORD,source=STRING,fields=mapping('field',STRING),filter=block('filter'))),
 'filter':(None,dict(field=STRING,type=VALUE,value=VALUE)),
}

def scalar(reader,kind):
    if kind==EXPR:return reader.expression()
    if kind==STRING:return reader.string()
    return reader.take(kind)

def value_text(value,kind):
    if kind==EXPR:
        # Rendering only: all parsing, typing and evaluation remain preserved.
        op=value['op']
        if op=='ref':args=[j(value['id'])]
        elif op=='const':args=[j(value['type']),j(value['value'])]
        elif op in ('all','any'):args=[value_text(x,EXPR) for x in value['args']]
        elif op=='not':args=[value_text(value['arg'],EXPR)]
        else:args=[value_text(value['left'],EXPR),value_text(value['right'],EXPR)]
        return '('+' '.join([op]+args)+')'
    if kind==WORD:
        need(type(value) is str and value.isascii() and value.replace('_','').isalnum(),'word_value')
        return value
    if kind==STRING:need(type(value) is str,'string_value')
    return j(value)

class Parser:
    def __init__(self,source):
        self.source=source
        self.rows=[(line,loc) for line,loc in syntax.source_rows(source) if line.strip()]
        self.pos=0;self.locations={};self.nodes=[]

    def next(self):
        if self.pos>=len(self.rows):
            raw=self.source.encode()
            raise Invalid('incomplete_source',syntax.span(self.source,len(raw),len(raw),self.source.count('\n')+1,'token'))
        line,loc=self.rows[self.pos];self.pos+=1
        return syntax.Reader(self.source,line,loc),loc

    def add_span(self,path,start,end,kind):
        loc=syntax.span(self.source,start['byte_start'],end['byte_end'],start['line'],kind)
        self.locations[path]=loc
        return loc

    def item(self,desc,reader,location,path,depth):
        need(depth<=core.MAX_DEPTH,'source_nesting_limit',location)
        if type(desc) is str:
            value=scalar(reader,desc);reader.finish();self.locations[path]=location;return value
        kind=desc[0]
        if kind=='block':
            schema=desc[1];profile,fields=SCHEMAS[schema]
            # A missing filter or unbounded greatest query is explicitly null.
            nullable=schema=='filter' or schema=='typed_value' and path.endswith('/upper_bound')
            if nullable and reader.pos<len(reader.items) and reader.items[reader.pos]==('value',None):
                reader.take('value');reader.finish();self.locations[path]=location;return None
            obj={}
            if profile is not None:
                need(reader.string()==profile,'profile:'+schema,reader.location(0));obj['profile']=profile
            reader.finish()
            while True:
                r,loc=self.next();word=r.take('word')
                if word=='end':r.finish();break
                need(word in fields,'unknown_declaration:'+schema+':'+word,r.location(0))
                need(word not in obj,'duplicate_declaration:'+word,r.location(0))
                obj[word]=self.item(fields[word],r,loc,path+'/'+word,depth+1)
            span=self.add_span(path,location,loc,'block')
            self.nodes.append((schema,obj,path,span))
            return obj
        reader.finish();entry,child=desc[1:];obj={} if kind=='map' else []
        while True:
            r,loc=self.next();word=r.take('word')
            if word=='end':r.finish();break
            need(word==entry,'expected_entry:'+entry,r.location(0))
            if kind=='map':
                name=r.string();need(name not in obj,'duplicate_entry:'+name,r.location(1))
                escaped=name.replace('~','~0').replace('/','~1')
                obj[name]=self.item(child,r,loc,path+'/'+escaped,depth+1)
            else:obj.append(self.item(child,r,loc,path+'/'+str(len(obj)),depth+1))
        self.add_span(path,location,loc,kind)
        return obj

    def parse(self):
        r,loc=self.next()
        need(r.take('word')=='selected_term_state','source_header',loc)
        need(r.string()==PROFILE,'source_profile',loc)
        contract=self.item(block('contract'),r,loc,'',0)
        need(self.pos==len(self.rows),'declaration_after_end',self.rows[self.pos][1] if self.pos<len(self.rows) else loc)
        return contract

def render(contract):
    rows=[]
    def emit(word,value,desc,depth):
        indent='  '*depth
        if type(desc) is str:
            rows.append(indent+word+' '+value_text(value,desc)+';');return
        kind=desc[0]
        if kind=='block':
            schema=desc[1];profile,fields=SCHEMAS[schema]
            if value is None and (schema=='filter' or schema=='typed_value' and word=='upper_bound'):
                rows.append(indent+word+' null;');return
            need(type(value) is dict,'render_block:'+schema)
            if profile is not None:
                need(value.get('profile')==profile and next(iter(value))=='profile','render_profile_order:'+schema)
            rows.append(indent+word+(' '+j(profile) if profile else '')+';')
            for key,item in value.items():
                if key=='profile' and profile:continue
                need(key in fields,'render_field:'+schema+':'+key)
                emit(key,item,fields[key],depth+1)
        else:
            entry,child=desc[1:];rows.append(indent+word+';')
            if kind=='map':
                need(type(value) is dict,'render_map')
                for key,item in value.items():emit(entry+' '+j(key),item,child,depth+1)
            else:
                need(type(value) is list,'render_list')
                for item in value:emit(entry,item,child,depth+1)
        rows.append(indent+'end;')
    emit('selected_term_state '+j(PROFILE),contract,block('contract'),0)
    source='\n'.join(rows)+'\n'
    need(s.p.order_digest(Parser(source).parse())==s.p.order_digest(contract),'render_exact_roundtrip')
    return source

def lower(source):
    parser=Parser(source);contract=parser.parse()
    return dict(profile=PROFILE,status='lowered_structural',contract=contract,
      contract_sha256=core.digest(contract),contract_order_sha256=s.p.order_digest(contract),
      source_sha256=sha256(source.encode()).hexdigest(),source_locations=parser.locations,
      executed=False,opening_admitted=False,future_commands_validated=False,
      source_admission=False,accounting_admission=False)

def compile_text(source,memory_definition):
    parser=Parser(source);contract=parser.parse()
    # Postorder checks locate opaque semantic errors at their actual component.
    validators={
      'projection':lambda v:s.p.compile_spec(v,memory_definition),
      'rules':s.bundle.t.c.guarded.compile_manifest,
      'collections':s.bundle.d.bridge.engine.validate,
      'common':s.p.guards.validate,
      'admission':s.admission.compile_template,
      'guarded_queries':lambda v:s.bundle.t.c.validate(v,memory_definition),
      'nested':lambda v:s.bundle.t.validate(v,memory_definition),
      'events':lambda v:s.bundle.d.bridge.validate(v,memory_definition),
      'structure':lambda v:s.validate(v,memory_definition),
      'semantics':lambda v:s.bundle.validate(v,memory_definition),
      'contract':lambda v:s.validate_contract(v,{'memory_definition':memory_definition}),
    }
    for schema,value,path,location in parser.nodes:
        if schema not in validators:continue
        try:validators[schema](value)
        except Exception as exc:
            raise Invalid(getattr(exc,'reason',str(exc)),location) from exc
    return dict(profile=PROFILE,status='compiled_structural',contract=contract,
      contract_sha256=core.digest(contract),contract_order_sha256=s.p.order_digest(contract),
      source_sha256=sha256(source.encode()).hexdigest(),source_locations=parser.locations,
      executed=False,opening_admitted=False,future_commands_validated=False,
      source_admission=False,accounting_admission=False)

def assess_source(source,memory_definition,state,coverage,selection,call):
    contract=compile_text(source,memory_definition)['contract']
    return s.admit(contract,state,coverage,selection,call)
