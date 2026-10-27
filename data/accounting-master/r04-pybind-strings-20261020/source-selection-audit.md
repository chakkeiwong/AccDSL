# Selected source audit

Both official commit responses resolve the named tags and identify their trees.
Neither recursive tree is truncated. Six selected blob paths exist and are
smaller than the 2 MiB bound. cast.h contains the argument caster; pytypes.h
contains the compatibility/helper definitions; strings.rst is the same-version
public contract. Read only the relevant source spans and record their limits.
Two additional official Python 3.10 C API pages explain the UTF8/bytes API
semantics. These pages are dated acquired documentation, not pinned CPython
implementation and not evidence of installed-runtime behavior.

v2.2.0 resolves to 2a5a5ec0a47c245fbf1bb1a8a90b4c3278e01693;
v2.11.1 resolves to 8a099e44b3d5f85b20f05828d919d2332a8de841.
Their source commit dates are 31 August 2017 and 17 July 2023. v2.11.1 is a
chronologically eligible comparator only; no build-identity inference follows.
