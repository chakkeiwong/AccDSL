# Pinned dynamic helpers found by relocation

Attempt-01 passes bundle integrity but cannot import MethodInputBinding/1:
company-portable-authoring-20261023/portable.py is absent. This module is loaded
through spec_from_file_location without registration in sys.modules, so a module
inventory alone misses it. Its companion company-path-admission helper is also
explicitly pinned by MethodInputBinding/1. Add the exact HELPERS keys and preserve
their original hashes in the bundle. Do not broaden external-file access or
change the financial engine. Keep attempt-01 and run fresh attempt-02.
