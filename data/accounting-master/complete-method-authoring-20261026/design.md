# CompanyMethodAuthoring/1

Text declares a complete CompanyBookMethod/1 and explicitly selects
CompanyBookTransition/1 or /2. It does not infer the book, event, schemas, source
authority or v2 memory type definition. Those remain separate compilation inputs.
All record fields are authored; none is selected from a Python method-name table.

Each declaration occupies one line and ends with a semicolon. Tokens use the
existing strict JSON/string lexer and prefix expression notation. JSON type,
binding and memory-template tokens are data records, not executable callbacks.
Duplicate declarations, unknown commands, extra fields and trailing text refuse.

Grammar (uppercase denotes a token or explicit expression):

    company_method PROFILE TRANSITION METHOD_PROFILE ID VERSION;
    context OBJECT;
    account_map ROLE ACCOUNT;
    begin_preconditions;
      <complete MethodRequirementExchange/2 text, original selected digest>
    end_preconditions;
    input_binding "preconditions" INPUT SOURCE_OBJECT;
    begin_monetary PROFILE METHOD_ID VERSION;
      money_input ID TYPE ROLE SOURCE_REF;
      calculation ID TYPE DEPENDENCIES EXPRESSION;
      money_account ROLE TYPE;
      cash_account ROLE;
      posting ID ACCOUNT_ROLE DEPENDENCIES EXPRESSION;
      flow ID ACTIVITY ORIGIN DEPENDENCIES EXPRESSION;
    end_monetary;
    input_binding "monetary" INPUT SOURCE_OBJECT;
    begin_memory PROFILE STATE_SCHEMA_DIGEST INPUT_SCHEMA_DIGEST;
      memory_input ID SOURCE_OBJECT;
      write ID OP PATH_LIST TEMPLATE_OBJECT;
    end_memory;
    begin_postconditions;
      <complete MethodRequirementExchange/2 text, original selected digest>
    end_postconditions;
    input_binding "postconditions" INPUT SOURCE_OBJECT;
    residual TEXT;
    end_method;

Top-level mapping/binding declarations may be reordered; list order inside
requirements, calculations, postings, flows, writes and residuals is preserved.
Each section and context occurs exactly once. Nested requirement exchanges must
have empty values and available_capabilities: this document authors declarations,
not event values or capability findings. The original requirement parser performs
their version selection and semantic validation. The method's prepare validator
still requires the native guarded profile and exact nested method identity.

Monetary expressions use ref, const, add, sub, mul and min. Syntax lowering adds
no evaluation; original MethodMonetaryEffects/1 checks types, dependencies,
forward references and financial dimensions. Native memory definitions are
compiled against the explicitly supplied schemas. v1 permits fixed scalar
replacement; v2 also checks typed insertion against memory_definition. The
same original prepare runs for text and typed methods in the identical book/event
environment. Compile-only output leaves every admission/execution flag false.

Source spans retain complete line text coordinates and a digest of each source
slice; semantic content identity excludes whitespace. The text source itself
has a separate exact digest. A successful parse without environment validation
is only lowered syntax, not a compiled financial method. Complete event effects
are compared separately through existing propose/apply, never during compilation.

Limits inherit the one-megabyte record/text bound and 4096-node/48-depth checks.
These are reference resource limits. No source trust, general method completeness,
new calendar, profile migration, runtime dispatch or accounting rule is implied.
