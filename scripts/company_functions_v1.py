"""Optional pure functions lowered to the pinned CompanyExpressionsDraft/1."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import re

PROFILE = 'CompanyFunctions/1'
ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT/'data/accounting-master/company-expressions-20261023/expressions.py'
BASE_SHA256 = 'cd80145f61266346f15bdfa82062790bdeb8f4223c75beb1387ae5b140b2d449'
LIMITS = {'functions':32,'parameters':16,'scope_nodes':256,'call_depth':16,
          'expression_depth':64,'emitted_nodes':2048,'request_bytes':262144}
FLAGS = {'temporal_admission':False,'historical_execution_established':False,
         'forecast_admission':False,'real_behavior_evidence':False}

class Invalid(ValueError): pass

def need(condition, why):
    if not condition: raise Invalid(why)

def closed(value, keys):
    need(type(value) is dict and set(value) == set(keys), 'closed_fields')

def name(value):
    need(type(value) is str and re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', value), 'identifier')
    return value

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')

def digest(value): return sha256(canonical(value)).hexdigest()

def load_baseline():
    need(sha256(BASE_PATH.read_bytes()).hexdigest() == BASE_SHA256, 'baseline_hash')
    spec = importlib.util.spec_from_file_location('accdsl_pure_function_baseline', BASE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def compile_program(request):
    """Compile without evaluating values or touching company state."""
    encoded = canonical(request)
    need(len(encoded) <= LIMITS['request_bytes'], 'request_bytes_limit')
    closed(request, ['profile','name','inputs','functions','nodes','outputs'])
    need(request['profile'] == PROFILE, 'profile')
    need(type(request['name']) is str and bool(request['name']), 'program_name')
    need(type(request['functions']) is list and len(request['functions']) <= LIMITS['functions'], 'function_limit')
    base = load_baseline()
    functions = {}
    for f in request['functions']:
        closed(f, ['name','parameters','return_type','nodes','output'])
        ident = name(f['name']); need(ident not in functions, 'duplicate_function')
        need(type(f['parameters']) is list and len(f['parameters']) <= LIMITS['parameters'], 'parameter_limit')
        seen = set()
        for param in f['parameters']:
            closed(param, ['name','type']); key = name(param['name'])
            need(key not in seen, 'duplicate_parameter'); seen.add(key)
        name(f['output']); functions[ident] = f
    need(type(request['inputs']) is dict and type(request['outputs']) is dict and request['outputs'], 'program_maps')
    for k,v in request['outputs'].items(): name(k); name(v)
    scopes = {'main':request['nodes']}
    for ident,f in functions.items(): scopes['function:'+ident] = f['nodes']
    indexes = {}
    calls = {ident:set() for ident in functions}
    for scope,nodes in scopes.items():
        need(type(nodes) is list and 1 <= len(nodes) <= LIMITS['scope_nodes'], 'scope_node_limit')
        index = {}
        for node in nodes:
            need(type(node) is dict, 'node_object')
            ident = name(node.get('id')); need(ident not in index, 'duplicate_node')
            op = node.get('op')
            if op == 'param':
                closed(node, ['id','op','target']); name(node['target'])
                need(scope != 'main', 'main_parameter')
                need(node['target'] in {p['name'] for p in functions[scope[9:]]['parameters']}, 'parameter_capture')
            elif op == 'call':
                closed(node, ['id','op','function','args']); target = name(node['function'])
                need(target in functions, 'missing_function')
                need(type(node['args']) is list and len(node['args']) == len(functions[target]['parameters']), 'call_arity')
                for arg in node['args']: name(arg)
                if scope != 'main': calls[scope[9:]].add(target)
            elif op == 'input':
                closed(node, ['id','op','target']); name(node['target'])
                need(scope == 'main', 'input_capture')
            elif op == 'literal': closed(node, ['id','op','type','value'])
            else:
                need(op in base.ARITY, 'unsupported_operation')
                closed(node, ['id','op','args'])
                need(type(node['args']) is list and len(node['args']) == base.ARITY[op], 'operation_arity')
                for arg in node['args']: name(arg)
            index[ident] = node
        indexes[scope] = index
    visiting = set(); heights = {}
    def call_height(ident):
        need(ident not in visiting, 'recursive_function')
        if ident in heights: return heights[ident]
        visiting.add(ident)
        h = 1 + max((call_height(x) for x in sorted(calls[ident])), default=0)
        visiting.remove(ident); need(h <= LIMITS['call_depth'], 'call_depth_limit')
        heights[ident] = h; return h
    for ident in functions: call_height(ident)
    emitted = 0; scope_visits = 0; template_analyses = {}
    def expand(scope, inputs, outputs, parameters=None):
        nonlocal emitted, scope_visits
        nodes = []; origins = {}; pending_calls = []; serial = 0
        def append(node, origin):
            nonlocal emitted, serial
            emitted += 1; need(emitted <= LIMITS['emitted_nodes'], 'expansion_limit')
            serial += 1; ident = 'n'+str(serial)
            node = deepcopy(node); node['id'] = ident
            nodes.append(node); origins[ident] = origin
            return ident
        seed_params = {}
        for key in (parameters or {}):
            seed_params[key] = append({'op':'input','target':key}, {'scope':scope,'parameter':key,'calls':[]})
        def body(current_scope, bindings, stack):
            nonlocal scope_visits
            scope_visits += 1
            need(scope_visits <= LIMITS['emitted_nodes'], 'expansion_scope_limit')
            index = indexes[current_scope]; cache = {}; active = set()
            def visit(ident, depth=1):
                need(depth <= LIMITS['expression_depth'], 'expression_depth_limit')
                if ident in cache: return cache[ident]
                need(ident in index, 'missing_node_reference')
                need(ident not in active, 'cyclic_expression')
                active.add(ident); node = index[ident]; op = node['op']
                origin = {'scope':current_scope,'node':ident,'calls':deepcopy(stack)}
                if op == 'param':
                    need(node['target'] in bindings, 'parameter_capture'); result = bindings[node['target']]
                elif op == 'call':
                    arguments = [visit(x, depth+1) for x in node['args']]
                    f = functions[node['function']]
                    child_stack = stack + [{'scope':current_scope,'node':ident,'function':f['name']}]
                    need(len(child_stack) <= LIMITS['call_depth'], 'call_depth_limit')
                    local = body('function:'+f['name'], dict(zip([p['name'] for p in f['parameters']], arguments)), child_stack)
                    result = local[f['output']]
                    pending_calls.append({'origin':origin,'function':f['name'],'arguments':arguments,'result':result})
                else:
                    clone = deepcopy(node)
                    if 'args' in clone: clone['args'] = [visit(x, depth+1) for x in clone['args']]
                    result = append(clone, origin)
                active.remove(ident); cache[ident] = result; return result
            for ident in index: visit(ident)
            return cache
        mapping = body(scope, seed_params, [])
        for target in outputs.values(): need(target in mapping, 'missing_output')
        graph = {'profile':base.PROFILE,'name':request['name'],'inputs':deepcopy(inputs),
                 'nodes':nodes,'outputs':{k:mapping[v] for k,v in outputs.items()}}
        # Nodes are emitted after dependencies. Check expanded depth before the
        # predecessor analyzer's recursive walk, including unused definitions.
        depths = {}
        for node in nodes:
            depths[node['id']] = 1 + max((depths[x] for x in node.get('args',[])), default=0)
            need(depths[node['id']] <= LIMITS['expression_depth'], 'expanded_depth_limit')
        analysis = base.analyze(graph)
        for call in pending_calls:
            f = functions[call['function']]
            for arg,param in zip(call['arguments'],f['parameters']): base.compatible(analysis['types'][arg], param['type'])
            base.compatible(analysis['types'][call['result']], f['return_type'])
            call['declared_argument_dependencies'] = sorted({x for arg in call['arguments'] for x in analysis['dependencies'][arg]})
            call['effective_result_dependencies'] = analysis['dependencies'][call['result']]
        return graph,analysis,origins,pending_calls,mapping
    for ident,f in functions.items():
        params = {p['name']:{'type':deepcopy(p['type']),'value':'unknown'} for p in f['parameters']}
        graph,analysis,_,_,_ = expand('function:'+ident, params, {'result':f['output']},params)
        base.compatible(analysis['outputs']['result'], f['return_type'])
        template_analyses[ident] = {'parameters':deepcopy(f['parameters']),'return_type':deepcopy(f['return_type'])}
    graph,analysis,origins,call_sites,mapping = expand('main',request['inputs'],request['outputs'])
    return dict(FLAGS,profile=PROFILE,status='compiled',request_sha256=digest(request),
                baseline_sha256=BASE_SHA256,compiler_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                graph=graph,graph_sha256=base.digest(graph),analysis=analysis,origins=origins,
                call_sites=call_sites,main_node_map=mapping,function_signatures=template_analyses,
                limits=deepcopy(LIMITS),validation_emitted_nodes=emitted,validation_scope_visits=scope_visits)

def evaluate(request):
    try:
        compiled = compile_program(request)
        result = load_baseline().evaluate(compiled['graph'])
        return dict(FLAGS,profile=PROFILE,status=result['status'],compilation=compiled,evaluation=result)
    except Exception as exc:
        return dict(FLAGS,profile=PROFILE,status='invalid',reason='function_program',
                    detail=type(exc).__name__+':'+str(exc).splitlines()[0][:250])
