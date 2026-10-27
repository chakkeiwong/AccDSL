# Assumption information for a company path

A source’s publication date cannot establish when the simulation assumptions were chosen. CompanyInformationDraft/1 therefore identifies every component of a path: its header and each complete annual definition. Each component has its own authored, published, ingested and accepted times. These declarations bind exact content, so changing one annual input requires fresh timing evidence for that year.

An investor-information query requires an eligible source view and an eligible public publication time for every path component. A system-as-of query instead requires the authored content to have been ingested and accepted. Public availability and internal system history answer different questions. A fiscal period never supplies either timestamp. If a date is missing, unverifiable or later than the cutoff, the result stays unresolved or ineligible. A calendar-day publication that overlaps the authorship day cannot establish which came first.

The test clocks are intentionally synthetic. The verifier obtains them from a trusted local fixture and checks content hashes, cutoff boundaries, chronology, exact component coverage and a trusted semantic replay of the joined exchange. The declaration itself cannot certify its author or turn the clock into a real observation. The 103 checks support only synthetic temporal-selection behavior; historical source vintages and forecast admission remain absent.

Evidence: data/accounting-master/company-information-20261023/result.md.
