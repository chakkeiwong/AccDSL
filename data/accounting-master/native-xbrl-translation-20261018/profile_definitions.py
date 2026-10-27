"""Closed type declarations for the proposed documentary profile, not a runtime registry."""
def fields(**items):
    return {"fields": items}


def listing(item):
    return {"list": item}


def union(*items):
    return {"union": list(items)}


def literal(value):
    return {"literal": value}


TYPES = {
    "Unknown": fields(tag=literal("Unknown"), reason="Text", obligation_refs=listing("Ref")),
    "NotApplicable": fields(tag=literal("NotApplicable"), reason="Text"),
    "RawField": union(fields(tag=literal("Present"), token="Text"), fields(tag=literal("Absent"))),
    "QName": fields(namespace_uri="Text", local_name="Text"),
    "Span": fields(byte_start="Int", byte_end="Int"),
    "Locator": fields(byte_start="Int", byte_end="Int", element_id=union("Text", "Null"), element_path="Text"),
    "Namespace": fields(prefix="Text", namespace_uri="Text"),
    "Attribute": fields(name="Text", value="Text"),
    "Identifier": fields(scheme="Text", text="Text"),
    "Period": fields(form={"enum": ["duration", "instant", "forever", "other"]},
                     start_token=union("Text", "Null"), end_token=union("Text", "Null"),
                     instant_token=union("Text", "Null")),
    "Dimension": fields(container={"enum": ["segment", "scenario"]},
                        form={"enum": ["explicit", "typed"]}, axis_token="Text", axis_qname="QName",
                        member_token=union("Text", "Null"), member_qname=union("QName", "Unknown"),
                        source_span="Span"),
    "Measure": fields(token="Text", qname="QName"),
    "Time": union(fields(tag=literal("Instant"), date="Text"),
                  fields(tag=literal("Duration"), start="Text", end_exclusive="Text"), "Unknown"),
    "Value": union(fields(tag=literal("Decimal"), rational="Rational"),
                   fields(tag=literal("Fraction"), numerator_token="Text", denominator_token="Text", rational="Rational"),
                   fields(tag=literal("Nil")), fields(tag=literal("Text"), text="Text"), "Unknown"),
    "Mapping": union(fields(source_path="Text", target_ref="Ref", target_path="Text", relation=literal("equal_decoded_value")),
                     fields(source_path="Text", target_ref="Ref", target_path="Text", relation=literal("explicit_conversion"), conversion_method_ref="Ref")),
}

RECORDS = {
    "ConversionMethod": fields(name="Text", algorithm="Text", specification_ref="BlobRef", evidence_mode=literal("specification_example")),
    "SourceVersion": fields(original_bytes_ref="BlobRef", media_type="Text", origin="Text", acquisition="Unknown", issuer="Unknown",
                            document_identity="Text", publication_evidence="Unknown", vintage_evidence="Unknown", namespace_bindings=listing("Namespace")),
    "UnitOccurrence": fields(source_ref="Ref", locator="Locator", package_root_key="Text", parent_key="Text", disposition=literal("retained")),
    "XbrlContextEvidence": fields(occurrence_ref="Ref", xml_id="Text", identifier="Identifier", period="Period",
                                  dimensions=listing("Dimension"), non_dimension_spans=listing("Span")),
    "XbrlUnitEvidence": fields(occurrence_ref="Ref", xml_id="Text", numerator=listing("Measure"), denominator=listing("Measure")),
    "Context": fields(source_context_ref=union("Ref", "Unknown"), source_unit_ref=union("Ref", "Unknown", "NotApplicable"),
                      legal_entity="Unknown", book="Unknown", perimeter="Unknown", basis="Unknown", currency_or_unit="Unknown",
                      time="Time", calendar="Unknown", dimensions="Unknown", interpretation_status=literal("candidate")),
    "ReportedAssertion": fields(occurrence_refs=listing("Ref"), context_ref="Ref", concept="QName", context_id_token="RawField", unit_id_token="RawField",
                                reported_text="Text", source_attributes=listing("Attribute"), value="Value", decimals="RawField", precision="RawField",
                                explicit_language="RawField", effective_language="Unknown", interpretation_status=literal("candidate")),
    "ImportMapping": fields(outputs=listing("Ref"), field_mappings=listing("Mapping")),
    "ImportComparison": fields(mapping_ref="Ref", output_digests=listing("Text"), field_mapping_count="Int", verdict=literal("correspondence_checked"), evidence_mode=literal("specification_example")),
    "LegacyImport": fields(format="Text", original_bytes_ref="BlobRef", original_id="Text", decoder_ref="Ref", portable_ref="Ref", comparison_ref="Ref"),
}

PACKET = fields(
    fixture_id=literal("authored-native-xbrl-v1"), evidence_mode=literal("specification_example"),
    upstream_executed=literal(False), source_blob="BlobRef", origin=literal("authored-fixture:source.xml"),
    namespace_bindings=listing("Namespace"),
    contexts=listing(fields(xml_id="Text", locator="Locator", identifier="Identifier", period="Period",
                            dimensions=listing("Dimension"), non_dimension_spans=listing("Span"))),
    units=listing(fields(xml_id="Text", locator="Locator", numerator=listing("Measure"), denominator=listing("Measure"))),
    facts=listing(fields(xml_id="Text", locator="Locator", concept="QName", context_id_token="RawField", unit_id_token="RawField",
                         reported_text="Text", attributes=listing("Attribute"), decimals="RawField", precision="RawField",
                         explicit_language="RawField", type_hypothesis={"enum": ["decimal", "fraction", "text", "unknown"]},
                         has_child_content="Bool", numerator_token=union("Text", "Null"), denominator_token=union("Text", "Null"))))


def profile():
    return {"schema": "accdsl.native_xbrl.documentary_profile.proposed.v1", "status": "proposed_not_registered",
            "evidence_mode": "specification_example", "product_implemented": False,
            "envelope_fields": ["kind", "schema", "key", "revision", "body", "dependencies"],
            "primitive_types": ["Text", "Int", "Bool", "Null", "Ref", "BlobRef", "Rational"],
            "packet_type": PACKET,
            "types": TYPES,
            "records": {name: {"schema": "accdsl.native_xbrl.proposed." + name + ".v1", "body_type": shape}
                        for name, shape in RECORDS.items()}}
