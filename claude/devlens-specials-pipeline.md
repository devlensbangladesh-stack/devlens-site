# Devlens Specials pipeline

A Devlens Special is a longer original report on one issue that matters to the NGO sector, for example "Aid cuts are pushing Bangladesh's NGOs from services to lending" (13 November 2026).

## When
- About one a week. A scheduled run should not publish a Special unless the owner has asked for that topic; it can propose one in the final report instead.

## Choosing a topic
- A trend across several recent stories, a new study or official dataset, or a question NGOs are asking (funding, regulation, staffing, safety).
- There must be enough verifiable evidence: official data, published research, on-record interviews or public statements.

## Writing
- 1,200 to 2,000 words. Follow `devlens-writing-standard.md`.
- Sections: intro (the finding in two or three sentences), the evidence, what it means for NGOs and donors, what could change, limits of the evidence, sources.
- Every figure attributed and linked.

## Publishing
- Post JSON with categories `["devlens-special"]` (Specials are kept out of the homepage "latest" list).
- Set `home.json` `special` to `slug`, `label` ("Special report · Topic"), `headline`, `summary`, `published` (YYYY-MM-DD).
- Move the previous Special into `pinnedSpecials` (same fields) so it shows under "Previous special reports".
- A Special needs an image before it goes live (see `devlens-needs-images.md`).
