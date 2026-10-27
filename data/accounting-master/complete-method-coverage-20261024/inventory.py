"""Source-anchored branch/dependency inventory; not an accounting completeness proof."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import ast
import json
from case_dispositions import GROUPS

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE='data/accounting-master/'
FILES={
    BASE+'company-return-schema-20261023/return_schema.py':'authoring',
    BASE+'company-return-schema-20261023/retained_fixture.py':'source_binding',
    BASE+'company-return-execution-20261024/native_returns.py':'runtime',
    BASE+'company-return-execution-20261024/native_reports.py':'reporting',
    BASE+'company-return-execution-20261024/retained_execution_context.py':'retained_adapter',
    BASE+'company-composed-profile-20261024/company_program.py':'composition'}
EVIDENCE=['company-return-schema-20261023','company-return-execution-20261024',
          'company-composed-profile-20261024']
CHECK_CALLS={'need','yes','require','outside','validate','assess','invariant','bound_to_retained'}


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def category(stage,function,kind,text):
    """Explicit grouping rule; fine semantic expressibility stays unpromoted."""
    leaf=function.split('.')[-1]
    if stage=='source_binding':
        return 'source_projection_and_exact_binding'
    if stage=='retained_adapter':
        return 'trusted_adapter_and_source_identity'
    if stage=='composition':
        return 'composition_capability_source_and_order'
    if stage=='reporting':
        return 'report_and_carry_invariants'
    if leaf in ['schema','closed']:
        return 'structural_schema'
    if leaf in ['q','rational','fmt','yes']:
        return 'scalar_or_finding_admission'
    if stage=='authoring' and function.startswith('validate'):
        return 'structural_context_collection_and_time'
    if stage=='authoring':
        return 'static_guarded_domain_and_method_conditions'
    if function.startswith('invariant'):
        if 'funding_failure' in text:
            return 'economic_funding_failure'
        return 'shared_book_state_invariants'
    if function.startswith('initialize'):
        return 'opening_state_and_component_allocation'
    if function.startswith('transition'):
        if 'funding_failure' in text:
            return 'economic_funding_failure'
        return 'event_specific_transition_and_postconditions'
    if leaf in ['propose','apply']:
        return 'proposal_identity_and_semantic_replay'
    if leaf=='run_prefix':
        return 'prefix_failure_and_atomicity'
    return 'supporting_semantics'


def features(node):
    found=set()
    for part in ast.walk(node):
        if isinstance(part,ast.BinOp) and isinstance(part.op,ast.Mult):
            found.add('product')
        if isinstance(part,(ast.ListComp,ast.SetComp,ast.DictComp,ast.GeneratorExp,ast.For)):
            found.add('collection_or_quantification')
        if isinstance(part,ast.Subscript):
            found.add('record_or_collection_selection')
        if isinstance(part,ast.Call):
            name=ast.unparse(part.func)
            if name in ['sum','min','max','len','set','all','any']:
                found.add(name)
            if name in ['yes','outside']:
                found.add('finding_or_scope_consequence')
    return sorted(found)


def inspect_file(name,stage):
    source=(ROOT/name).read_text()
    tree=ast.parse(source)
    rows,functions=[],[]
    class Visitor(ast.NodeVisitor):
        function='module'
        guards=[]
        loops=[]

        def add(self,node,kind):
            text=ast.get_source_segment(source,node)
            rows.append({'id':name+':'+str(node.lineno)+':'+str(node.col_offset)+':'+kind,
                'file':name,'source_sha256':sha(ROOT/name),'function':self.function,
                'line':node.lineno,'end_line':getattr(node,'end_lineno',node.lineno),
                'kind':kind,'source':text,'guards':list(self.guards),'loops':list(self.loops),
                'category':category(stage,self.function,kind,text),'features':features(node),
                'declarative_coverage':'not_promoted_by_source_enumeration',
                'disposition':'Retain exact current behavior; category review specifies next repair or required external boundary.'})

        def visit_FunctionDef(self,node):
            old=self.function
            self.function=node.name if old=='module' else old+'.'+node.name
            functions.append({'name':self.function,'line':node.lineno,'end_line':node.end_lineno})
            self.generic_visit(node)
            self.function=old

        def visit_If(self,node):
            self.add(node,'branch')
            self.visit(node.test)
            self.guards.append(ast.unparse(node.test))
            for child in node.body:
                self.visit(child)
            self.guards.pop()
            if node.orelse:
                self.guards.append('else_of('+ast.unparse(node.test)+')')
                for child in node.orelse:
                    self.visit(child)
                self.guards.pop()

        def visit_For(self,node):
            self.add(node,'iteration')
            self.visit(node.iter)
            self.loops.append(ast.unparse(node.target)+' in '+ast.unparse(node.iter))
            for child in node.body:
                self.visit(child)
            self.loops.pop()
            for child in node.orelse:
                self.visit(child)

        def visit_IfExp(self,node):
            self.add(node,'conditional_expression')
            self.generic_visit(node)

        def visit_comprehension(self,node):
            self.visit(node.iter)
            self.loops.append(ast.unparse(node.target)+' in '+ast.unparse(node.iter))
            for condition in node.ifs:
                self.add(condition,'comprehension_filter')
                self.visit(condition)
            self.loops.pop()

        def visit_Raise(self,node):
            self.add(node,'raise')
            self.generic_visit(node)

        def visit_Assert(self,node):
            self.add(node,'assert')
            self.generic_visit(node)

        def visit_ExceptHandler(self,node):
            self.add(node,'exception_outcome')
            self.generic_visit(node)

        def visit_Call(self,node):
            target=ast.unparse(node.func)
            if target.split('.')[-1] in CHECK_CALLS:
                self.add(node,'check_call')
            self.generic_visit(node)

    Visitor().visit(tree)
    # Independent AST walk checks enumerated syntax anchors; it does not judge semantics.
    expected=[]
    for node in ast.walk(tree):
        kind=next((k for cls,k in [(ast.If,'branch'),(ast.For,'iteration'),(ast.Raise,'raise'),
                   (ast.Assert,'assert'),(ast.ExceptHandler,'exception_outcome'),
                   (ast.IfExp,'conditional_expression')] if isinstance(node,cls)),None)
        if isinstance(node,ast.Call) and ast.unparse(node.func).split('.')[-1] in CHECK_CALLS:
            kind='check_call'
        if kind:
            expected.append(name+':'+str(node.lineno)+':'+str(node.col_offset)+':'+kind)
        if isinstance(node,ast.comprehension):
            for condition in node.ifs:
                expected.append(name+':'+str(condition.lineno)+':'+str(condition.col_offset)+':comprehension_filter')
    assert sorted(expected)==sorted(row['id'] for row in rows),name
    return {'file':name,'sha256':sha(ROOT/name),'stage':stage,'functions':functions,
            'anchors':sorted(rows,key=lambda r:(r['line'],r['id']))}


def build():
    files=[inspect_file(name,stage) for name,stage in FILES.items()]
    evidence={}
    for package in EVIDENCE:
        path=ROOT/BASE/package/'checks.json'
        body=json.loads(path.read_text())
        assert set(GROUPS[package])==set(body['adverse']),package
        evidence[package]={'file':str(path.relative_to(ROOT)),'sha256':sha(path),
                           'prior_record':body,'reexecuted':False,
                           'adverse_dispositions':GROUPS[package],
                           'coverage':'Prior check/adverse records preserved exactly; branch-level test attribution remains pending.'}
    categories=Counter(row['category'] for f in files for row in f['anchors'])
    return {'scope':'All listed syntax anchors in six explicitly selected boundary files; not all accounting methods or imported adapter internals',
            'files':files,'categories':dict(categories),'prior_evidence':evidence,
            'external_dependencies':[
                'jsonschema and calendar parsing structural behavior',
                'Pinned retained financial_checks.py surrounding-method implementation',
                'Actual source truth, accounting authority and human judgments',
                'Unrepresented sectors, contracts and general source-to-latent reconstruction'],
            'method_eligible':False,'accounting_admission':False,'whole_requirements_closed':0}


if __name__=='__main__':
    inventory=build()
    print(json.dumps({'files':len(inventory['files']),
        'anchors':sum(len(f['anchors']) for f in inventory['files']),
        'functions':sum(len(f['functions']) for f in inventory['files']),
        'categories':inventory['categories'],
        'prior_cases':sum(len(p['prior_record']['adverse']) for p in inventory['prior_evidence'].values())}))
