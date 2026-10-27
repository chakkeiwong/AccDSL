# Preflight repair

The first verification command stopped during import, before any financial
checks, because the policy-switch row used asset_oci twice: once for the
period return and once for its cumulative balance. Renamed the period field
period_asset_oci; asset_oci retains the cumulative amount used in the independently
authored targets. The failure was SyntaxError: keyword argument repeated:
asset_oci at reference.py line155. No financial attempt or result was produced.
