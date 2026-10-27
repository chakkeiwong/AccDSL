# Correct the descriptive witness count

Attempt03 passes263 checks,42 queries,11 prefixes and all three retained native
histories. The loop used the full retained population, but the manifest's
descriptive data_version string incorrectly said two witnesses. The runner now
asserts the exact three-witness population and records it correctly. Preserve
attempt03 and run fresh attempt04; no algorithm or source fixture changes.
