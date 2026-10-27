# Native loader source delta, proposed version 1

This additive note refines native-offline-resolution-proposed-v1.md using newly
inspected source at the same Arelle commit,
01f6a4656c2c6551d2f05f31c9d74366d133ee7e. It changes no frozen input, active
schema, runtime selection or manuscript. Exact files and spans are bound in
`data/accounting-master/native-loader-source-20261018/source-anchors.json`.

## Bytes and parser input

The proposed receipt needs three distinct stages: the original retained bytes,
the selected resource/archive member bytes, and the text or bytes supplied to
the parser. FileSource.file reads ZIP or tar member bytes; a text request can
detect encoding, strip the declaration and wrap a text stream (544–588). Its
ordinary branch can first be replaced by a FileSource.File hook (652–662).
openXmlFileStream opens binary bytes, detects encoding with a disclosure-system
default, decodes the full content and can strip the XML declaration before
returning StringIO (931–957). Original byte offsets cannot be measured on that
transformed text. Archive receipts also retain the container hash, selected
member name and separator normalization (863–878).

Declaration removal has two paths: stripDeclarationBytes inspects the first
120 bytes for UTF-8-like input, while non-UTF-8 input is decoded and passed to
stripDeclarationText; the latter uses XmlUtil's pattern and rejects a matched
declaration preceded by whitespace (959–980; XmlUtil 29). Record the selected
path and input/output identities. For a Unicode parser stream, hash a declared
serialization of its code points and label it as text identity, not original
file bytes. No parser-consumed stream has been observed in this work.

XmlUtil.encoding checks FF FE before FF FE 00 00 (146–160). Consequently, at
the inspected source-branch level, an input beginning FF FE 00 00 meets the
earlier UTF-16 return before the UTF-32 return. This is an ordering finding,
not a tested downstream failure or a general encoding verdict. The retained
filing's actual byte encodings and future decoder behavior require their own
checks. Do not silently endorse this helper as an encoding oracle.

## Parsing and additional resource discovery

ModelObjectFactory.parser explicitly sets recover=True, huge_tree=True and
resolve_entities=False (44–51). ModelDocument subsequently records entries
from the parser error log (200–208). A returned tree therefore does not suffice
for the adapter's proposed clean-XML outcome: preserve parser diagnostics and
reject that outcome when syntax recovery is reported. Keep recoverable source
material separate from admitted semantic readings. This requirement does not
assert that the retained fixture had a syntax error or that Arelle accepted one.

The constructor does not explicitly set every lxml/libxml2 option. Exact
library/build defaults, resource limits and whole-process network behavior
remain unverified. In particular, resolve_entities=False alone cannot certify
all other file-opening paths. DiscoveringClassLookup can call
ModelDocument.loadSchemalocatedSchema for an unfamiliar namespace with a
schema-location hint (ModelObjectFactory 171–202). Discovery during parsing
must use the same proposed URI-to-byte accounting as top-level imports.

## Mapping is a sequence of decisions

FileSource.isMappedUrl also asks the disclosure system; mappedUrl uses the first
matching source prefix and then disclosure-system mapping (494–511). The
earlier ModelDocument branch labels alone therefore do not describe independent
mapping alternatives. openFileStream can apply a package mapping or disclosure
mapping again, then consult WebCache for HTTP input (880–900). Record each
actual decision and intermediate URI/path. Reject an undeclared final-byte
substitution even when the initial logical target was correct.

PackageRegistry forwards map/is_mapped to PackageManager. The manager selects
the longest matching prefix, with an early return for an already-mapped URL
(package_manager 709–729). FileSource uses first-match order. DisclosureSystem
uses an exact file mapping before its first matching path prefix (511–529).
These rules are different: a future mapping compiler must preserve the source
mechanism and effective order; it cannot impose one generic prefix rule.

DisclosureSystem.loadMappings parses its configured mapping document and calls
xinclude (493–510). FileSource.openFileStream has a server-cache branch that
can call WebCache.retrieve (900–919). These source paths require explicit
configuration/disposition and later observed behavior. Their existence does
not establish that the selected local native path enters them.

## Requested and effective state

PackageManager.py and PluginManager.py are compatibility wrappers; the inspected
implementations live in packages/_package_manager.py and
plugin_system/_plugin_manager.py. The provider/registry wrappers have also been
read. Plugin hooks are drawn from enabled configured modules and can trigger
loading when requested (plugin_manager 675–698). Plugin and package close/reset
behavior remains separate from a command-line argument being empty.

The selected Session path closes the global managers, supplies an empty preload
dictionary and creates CntlrCmdLine. Its constructor passes hasGui=False; Cntlr
passes that flag to package/plugin configuration loading. Empty plugins and
packages do not enter the corresponding truthy options blocks. This source
chain narrows the prior uncertainty: persistent GUI package/plugin loading is
not requested by this new-controller route. It does not certify effective
runtime state, all controller reuse paths or absence of internal hooks. Retain
the effective-state receipt duty and exact configuration/build identities.

UrlUtil.splitDecodeFragment splits once at # and UTF-8 unquotes the fragment
(58–62). The preceding bounded graph examples contain only plain fragments.
Keep their narrower scope; do not extend them to percent-encoded fragments
without explicit source-token and decoded-ID cases.

## Consequence for the twelve lock duties

Source preparation has advanced for decoder/parser, mapping, effective
configuration and network-path duties. Their runtime values stay unresolved.
The other duties—target/Python, distribution, transitive/build/native identities,
actual opens, validation/translation and terms—remain unchanged. No exact lock,
runtime equivalence, accounting admission or distribution permission follows.
