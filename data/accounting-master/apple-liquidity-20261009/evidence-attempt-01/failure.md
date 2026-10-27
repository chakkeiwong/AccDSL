The first evidence-helper attempt stopped before table calculation because it
assumed the tax unit used `calculations.json`. That unit uses `tax-bridges.json`.
The script and already extracted source excerpts are preserved here. The next
attempt corrects only the dependency filename; no frozen source/unit is changed.
