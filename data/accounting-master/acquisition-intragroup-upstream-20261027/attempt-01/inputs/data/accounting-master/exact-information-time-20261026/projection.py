"""Exact timestamp conversion; selected predicates remain in existing engines."""
from datetime import date
from fractions import Fraction
from pathlib import Path
import re,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import method_requirements_v1 as core
import method_input_binding_v2 as binder
import method_requirements_v2 as dimensional
PROFILE='ExactInstantProjection/1'
AXIS='proleptic-Gregorian/0001-01-01T00:00:00Z/fixed-offset/no-leap-seconds'
BOUNDARY={'executed':False,'source_admission':False,'accounting_admission':False,'method_eligible':False}
PATTERN=re.compile(r'([0-9]{4}-[0-9]{2}-[0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(?:[.]([0-9]+))?(Z|[+-][0-9]{2}:[0-9]{2})')

class Unsupported(ValueError):pass

def instant(value):
    core.text(value,'timestamp')
    m=PATTERN.fullmatch(value)
    if not m:raise Unsupported('explicit_fixed_offset_timestamp_required')
    day,hour,minute,second,fraction,offset=m.groups()
    d=date.fromisoformat(day);core.need(d.isoformat()==day,'canonical_date')
    h,mn,s=int(hour),int(minute),int(second)
    core.need(0<=h<24 and 0<=mn<60,'clock_range')
    if s==60:raise Unsupported('leap_second')
    core.need(0<=s<60,'second_range')
    if fraction and len(fraction)>18:raise Unsupported('fraction_precision_limit')
    if offset=='-00:00':raise Unsupported('unknown_negative_zero_offset')
    shift=0
    if offset!='Z':
        oh,om=int(offset[1:3]),int(offset[4:6])
        core.need(0<=oh<24 and 0<=om<60,'offset_range')
        shift=(1 if offset[0]=='+' else -1)*(oh*3600+om*60)
    q=Fraction((d.toordinal()-1)*86400+h*3600+mn*60+s-shift)
    if fraction:q+=Fraction(int(fraction),10**len(fraction))
    if not 0<=q<date.max.toordinal()*86400:raise Unsupported('normalized_utc_range')
    return q

def rational(q):return str(q.numerator)+'/'+str(q.denominator)

def output_type(source_type):
    core.need(source_type['kind']=='text','timestamp_text_type')
    result={'kind':'rational','context':{'time_axis':AXIS,'source_context':core.canonical(source_type['context']).decode()},
            'dimensions':{'utc_second':1},'scale':'1/1'}
    dimensional.typed(result)
    return result

def project(packet):
    result={**BOUNDARY,'profile':PROFILE}
    try:
        core.closed(packet,['plan','manifests','schemas','blobs','available_capabilities'],'projection_inputs')
        core.identifiers(packet['available_capabilities'],'available_capabilities')
        bound=binder.bind(packet['plan'],packet['manifests'],packet['schemas'],packet['blobs'])
        result['source_binding']=bound
        if bound['status']!='bound':return {**result,'status':bound['status'],'reason':bound['reason']}
        values={}
        for key,item in bound['values'].items():
            line=bound['lineage'][key];typ=output_type(line['type'])
            projected=dict(item) if item['status']=='unknown' else {'status':'known','value':rational(instant(item['value']))}
            values[key]={'value':projected,'type':typ,'role':line['role'],'original_value':dict(item),
                         'original_type':line['type'],'source_lineage':line}
        record={'profile':PROFILE,'time_axis':AXIS,'source_plan_digest':bound['plan_digest'],
                'source_manifest_digest':bound['manifest_digest'],'values':values}
        core.need(len(core.canonical(record))<=core.MAX_BYTES,'projection_size_limit')
        return {**result,'status':'projected','record':record,'record_digest':core.digest(record)}
    except Unsupported as exc:return {**result,'status':'unsupported','reason':str(exc)}
    except (ValueError,TypeError,KeyError,OverflowError) as exc:return {**result,'status':'invalid','reason':str(exc)}
