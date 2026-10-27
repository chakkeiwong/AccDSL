# DeclaredCompanyText/1 authoring contract

MC13–18/23–26/28/32/34/35; bounded S2–S5 reference. The text authors the
operation sequence, not the imported opening, method algorithms, schemas or map.
Four exact imports separately identify opening, schemas, registry and mapping.
Each is addressed by canonical-content SHA256 and supplied through a data-only
imports dictionary. No filesystem lookup, network, callback or implicit default.

Grammar: one semicolon-terminated declaration per nonblank line. Quoted tokens
are strict JSON strings; values are a string or Boolean only, never numeric JSON
literals, objects or arrays. No comments. Blank lines, UTF-8 and CRLF follow the
existing bounded lexer. There is no expression evaluation or Python code.

company_program "DeclaredCompanyText/1" "name";
import_opening "sha256";
import_schemas "sha256";
import_registry "sha256";
import_mapping "sha256";
event "identity" method "method_key" on "YYYY-MM-DD";
  input "name" known "rational/text/date" because "provenance";
  input "name" known true because "provenance";
  input "name" unknown "reason" because "provenance";
end_event;
report "identity" at "YYYY-MM-DD";
  equity "movement_id" event "event_id" on "date" account "account_id" amount "rational" because "description";
  note "id" label "label" status "missing|unsupported|unresolved" because "reason";
end_report;
carry "identity" at "YYYY-MM-DD";
  retained_account "account_id";
  next_end_exclusive "YYYY-MM-DD";
  memory "pointer" preserve because "provenance";
  memory "pointer" next_period_start because "provenance";
  memory "pointer" reset value because "provenance";
  equity ...;
  note ...;
end_carry;
end_program;

Events/reports/carries occur in any authored sequence up to64 commands; required
imports occur once in the displayed order. Each input/memory pointer occurs at
most once per command. All carry singleton fields are mandatory. Empty equity
and note lists are the explicit contents of their command blocks, not invented
facts. Empty memory policy lists are preserved and fail at runtime if required.
Command identity reuse remains an engine refusal with an exact successful prefix.

The parsed typed authoring record contains profile,name,imports,commands. Event
input type is resolved from the selected imported registry entry. Reset type is
resolved from the declared opening memory leaf; fixed schema is an engine
restriction. These are required declared types, not guessed quantities or units.
The compile result records both resolved program and import dependencies. No
methods, accounts, values, policies or future hashes are synthesized. Conversion
from an engine program checks exact input/reset type correspondence before
removing redundant type declarations. Round-trip must reproduce the entire engine
program canonically, including unknown reasons, notes and provenance strings.

Parse errors carry physical line and character offset. Semantic import/compile
errors carry their stage and applicable import or command location when available.
Source hash and command/field spans accompany successful text compilation. The
underlying engine performs structural validation before execution and dynamic
findings at the actual command turn. Compiler validation cannot promote fiscal
completeness, admission, durable execution, or broader language coverage.
