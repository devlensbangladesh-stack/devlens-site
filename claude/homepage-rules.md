# Homepage rules (src/data/home.json)

## Lead (`lead`)
- The morning run sets a new lead. The afternoon run changes it only for a bigger story.
- NGO and development stories always take priority over politics or business.
- Fields: `slug`, `label` ("Sector · Topic", e.g. "Labour · Garments"), `headline`, `summary` (one or two sentences).
- When a running story moves on (e.g. a new figure), publish a new story and make it the lead rather than rewriting the old one.

## Lead photo (owner rule, 24 Nov 2026)
Every lead story must have a photo. Never publish or keep a lead with `"image": null`.
1. Write `photo-searches.json` with 2 to 4 searches for the lead (e.g. {"lead1": "garment factory Gazipur", "lead2": "sewing machine Bangladesh"}), commit and push it to main. The photos.yml workflow searches Wikimedia Commons and Openverse on GitHub (this works even when the cloud session cannot reach Commons) and pushes contact sheets and JSON to the `photo-candidates` branch.
2. When the branch updates (a few minutes), `git fetch origin photo-candidates` and read `<key>.json` and the numbered `<key>.jpg` contact sheet. Pick a landscape photo that fits the story and passes the checks in `devlens-needs-images.md` (licence, no identifiable politicians, no party posters, no identifiable children or victims).
3. Add the pick to `photo-queue.json` with the lead's `slug`, the candidate `url`, a NEW unique `path` under `/media/YYYY/MM/`, `alt`, `credit`, `creditUrl` and `focusY`, then push. The fetch job downloads and crops the photo and sets `image` on the post.
4. Open the saved file and the live lead to check it before finishing.

If no new photo fits:
- For a running story (one Devlens has covered before), use a new free-licence photo of the general subject, credit starting "File photo", e.g. a factory floor for a wage story. Never reuse an image already on the site.
- If there is still nothing usable, make the most important story that does have a photo the lead, put the photo-less story first in Also today, and say so in the run log and final report.

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
