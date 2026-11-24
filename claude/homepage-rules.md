# Homepage rules (src/data/home.json)

## Lead (`lead`)
- The morning run sets a new lead. The afternoon run changes it only for a bigger story.
- NGO and development stories always take priority over politics or business.
- Fields: `slug`, `label` ("Sector · Topic", e.g. "Labour · Garments"), `headline`, `summary` (one or two sentences).
- When a running story moves on (e.g. a new figure), publish a new story and make it the lead rather than rewriting the old one.

## Also today (`alsoToday`)
- The main item (`slug`, `label`, `headline`, `summary`) is the second most important story of the day.
- The previous lead moves into Also today. If the new lead replaces it on the same topic, put the old lead into `plus` instead of the main item.
- `plus` is a list of slugs. New stories go to the front, newest and most important first; the homepage shows the first 6. Keep older slugs after them and do not duplicate any.

## Key numbers (`numbers`) and pills
- Three items, newest first: `value`, `label` (one sentence), `source` ("Organisation, Mon YYYY").
- Only official figures or figures from named research institutes, never from opinion pieces.
- When a number is added, `pills.keyNumbers` goes up by one. When a research summary or report story is added, `pills.newReports` goes up by one. `pills.fundingOpen` = open items on the funding page.

## Funding box (`funding`)
- Items with `title`, `funder`, `deadline` (YYYY-MM-DD), `url`. Remove items past their deadline; keep it in step with the funding page.

## Devlens Special (`special`, `pinnedSpecials`)
- See `devlens-specials-pipeline.md`.

## Spotlight (`spotlight`)
- For time-limited events (e.g. COP31). It shows between `start` and `until`. Update `today` during the event.

## Always
- Keep the Beta label (in `src/layouts/Base.astro`). Do not remove it.
- The site date comes from the build. Push at least once a day so it stays current.
- After editing, check the built `dist/index.html` shows the new lead.
