# Attempt 01: fixture-envelope mismatch

The checker passed the stored selection transport envelope to the native
program API, which correctly returned invalid_program / fields:program_selection.
The fixture contains selection and expected_sha256; the native API requires
those as separate arguments. This is a checker input error, not a financial
runtime regression. Attempt 02 reads both exact stored fields and verifies
their digest before execution. No native implementation or expected result
is changed, and the failed attempt remains preserved.
