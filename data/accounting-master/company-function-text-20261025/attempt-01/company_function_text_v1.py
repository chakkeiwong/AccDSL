"""Matched textual authoring; no expression evaluation, shell execution or I/O."""
from hashlib import sha256
from pathlib import Path
import json
import shlex
import company_functions_v1 as functions

COMPILER_SHA256='148aa59be38de0afb46b86983e3d3e2b83284b043ffdfc6058a7af9a32f3f447'
LIMITS={'source_bytes':524288,'line_bytes':16384,'declarations':12000}

class Invalid(ValueError):pass
def need(ok,reason):
    if not ok:raise Invalid(reason)

def compiler():
    need(sha256(Path(functions.__file__).read_bytes()).hexdigest()==COMPILER_SHA256,'compiler_hash')
    return functions

def strict_type(text):
    def unique(pairs):
        result={}
        for k,v in pairs:
            need(k not in result,'duplicate_type_key');result[k]=v
        return result
    def constant(value):raise Invalid('nonfinite_type_constant')
    return json.loads(text,object_pairs_hook=unique,parse_constant=constant)

def scalar(value):return True if value=='true' else False if value=='false' else value

def lower(source):
    if type(source) is str:raw=source.encode('utf-8')
    else:need(type(source) is bytes,'UTF8_source_required');raw=source
    need(len(raw)<=LIMITS['source_bytes'],'source_bytes_limit')
    text=raw.decode('utf-8','strict')
    need(not text.startswith('\ufeff'),'UTF8_BOM_unsupported')
    need('\r' not in text.replace('\r\n',''),'lone_CR_unsupported')
    need(all(ord(c)>=32 or c in '\t\r\n' for c in text),'control_character')
    need('\x7f' not in text,'control_character')
    module=compiler();body=None;active=None;ended=False;offset=0;spans=[]
    function_names=set();phase=None;function_index=None
    lines=raw.splitlines(keepends=True)
    for number,chunk in enumerate(lines,1):
        content=chunk[:-2] if chunk.endswith(b'\r\n') else chunk[:-1] if chunk.endswith(b'\n') else chunk
        need(len(content)<=LIMITS['line_bytes'],'line_bytes_limit')
        decoded=content.decode('utf-8');line=decoded.strip(' \t')
        start=offset+len(content)-len(content.lstrip(b' \t'))
        end=offset+len(content.rstrip(b' \t'))
        offset+=len(chunk)
        if not line:continue
        try:
            need(not ended,'content_after_end_program')
            need(line.endswith(';'),'semicolon_required')
            tokens=shlex.split(line[:-1],comments=False,posix=True)
            need(bool(tokens),'empty_declaration');kind,*args=tokens
            need(len(spans)<LIMITS['declarations'],'declaration_limit')
            path=[]
            if body is None:
                need(kind=='program' and len(args)==2,'program_header')
                body={'profile':args[0],'name':args[1],'inputs':{},'functions':[],'nodes':[],'outputs':{}}
            elif active is not None:
                prefix=['functions',function_index]
                if kind=='parameter' and len(args)==2:
                    need(phase=='parameters','parameter_order')
                    need(args[0] not in {p['name'] for p in active['parameters']},'duplicate_parameter')
                    path=prefix+['parameters',len(active['parameters'])]
                    active['parameters'].append({'name':args[0],'type':strict_type(args[1])})
                elif kind=='returns' and len(args)==1:
                    need(phase=='parameters','returns_order');active['return_type']=strict_type(args[0]);phase='nodes';path=prefix+['return_type']
                elif kind=='result' and len(args)==1:
                    need(phase=='nodes','result_order');active['output']=args[0];phase='ended';path=prefix+['output']
                elif kind=='end_function' and not args:
                    need(phase=='ended','incomplete_function');path=prefix;active=None;phase=None
                else:
                    need(phase=='nodes','function_declaration_order')
                    path=prefix+['nodes',len(active['nodes'])]
                    active['nodes'].append(parse_node(kind,args,inside=True))
            elif kind=='function' and len(args)==1:
                need(args[0] not in function_names,'duplicate_function');function_names.add(args[0])
                function_index=len(body['functions']);active={'name':args[0],'parameters':[],'nodes':[]}
                body['functions'].append(active);phase='parameters';path=['functions',function_index]
            elif kind=='input' and len(args)==3:
                need(args[0] not in body['inputs'],'duplicate_input')
                body['inputs'][args[0]]={'type':strict_type(args[1]),'value':scalar(args[2])};path=['inputs',args[0]]
            elif kind=='output' and len(args)==2:
                need(args[0] not in body['outputs'],'duplicate_output');body['outputs'][args[0]]=args[1];path=['outputs',args[0]]
            elif kind=='end_program' and not args:ended=True
            else:
                path=['nodes',len(body['nodes'])];body['nodes'].append(parse_node(kind,args,inside=False))
            left=len(decoded)-len(decoded.lstrip(' \t'));right=len(decoded.rstrip(' \t'))
            spans.append({'kind':kind,'path':path,'line':number,'byte_start':start,'byte_end':end,
                          'column_start':left+1,'column_end':right+1,'slice_sha256':sha256(raw[start:end]).hexdigest()})
        except (ValueError,TypeError,KeyError) as exc:
            raise Invalid('line '+str(number)+': '+str(exc)) from exc
    need(body is not None and ended and active is None,'incomplete_program')
    compilation=module.compile_program(body)
    return dict(module.FLAGS,status='compiled_source',profile='CompanyFunctionText/1',request=body,
        request_sha256=module.digest(body),source_sha256=sha256(raw).hexdigest(),source_bytes=len(raw),
        compiler_sha256=COMPILER_SHA256,frontend_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        declarations=spans,compilation=compilation)

def parse_node(kind,args,inside):
    if kind=='literal' and len(args)==3:return {'id':args[0],'op':'literal','type':strict_type(args[1]),'value':scalar(args[2])}
    if kind=='node' and len(args)>=2:
        need(args[1] in functions.load_baseline().ARITY,'ordinary_operator_required')
        return {'id':args[0],'op':args[1],'args':args[2:]}
    if kind=='call' and len(args)>=2:return {'id':args[0],'op':'call','function':args[1],'args':args[2:]}
    if kind=='input_ref' and len(args)==2 and not inside:return {'id':args[0],'op':'input','target':args[1]}
    if kind=='param_ref' and len(args)==2 and inside:return {'id':args[0],'op':'param','target':args[1]}
    raise Invalid('unknown_declaration_or_arity')

def render(request):
    compiler().compile_program(request)
    def token(value):
        if type(value) is bool:return 'true' if value else 'false'
        need(type(value) is str and '\n' not in value and '\r' not in value,'line_token_required')
        return shlex.quote(value)
    def line(kind,*args):return ' '.join([kind]+[token(x) for x in args])+';'
    def typ(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
    def node(n):
        if n['op']=='literal':return line('literal',n['id'],typ(n['type']),n['value'])
        if n['op'] in ['input','param']:return line('input_ref' if n['op']=='input' else 'param_ref',n['id'],n['target'])
        if n['op']=='call':return line('call',n['id'],n['function'],*n['args'])
        return line('node',n['id'],n['op'],*n['args'])
    out=[line('program',request['profile'],request['name'])]
    for k,v in sorted(request['inputs'].items()):out.append(line('input',k,typ(v['type']),v['value']))
    for f in request['functions']:
        out.append(line('function',f['name']))
        for p in f['parameters']:out.append(line('parameter',p['name'],typ(p['type'])))
        out.append(line('returns',typ(f['return_type'])));out.extend(node(n) for n in f['nodes'])
        out.extend([line('result',f['output']),'end_function;'])
    out.extend(node(n) for n in request['nodes'])
    out.extend(line('output',k,v) for k,v in sorted(request['outputs'].items()))
    text='\n'.join(out+['end_program;'])+'\n'
    # Rendering succeeds only for the same subset the frontend accepts.
    lowered=lower(text)
    need(lowered['request']==request,'render_request_mismatch')
    return text
