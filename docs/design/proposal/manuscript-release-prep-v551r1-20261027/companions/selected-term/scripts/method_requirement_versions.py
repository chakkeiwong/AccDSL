"""Closed dispatch to preserved requirement versions; no automatic migration."""
import method_requirements_v1 as v1
import method_requirements_v2 as v2
import method_requirements_v3 as v3

VERSIONS={v1.PROFILE:v1,v2.PROFILE:v2,v3.PROFILE:v3}


def module(profile):
    v1.need(type(profile) is str and profile in VERSIONS,'unsupported_requirement_profile')
    return VERSIONS[profile]


def validate(definition):
    v1.need(type(definition) is dict,'definition')
    selected=module(definition.get('profile'))
    if selected is v1:
        selected.validate_manifest(definition)
    else:
        selected.compile_manifest(definition)
    return definition


def typed(profile,value):
    selected=module(profile)
    return v1.typed(value) if selected is v1 else v2.typed(value)


def assess(definition,values,available):
    validate(definition)
    key=v1.digest(definition)
    return module(definition['profile']).assess({key:definition},key,values,available)
