# Bind an assessment to the actual event date

The pre-freeze red-team review found that method-definition equality alone did
not bind the registry entry's metadata policy. CompanyMethodRegistry permits a
date input to move from metadata_bindings to event_inputs. A caller could keep
the same method hash, supply a later assessment date and execute it earlier.
That is wrong relative to the stated observation-time contract.

The guarded profile now compares event_inputs, metadata_bindings, clock and
account_classes with the regenerated recognized entry. Schema and method hashes
retain the engine's existing checks. The focused adversarial test explicitly
moves event_date into caller inputs, supplies 31 January but executes 2 January,
and requires refusal. It passes. The first recording run overlapped this repair
and is not acceptance evidence; its source-stability check must reject it. Keep
its logs separately and record the final fixed source afresh. The defect rejects
the earlier candidate, not the planned collection-clock direction.
