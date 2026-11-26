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

If no photo of the event itself is available, use any other publicly available photo that is public domain or under an open licence (CC0, CC BY, CC BY-SA), for example from Wikimedia Commons, Openverse, Flickr Commons or government sources such as PID. A general photo of the subject is fine (e.g. a factory floor for a wage story, a clinic for a health story); for a running story, start the credit with "File photo". Rules that still apply:
- Credit the author and licence and link to the source page.
- Never reuse an image already on the site; use a new file path.
- Do not use photos marked NC (non-commercial) or ND (no derivatives), and do not use newspaper or agency photos (see `devlens-needs-images.md`).
- The lead never goes out without a photo.

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
- Optional fields: `theme` ("orange" gives the orange campaign colours), `todayLabel`, `watchLabel`, `linksLabel` (section headings), and `strip` ({`text`, `url`, `help`, `helpUrl`}), which shows a slim coloured bar under the header on every page while the spotlight runs.

### 16 Days of Activism (owner request, 26 Nov 2026): update EVERY run until 10 December 2026
The orange spotlight `16days-2026` runs from 25 November to 10 December 2026 (theme "Ensure justice, protect survivors, end impunity"). It hides itself after 10 December; do not delete it before then. Every run, morning and afternoon:
1. Research fresh 16 Days content from the last 24 to 36 hours: campaign events and statements (Ministry of Women and Children Affairs, UN Women, UNFPA, UN in Bangladesh, embassies), NGO and rights-group activity (MJF, BLAST, ASK, Odhikar, Naripokkho, Bangladesh Mahila Parishad, BRAC, ActionAid, Plan, Care and others), new data on violence against women and girls (police, ASK, Odhikar, BBS, One-Stop Crisis Centres, 109 helpline), court cases, law and policy changes, Rohingya camp GBV, and Bangla press coverage.
2. Publish at least one new story on it each morning (more when there is news), tagged `gender-based-violence-gbv-prevention-and-response` plus other fitting tags, with a NEW photo (free-licence route; PID photos of official 16 Days events are fine). Add each new slug to the FRONT of `spotlight.stories`.
3. Rewrite `spotlight.today`: set `date` to today ("27 Nov"), write 3 to 5 sentences on what happened since the last update, with `sources` (name and URL; Devlens stories may be linked as "/YYYY/MM/DD/slug/"). Never repeat yesterday's text.
4. Do not add a "What to watch" block to this spotlight (owner decision, 26 Nov): keep `spotlight.watch` as an empty list. Update `strip.text` and `strip.url` to point to the newest 16 Days story.
5. Key dates to cover: 29 November (International Women Human Rights Defenders Day), 3 December (International Day of Persons with Disabilities, link to violence against women with disabilities), 9 December (Begum Rokeya Day, Rokeya Padak), 10 December (Human Rights Day, campaign close). On 10 December publish a wrap-up of the 16 days.
6. Keep the help links (109, 999) in `spotlight.links`. The data panel (`spotlight.data`) replaces "What to watch": every item needs `value`, `label`, `url` (the ORIGINAL source: report PDF, official release or the news report that first published it) and `source` (short name). Update or add items when new official figures appear. Facts only from sources; follow devlens-writing-standard.md.
7. After 10 December, leave the data in place (the site hides it) and stop these updates.

## Photos (owner rule, 26 Nov 2026)
- Every story published on the site must have a photo. Never leave `"image": null`. If the first search fails, search again with broader terms (the place, the institution's building, the sector) and use a free-licence file photo with a "File photo" credit.

## Always
- Keep the Beta label (in `src/layouts/Base.astro`). Do not remove it.
- The site date comes from the build. Push at least once a day so it stays current.
- After editing, check the built `dist/index.html` shows the new lead.
