# Arelle occurrence and value boundary

18 October 2026. Static inspection of selected commit
01f6a4656c2c6551d2f05f31c9d74366d133ee7e. Source:
`docs/design/proposal/methods/preparation-20261005-v1/03-adapters/sources/upstream/arelle/arelle__ModelInstanceObject.py`,
SHA256 097d4c252ea800c55c221eb67f9694ca689ee5c7bcd19ae38698941f966e8059.
Line numbers below refer to those exact retained bytes.

The target is an immutable reported occurrence plus explicitly derived
interpretations. The accessors actually inspected return a mixture of text,
defaults, resolved metadata, transformed values and formatted presentation.
They are different quantities. An adapter using one string for all of them
would be wrong relative to the source-preservation target. No such implemented
adapter is claimed here; the earlier exchanges are synthetic expected records.

| Boundary and inspected lines | Actual behavior | Required preservation and fallback |
|---|---|---|
| Native `value`, 392–400 | Uses textValue, then concept default or fixed value when the text is empty | Keep original document bytes and occurrence locator separately. Label the semantic value as reported text, default or fixed, with the supplying declaration bound. An empty occurrence must not be rewritten as an explicitly reported number. Missing declaration/validation leaves that interpretation unresolved. |
| `decimals`/`precision`, 308–346 | Reads the explicit attribute or the concept type's fixed/default attribute | Preserve the literal attribute, its absence, the resolved value and the declaration dependency distinctly. Never multiply an amount by precision/decimals. A convenience value alone cannot prove what was explicitly reported. |
| `xmlLang`, 349–368 | Can inherit language from fact ancestry or the instance parent; a configured disclosure-system default can supply a nonnumeric language | Retain explicit language separately from inherited/configured language and bind the supplying ancestry/configuration. Do not label a configured language as issuer text. Unresolved language may remain unknown. |
| `xsiNil`/`isNil`, 370–376 | An absent nil attribute reads as false; true and 1 read as nil | Preserve original attribute evidence plus the semantic nil state. Nil is not numerical zero, and nonnil alone does not establish valid numeric content. Do not use the mutating nil setter to repair retained evidence. |
| `effectiveValue`, 413–456 | Returns view strings, including nil/error/reported sentinels, rounded/locale-formatted numerics, normalized strings and exception text | Treat it solely as presentation. It cannot supply an exact amount, original token or validation result. Keep structured validation/error status and the underlying supported value; unresolved/error states must not become financial facts. |
| Native `fractionValue`, 403–410 | Returns separate numerator and denominator text | Retain both components and source structure. A generic decimal field does not establish supported exact fraction semantics. Preserve raw/unresolved content until an explicit fraction contract and validation exist; no silent float or string flattening. |
| Future inline `rawValue`, 680–697 | Calls innerText with exclusion/escaping/continuation options and can collapse whitespace when a format is present | This is extracted/aggregated text, not original bytes. Keep original occurrence structure and participating continuation/exclusion evidence before any supported transformation. These options identify dependencies to investigate; this inspection does not audit innerText internals or deliver an inline adapter. |
| Future inline `value`, 700–766 | Applies a format transform, then sign and scale for numeric nonfraction content; handles nil, tuples, fractions and invalid transforms separately | Retain format QName/registry identity, literal attributes, transformation/validation state and exact numeric meaning separately. Do not apply scale/sign again to an already transformed value. Validate attributes rather than treating the implementation's sign-presence branch as a validity rule. Unknown transforms remain unresolved. |

The existing native selection is unchanged. Its URI-to-bytes map, context/unit/
dimension preservation, occurrence multiplicity, offline policy, cancellation
and replay remain necessary. This supplement binds concrete accessor risks to
that policy; it does not replace any of the eleven frozen documentary exchanges
or their 1,255 checks. No new portable field schema, inline support, parser output
or runtime translation is delivered. Original bytes plus a usable locator remain
required even when a convenience accessor returns plausible text.

## Decision

| Decision | Primary criterion status | Veto status | Main uncertainty | Next justified action | What is not concluded |
|---|---|---|---|---|---|
| Deliver the static boundary supplement | Eight line-bound distinctions and fallbacks recorded against the selected source | Pinned hash matches; no parser/runtime claim; no frozen exchange change | Portable translation and actual parser behavior have not been exercised | Carry these cases into the later adapter translation/admission contract; continue independent manuscript review | Lossless implementation, accounting accuracy, compatibility or complete field coverage |
| Keep Version 3.44 unchanged | Existing manuscript already requires raw bodies and labels exchanges documentary | No confirmed manuscript contradiction found in the inspected selection passage | Wider manuscript review remains pending | Resume the exact candidate at page 80 | Full document correctness or acceptance |

No stochastic comparison occurred; ranking, uncertainty intervals and default
promotion are inapplicable. Strongest alternative explanation: a future adapter
could already preserve all these distinctions in other records. That would
satisfy the obligation rather than make the accessors byte-exact. A demonstrated
source-bound translation and downstream preservation checks would retire this
implementation uncertainty. The weakest evidence is the absence of runtime
translation; static inspection cannot establish that behavior.
