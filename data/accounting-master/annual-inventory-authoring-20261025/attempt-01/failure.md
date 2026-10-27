# Smoke failure and repair trigger

The first single-sale compilation failed before financial execution with
method_requirements_v1.Invalid: fields:provenance, wrapped as authoring.Invalid.
The new implementation incorrectly reused the tax declaration validator for
inventory findings. Tax declarations require structured provenance; the frozen
RecoveredLotSale/1 requires a nonempty provenance string. The schemas differ.
Repair the optional finding validator to match the frozen inventory event exactly,
while retaining tax validation for old operations. Do not rewrite supplied
provenance, relax the frozen evaluator or claim the original compiler passed.
The saved source is the failed implementation. No evidence was recorded.
