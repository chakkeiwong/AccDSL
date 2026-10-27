# Combined source verification repairs

26 October 2026. All 30 full program comparisons passed before a negative
fixture expected the wrong parser diagnostic. Removing the first recipe-end
delimiter lets the embedded parser encounter content after its own end marker;
the correct diagnostic is declaration_after_end. The fixture now requires that
diagnostic and continues to check its parent source location. This is a fixture
expectation repair, not a runtime or saved-result change.
