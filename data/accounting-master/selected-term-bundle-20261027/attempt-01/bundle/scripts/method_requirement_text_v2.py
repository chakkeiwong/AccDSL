"""Explicit versioned type and guard syntax reusing strict v1 tokenization."""
import method_requirements_v1 as core
import method_requirement_text_v1 as prior
import method_requirement_versions as versions

EXCHANGE='MethodRequirementExchange/2'


def validate_exchange(value):
    core.closed(value,['profile','definition','selected_digest','values','available_capabilities'],'exchange')
    core.need(value['profile']==EXCHANGE,'exchange_profile')
    core.need(len(core.canonical(value))<=core.MAX_BYTES,'exchange_size_limit')
    versions.validate(value['definition'])
    core.need(value['selected_digest']==core.digest(value['definition']),'selection_hash')
    core.validate_values(value['definition'],value['values'])
    core.identifiers(value['available_capabilities'],'available_capabilities')
    return value


def decode_exchange(text):
    core.need(type(text) is str and len(text.encode('utf-8'))<=core.MAX_BYTES,'exchange_text_limit')
    return validate_exchange(prior.DECODER.decode(text))


def assess_exchange(value):
    validate_exchange(value)
    return versions.assess(value['definition'],value['values'],value['available_capabilities'])


class Reader(prior.Reader):
    def expression(self,depth=0):
        self.nodes+=1
        core.need(depth<=core.MAX_DEPTH and self.nodes<=core.MAX_NODES,'expression_limit')
        self.take('(')
        op=self.take('word')
        if op=='ref':
            value={'op':op,'id':self.string()}
        elif op=='const':
            value={'op':op,'type':self.take('value'),'value':self.take('value')}
        elif op in ['eq','le','lt','add','sub','mul']:
            value={'op':op,'left':self.expression(depth+1),'right':self.expression(depth+1)}
        elif op=='not':
            value={'op':op,'arg':self.expression(depth+1)}
        elif op in ['all','any']:
            args=[]
            while self.pos<len(self.items) and self.items[self.pos][0]=='(':
                args.append(self.expression(depth+1))
            core.need(bool(args),'empty_boolean_expression')
            value={'op':op,'args':args}
        else:
            raise core.Invalid('unknown_operator:'+op)
        self.take(')')
        return value


def lower(text):
    core.need(type(text) is str and len(text.encode('utf-8'))<=core.MAX_BYTES,'authoring_text_limit')
    definition,selection,values,available=None,None,{},[]
    ended,count=False,0
    required_known_seen=False
    for number,line in enumerate(text.split('\n'),1):
        if not line.strip():
            continue
        count+=1
        core.need(count<=core.MAX_NODES,'declaration_limit')
        try:
            core.need(not ended,'declaration_after_end')
            r=Reader(prior.tokens(line))
            command=r.take('word')
            if definition is None:
                core.need(command=='requirements_exchange','header_required')
                core.need(r.string()==EXCHANGE,'text_exchange_profile')
                profile=r.string()
                versions.module(profile)
                definition={'profile':profile,'method_id':r.string(),'version':r.string(),
                            'inputs':{},'requirements':[],'capabilities':[],'residual_prerequisites':[]}
                if profile=='MethodRequirements/3':
                    definition['required_known']=[]
            elif command=='input':
                key=r.string()
                core.need(key not in definition['inputs'],'duplicate_input')
                definition['inputs'][key]={'type':r.take('value'),'role':r.take('word'),'source_ref':r.string()}
            elif command in ['require','guarded']:
                core.need((command=='guarded')==(definition['profile']=='MethodRequirements/3'),
                          'explicit_guard_version_required')
                req={'id':r.string(),'on_false':r.take('word'),'on_unknown':r.take('word')}
                if command=='guarded':
                    req['guard_requires']=r.take('value')
                req['requires']=r.take('value')
                req['admission_refs']=r.take('value')
                if command=='guarded':
                    req['guard']=r.expression()
                req['predicate']=r.expression()
                definition['requirements'].append(req)
            elif command=='required_known':
                core.need('required_known' in definition,'required_known_version')
                core.need(not required_known_seen,'duplicate_required_known')
                definition['required_known']=r.take('value')
                required_known_seen=True
            elif command in ['capability','residual']:
                definition['capabilities' if command=='capability' else 'residual_prerequisites'].append(r.string())
            elif command=='select':
                core.need(selection is None,'duplicate_selection')
                selection=r.string()
            elif command=='bind':
                key,status=r.string(),r.take('word')
                core.need(key not in values,'duplicate_binding')
                core.need(status in ['known','unknown'],'binding_status')
                values[key]={'status':status,('value' if status=='known' else 'reason'):r.take('value')}
            elif command=='available':
                available.append(r.string())
            elif command=='end_requirements_exchange':
                ended=True
            else:
                raise core.Invalid('unknown_declaration:'+command)
            r.finish()
        except (ValueError,TypeError,RecursionError) as exc:
            raise core.Invalid('line '+str(number)+': '+str(exc)[:200]) from exc
    core.need(definition is not None and selection is not None and ended,'incomplete_document')
    core.need(definition['profile']!='MethodRequirements/3' or required_known_seen,
              'explicit_required_known_declaration')
    return validate_exchange({'profile':EXCHANGE,'definition':definition,'selected_digest':selection,
                              'values':values,'available_capabilities':available})


def render_expression(node):
    op=node['op']
    j=prior.json_token
    if op=='ref':
        args=[j(node['id'])]
    elif op=='const':
        args=[j(node['type']),j(node['value'])]
    elif op in ['all','any']:
        args=[render_expression(child) for child in node['args']]
    elif op=='not':
        args=[render_expression(node['arg'])]
    else:
        args=[render_expression(node['left']),render_expression(node['right'])]
    return '('+' '.join([op]+args)+')'


def render(exchange):
    validate_exchange(exchange)
    d=exchange['definition']
    j=prior.json_token
    rows=['requirements_exchange '+' '.join([j(EXCHANGE)]+[j(d[k]) for k in ['profile','method_id','version']])+';']
    for key,item in sorted(d['inputs'].items()):
        rows.append('input '+' '.join([j(key),j(item['type']),item['role'],j(item['source_ref'])])+';')
    for req in d['requirements']:
        guarded=d['profile']=='MethodRequirements/3'
        parts=[j(req['id']),req['on_false'],req['on_unknown']]
        if guarded:
            parts.append(j(req['guard_requires']))
        parts.extend([j(req['requires']),j(req['admission_refs'])])
        if guarded:
            parts.append(render_expression(req['guard']))
        parts.append(render_expression(req['predicate']))
        rows.append(('guarded ' if guarded else 'require ')+' '.join(parts)+';')
    if d['profile']=='MethodRequirements/3':
        rows.append('required_known '+j(d['required_known'])+';')
    for command,key in [('capability','capabilities'),('residual','residual_prerequisites')]:
        rows.extend(command+' '+j(value)+';' for value in d[key])
    rows.append('select '+j(exchange['selected_digest'])+';')
    for key,item in sorted(exchange['values'].items()):
        rows.append('bind '+' '.join([j(key),item['status'],j(item['value'] if item['status']=='known' else item['reason'])])+';')
    rows.extend('available '+j(value)+';' for value in exchange['available_capabilities'])
    rows.append('end_requirements_exchange;')
    output='\n'.join(rows)+'\n'
    core.need(len(output.encode('utf-8'))<=core.MAX_BYTES,'rendered_text_limit')
    return output
