# Declared company book and composed provisional transition

CompanyBook/1 is a new optional synthetic-book contract, not a relabelled native
PeriodBook. Fields:profile,context,period,date,accounts,balances,cash_account,
memory_schema,memory_types,memory,seen,flows. Context is exactly entity,book,
currency,case_id,mode; mode is synthetic. Each account declares one classification
asset,liability,equity,income or expense. Balances are exact debit-positive amounts
and sum to zero. Cash account is explicitly selected and classified asset.
Currency is one declared three-letter unit; no conversion or consolidation occurs.

Memory uses an existing closed MethodMemoryEffects schema registry. memory_types
assigns an exact scalar type to every current leaf by JSON pointer. The initial
subset has a fixed leaf population; collection insertion/deletion remains
unsupported rather than inventing type rules. Rational memory has declared
dimensions,scale and company context; Boolean/date/text types use the existing
requirement language. Leaf values are concrete; unknowns live in event inputs
or prerequisites, not a falsely balanced incomplete book.

CompanyBookMethod/1 declares id,version,context,account_map,preconditions,monetary,
memory,postconditions,residual_prerequisites. Context equals the book context.
Account_map maps distinct method roles to distinct declared book accounts.
Monetary definition uses those role names and the existing typed effect engine;
its cash role must map to the book's selected cash account. Unmapped book accounts
are preserved. This mapping declares economic roles; it does not infer their
accounting validity from account names.

Pre/postconditions contain a MethodRequirements/3 manifest and exact input
bindings. Monetary contains a MethodMonetaryEffects/1 definition and bindings.
Each binding reads a declared account role, a typed memory leaf, or a typed event
input. The source's exact type must equal the method declaration. Event inputs
have type,value and provenance; unknown is retained, never zero-filled. The
postcondition reads the proposed after-book and can require,for example,that a
liability control equals its contract memory. Residual prerequisites remain
explicit even when the selected predicates pass.

Memory contains a MethodMemoryEffects/1 definition and input_bindings. It stages
only the memory subtree. Inputs come from known bound monetary inputs,derived
calculations,event identity or date. The core owns balances,date,seen and gross
flows; memory definitions cannot write them. All definitions and schemas are
statically checked before preconditions. No caller path selects executable code.

This profile accepts static scalar replacements only. Every read has an exact
source type, including currency, company and scale, and must match its destination
leaf. Literals are interpreted in the declared destination type. Container writes,
insertions, appends and dynamic paths are unsupported in this fixed-leaf profile.
Nested requirement and monetary definitions share the enclosing method ID/version.
Memory input schemas carry explicit scalar kinds. A false requirement guard means
that prerequisite is inactive; all-inactive prerequisites do not suppress effects.

CompanyBookTransition/1 request fields:profile,expected_state_sha256,
expected_method_sha256,method,event,schemas. Event has id,date,inputs. The method
and all schema hashes must match their actual bodies. Event chronology lies in
the current period and not before the book; duplicate event IDs refuse.

Execution: validate all schemas/types/bindings; assess preconditions; derive
monetary amounts; stage typed memory; construct one new book with mapped journal,
gross flows and event memory; validate its structural/book invariants and method
postconditions. Any failed step returns no applied after-state. Successful propose
retains stage evidence and provisional after-book. Apply recomputes the complete
proposal against the exact request/state using canonical JSON equality, preserving
the distinction between Boolean false and numeric zero. This is atomic pure-value construction,
not database commit,durable recovery or posting authorization under the separate
portable AccountingEventBasis/PostingAuthorization contracts.

Primary demonstrations use two company owners,distinct account identifiers and
two memory layouts for the same explicit liability payment. Full native payment
and sale comparisons use declared projections and preserve unmapped state in
their native adapters. General reporting,closing,multi-currency,method admission,
dynamic memory collections and full native-method imports remain open.
