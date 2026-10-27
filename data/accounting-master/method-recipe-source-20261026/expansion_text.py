"""Explicit ordered row replacements over a directly authored base recipe."""
from hashlib import sha256
import recipe_text as recipe
syntax=recipe.syntax;core=recipe.core;expand=recipe.expander
Invalid=recipe.Invalid;need=recipe.need;j=recipe.j
PROFILE='OrderedExpansionText/1'

class Reader(recipe.Reader):
    def row_expression(self,depth=0):
        self.nodes+=1;need(depth<=core.MAX_DEPTH and self.nodes<=core.MAX_NODES,'row_expression_limit',self.location())
        self.take('(');index=self.pos;op=self.take('word')
        if op=='const':value={'expr':'literal','type':self.take('value'),'value':self.take('value')}
        elif op=='row':value={'expr':op,'field':self.string()}
        elif op=='key':value={'expr':op}
        elif op=='event_metadata':value={'expr':op,'field':self.string()}
        elif op=='event_input':value={'expr':op,'name':self.string(),'type':self.take('value')}
        elif op in ('date_lt','date_le'):value={'expr':op,'left':self.row_expression(depth+1),'right':self.row_expression(depth+1)}
        elif op=='if':value={'expr':op,'condition':self.row_expression(depth+1),'then':self.row_expression(depth+1),'else':self.row_expression(depth+1)}
        elif op=='operation_id':value={'expr':op,'prefix':self.string()}
        elif op=='path':
            value={'expr':'array','items':[]}
            while self.pos<len(self.items) and self.items[self.pos][0]=='(':value['items'].append(self.row_expression(depth+1))
        else:raise Invalid('row_expression:'+op,self.location(index))
        self.take(')');return value

def literal(value):return {'expr':'literal','type':expand.c.TEXT,'value':value}

def lower(source):
    location=None
    try:
        rows=syntax.source_rows(source);state='header';template=None;spans=[];operations=[];base_start=None
        for line,location in rows:
            if not line.strip():continue
            spans.append(location);need(state!='done','declaration_after_end',location)
            if state=='base':
                if line.strip()=='end_base;':
                    embedded=source.encode()[base_start:location['byte_start']].decode()
                    try:template['base_template']=recipe.lower(embedded)['template']
                    except Invalid as exc:
                        loc=exc.location
                        if loc:
                            exc.location=syntax.span(source,base_start+loc['byte_start'],base_start+loc['byte_end'],base_line+loc['line']-1,loc['granularity'])
                        raise
                    state='body'
                continue
            r=Reader(source,line,location);word=r.take('word')
            if state=='header':
                need(word=='ordered_expansion' and r.string()==PROFILE,'expansion_source_profile',location)
                template=dict(profile=r.string(),row_types={},row_operations=[],suffix_operations=[],residuals=[])
                need(template['profile']==expand.PROFILE,'expansion_profile',location);state='body'
            elif word=='begin_base':
                need('base_template' not in template,'duplicate_base',location);state='base'
                base_start=source.encode().find(b'\n',location['byte_end'])+1
                need(base_start>0,'base_newline_required',location);base_line=location['line']+1
            elif word=='map_pointer':
                need('map_pointer' not in template,'duplicate_map_pointer',location);template['map_pointer']=r.string()
            elif word=='row_type':
                key=r.string();need(key not in template['row_types'],'duplicate_row_type',location);template['row_types'][key]=r.take('value')
            elif word in ('row_replace','suffix_replace'):
                fields={'id':r.row_expression(),'op':literal('replace'),'path':r.row_expression(),
                        'value':{'expr':'object','fields':{'kind':literal('literal'),'value':r.row_expression()}}}
                template['row_operations' if word=='row_replace' else 'suffix_operations'].append({'expr':'object','fields':fields})
                operations.append(location)
            elif word=='residual':template['residuals'].append(r.string())
            else:
                need(word=='end_expansion','expansion_declaration:'+word,r.location(0))
                need('base_template' in template and 'map_pointer' in template and template['row_types'] and template['row_operations'],'incomplete_expansion',location);state='done'
            r.finish()
        need(state=='done','incomplete_source:'+state,location);recipe.c.base.memory.bounded(template);recipe.c.exact(template)
        return dict(profile=PROFILE,status='lowered_syntax_only',template=template,template_sha256=core.digest(template),
                    source_sha256=sha256(source.encode()).hexdigest(),source_spans=spans,operation_spans=operations,
                    executed=False,contextually_compiled=False,source_admission=False,accounting_admission=False)
    except Exception as exc:
        if isinstance(exc,Invalid):raise
        raise Invalid(getattr(exc,'reason',str(exc)),location) from exc

def construct_source(source,book,event,schemas,definition,call):
    lowered=lower(source)
    try:return expand.construct(lowered['template'],book,event,schemas,definition,call)
    except Exception as exc:raise Invalid(getattr(exc,'reason',str(exc)),syntax.span(source,0,len(source.encode()),1,'document')) from exc

def expression(value):
    kind=value['expr'];args=[]
    if kind=='literal':kind='const';args=[j(value['type']),j(value['value'])]
    elif kind in ('row','event_metadata'):args=[j(value['field'])]
    elif kind=='event_input':args=[j(value['name']),j(value['type'])]
    elif kind in ('date_lt','date_le'):args=[expression(value[k]) for k in ('left','right')]
    elif kind=='if':args=[expression(value[k]) for k in ('condition','then','else')]
    elif kind=='operation_id':args=[j(value['prefix'])]
    elif kind=='array':kind='path';args=[expression(v) for v in value['items']]
    else:need(kind=='key','row_expression')
    return '('+' '.join([kind]+args)+')'

def render(template):
    rows=['ordered_expansion '+j(PROFILE)+' '+j(template['profile'])+';','begin_base;']
    rows.extend(recipe.render(template['base_template']).rstrip('\n').split('\n'));rows.append('end_base;')
    rows.append('map_pointer '+j(template['map_pointer'])+';')
    for key,typ in template['row_types'].items():rows.append('row_type '+j(key)+' '+j(typ)+';')
    for word,key in [('row_replace','row_operations'),('suffix_replace','suffix_operations')]:
        for operation in template[key]:
            f=operation['fields']
            need(f['op']==literal('replace') and f['value']['fields']['kind']==literal('literal'),'replace_operation_required')
            rows.append(word+' '+' '.join(expression(v) for v in (f['id'],f['path'],f['value']['fields']['value']))+';')
    for value in template['residuals']:rows.append('residual '+j(value)+';')
    rows.append('end_expansion;');source='\n'.join(rows)+'\n'
    need(core.canonical(lower(source)['template'])==core.canonical(template),'render_roundtrip');return source
