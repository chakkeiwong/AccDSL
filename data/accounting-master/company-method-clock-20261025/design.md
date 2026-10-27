# Named methods and directly dated company events

CompanyMethodRegistry/1 fields: profile, context, entries. Each of at most32 named
entries declares method_sha256, method, schemas, account_classes, event_inputs,
metadata_bindings, clock. The method is an existing CompanyBookMethod/1 body;
schemas are its complete registry. Account_classes maps every declared account
role to an expected asset/liability/equity/income/expense classification. The
context must match the book. A changed method requires a changed registry identity.

Event_inputs maps every supplied input name to its exact type. Metadata_bindings
maps additional input names to id or date. The populations are disjoint and their
union equals every event input used by the method's prerequisite, monetary and
postcondition bindings. Metadata values come only from the actual event. Their
types are text/date with empty context, and provenance states the metadata origin.
Clock is a closed record with kind direct_event_date. Other named clock families
produce unsupported rather than silently accepting them as direct dates.

CompanyMethodCall/1 fields: profile, expected_state_sha256,
expected_registry_sha256, registry, method_key, event. Event is exactly id,date,
inputs. Each supplied input is the existing type,value,provenance record. Exact
population and type equality are required; callers cannot also supply metadata
inputs. Every registry entry is statically prepared against the current book with
unknown placeholder facts before the selected method receives its actual facts.
This evaluates no effects or applicability predicates. It rejects malformed unused
entries, missing schema/types and incorrect role classifications in the registry.

Materialize returns the ordinary CompanyBookTransition/1 request. Current state and
method identities are recomputed from the explicitly pinned book and registry.
Propose delegates to the checked transition, retaining its complete outcome and
status. Apply recomputes the entire call/proposal using canonical JSON equality,
then delegates to the transition's provisional apply. No durable or posting flags
become true. The input data cannot select executable Python modules or callbacks.

This reference implements named direct-event binding, not portable method admission
or a full ExtensionPackage. AccountingEventBasis/PostingAuthorization remain
separate. Complete native-domain adaptation, assessment intervals, measurement
clocks and carry are not implied by this registry. Native projections remain
explicit test fixtures until their full applicability obligations are implemented.
