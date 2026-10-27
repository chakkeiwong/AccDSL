# Bounded forward discovery

18 October 2026. One OpenAlex query was executed:
`https://api.openalex.org/works?filter=cites:W4291327732&sort=cited_by_count:desc&per-page=8`.
Its retained `sources/dm1995-citing-openalex.body` reports count 5148 and returns
these eight records. These are metadata candidates, not technically read
sources. The selection favors citation counts and is not a recent-work search.

| Returned title / year / citations in this response | Disposition |
|---|---|
| Deep learning with long short-term memory networks for financial market predictions / 2017 / 2799 | EMPIRICAL_EXAMPLE; deferred/outside this scalar-to-panel method unit |
| Consumption, Aggregate Wealth, and Expected Stock Returns / 2001 / 2182 | EMPIRICAL_EXAMPLE; deferred domain application |
| Testing the equality of prediction mean squared errors / 1997 / 2075 | DIRECT_METHOD, already source-blocked as HLN97; no duplicate source support |
| A Reality Check for Data Snooping / 2000 / 1838 | COMPETITOR; deferred primary reading; relevant to selection/multiple-comparison control |
| Probabilistic Forecasts, Calibration and Sharpness / 2007 / 1763 | DIRECT_METHOD/background for scores/calibration; not a verified panel uncertainty procedure here |
| Electricity price forecasting: A review of the state-of-the-art with a look into the future / 2014 / 1639 | SURVEY_OR_TUTORIAL; deferred domain survey, not primary inference support |
| Forecasting the Equity Risk Premium: The Role of Technical Indicators / 2014 / 998 | EMPIRICAL_EXAMPLE; deferred domain application |
| Forecasting: theory and practice / 2022 / 936 | SURVEY_OR_TUTORIAL; deferred broader survey |

Identifiers and DOI strings remain in the raw response. No conclusions about
the papers' technical methods follow from these titles. F26 was separately
discovered by an exact-title arXiv API response while resolving the blocked
retrospective; its matching primary text was then read. That is a new-source
discovery, not evidence that it appeared in this eight-item citing list.

No bounded forward query for HLN97, D15 or F26, nor a systematic recent-work,
replication or correction search, was completed. The finite retrieval budget
is closed. Broader scholarly survey readiness is not established. Those limits
block a comprehensive-literature claim, not completion of this narrow source
disposition or other independent internal work.
