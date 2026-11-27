# Homepage rules (src/data/home.json)

## Lead (`lead`)
- The site updates once a day at 8:00 am Dhaka (owner decision, 26 Nov 2026). Each run sets a new lead.
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
- Optional `compare` draws two bars under the figure when the source gives an earlier value: {`beforeLabel`, `before` (number), `beforeText`, `nowLabel`, `now` (number), `nowText`}, e.g. "A year earlier" 46 / "46%" against "Now" 55 / "55%". Use it only when both values come from the same source.
- When a number is added, `pills.keyNumbers` goes up by one. When a research summary or report story is added, `pills.newReports` goes up by one. `pills.fundingOpen` = open items on the funding page.

## Funding box (`funding`)
- Items with `title`, `funder`, `deadline` (YYYY-MM-DD), `url`. Remove items past their deadline; keep it in step with the funding page.

## Devlens Special (`special`, `pinnedSpecials`)
- See `devlens-specials-pipeline.md`.
- When the lead is itself the newest Special, the homepage Special box shows the previous Special so the same photo doesn't appear twice.

## Design (28 Nov 2026)
- Headlines use Source Serif 4; body and labels use Manrope. Green is the only brand colour; orange is for urgent items (deadlines, helplines, campaigns).
- The homepage no longer has Latest stories or a separate Closing soon section (owner requests, 28 Nov 2026; the jobs section now has Closing soon and Featured tabs, jobs only), Fresh evidence, Sector toolkit or the Share-your-work box; stories beyond "More from today" are reached through News and the category pages; Research and Resources are reached from the menu and footer.

## Spotlight (`spotlight`)
- For time-limited events (e.g. COP31). It shows between `start` and `until`. Update `today` during the event.
- Optional fields: `theme` ("orange" gives the orange campaign colours), `todayLabel`, `watchLabel`, `linksLabel` (section headings), and `strip` ({`text`, `url`, `help`, `helpUrl`}), which shows a slim coloured bar under the header on every page while the spotlight runs.

### 16 Days of Activism (owner request, 26 Nov 2026): update EVERY run until 10 December 2026
The orange spotlight `16days-2026` runs from 25 November to 10 December 2026 (theme "Ensure justice, protect survivors, end impunity"). It hides itself after 10 December; do not delete it before then. Every daily run (8:00 am Dhaka):
1. Research fresh 16 Days content from the last 24 to 36 hours: campaign events and statements (Ministry of Women and Children Affairs, UN Women, UNFPA, UN in Bangladesh, embassies), NGO and rights-group activity (MJF, BLAST, ASK, Odhikar, Naripokkho, Bangladesh Mahila Parishad, BRAC, ActionAid, Plan, Care and others), new data on violence against women and girls (police, ASK, Odhikar, BBS, One-Stop Crisis Centres, 109 helpline), court cases, law and policy changes, Rohingya camp GBV, and Bangla press coverage.
2. Publish at least one new story on it each day (more when there is news), tagged `gender-based-violence-gbv-prevention-and-response` plus other fitting tags, with a NEW photo (free-licence route; PID photos of official 16 Days events are fine). Add each new slug to the FRONT of `spotlight.stories`.
3. Rewrite `spotlight.today`: set `date` to today ("27 Nov"), write 3 to 5 sentences on what happened since the last update, with `sources` (name and URL; Devlens stories may be linked as "/YYYY/MM/DD/slug/"). Never repeat yesterday's text.
4. Do not add a "What to watch" block to this spotlight (owner decision, 26 Nov): keep `spotlight.watch` as an empty list. Update `strip.text` and `strip.url` to point to the newest 16 Days story.
5. Key dates to cover: 29 November (International Women Human Rights Defenders Day), 3 December (International Day of Persons with Disabilities, link to violence against women with disabilities), 9 December (Begum Rokeya Day, Rokeya Padak), 10 December (Human Rights Day, campaign close). On 10 December publish a wrap-up of the 16 days.
6. Keep the help links (109, 999) in `spotlight.links`. The data panel (`spotlight.data`) replaces "What to watch": every item needs `value`, `label`, `url` (the ORIGINAL source: report PDF, official release or the news report that first published it) and `source` (short name). Update or add items when new official figures appear. Facts only from sources; follow devlens-writing-standard.md.
7. After 10 December, leave the data in place (the site hides it) and stop these updates.

## Events page (owner request, 26 Nov 2026): update EVERY run
The Events page (`/events/`) is built from `src/data/events.json` by `src/pages/events.astro`. The page sorts each event into "Happening now", "Coming up" or "Recent events" by today's Dhaka date, so do not move items by hand. Every run:
1. Research events for the next 60 days that matter to Bangladesh's development sector: conferences, dialogues, report launches, consultations and comment deadlines, trainings and webinars, donor and UN meetings, campaigns, and international or national days (for example World AIDS Day, Human Rights Day, International Migrants Day, Begum Rokeya Day, International Mother Language Day, International Women's Day, World Health Day, World Environment Day, World Refugee Day). Sources: UN agencies in Bangladesh, ministries and PID, NGO and think-tank sites (CPD, BIDS, SANEM, BIGD, ICCCAD, icddr,b, MJF, TIB, BLAST, ASK and others), university and conference sites, and newspaper reports ("will be held", "to be held", "set to host").
2. Add each new event to `events.json` with `id` (unique, kebab-case), `start` and `end` (YYYY-MM-DD; the same date for a one-day event), `kind` (Conference, Dialogue, Workshop, Launch, Consultation, Campaign, Observance, National day, Deadline, Summit, Court ruling, Meeting), `place`, `title`, `organiser`, `summary` (one or two plain sentences: what it is and why it matters to NGOs), `url` (the organiser's own page or the news report that announced it) and `source` (short name). Only list events confirmed by a named source; never guess dates.
3. When Devlens publishes a story about an event (before or after it), add the story's slug as `coverage` (and optionally `coverageLabel`). The build fails if the slug does not exist, so check it.
4. When an event has happened, rewrite its `title` or `summary` to say what came out of it (decisions, figures, quotes from the source) and add the Devlens story as `coverage`.
5. Add notable events that Devlens covered in the last day (dialogues, launches, conferences) to `events.json` so "Recent events" stays current. The page shows the 12 most recent.
6. Remove events that ended more than 60 days ago. Set `updated` to today's date.
7. Keep at least 8 upcoming events listed. If there are fewer, search wider (regional events with Bangladesh participation, webinars, international days).

## Search (SEO) rules for every story (owner request, 26 Nov 2026)
The site already outputs titles, descriptions, social cards, structured data (NewsArticle, BreadcrumbList, organisation), the sitemap, the Google News sitemap (`/news-sitemap.xml`, last two days) and IndexNow pings to Bing after each push. Writers only need to get the content fields right:
- Headline: 65 characters or fewer, with the main search words early (the place, organisation, number or topic people will search for), e.g. "Measles deaths pass 1,300 in Bangladesh". No clickbait.
- Excerpt: 120 to 155 characters. It is the snippet Google shows, so say the key fact plainly and include the main topic words.
- Slug: short, lowercase, hyphenated, keywords only (5 to 9 words). Never change a slug after publishing.
- Image `alt`: describe what the photo shows and where (e.g. "Health workers vaccinate children at a clinic in Sylhet"). Never leave it empty.
- Tags: 3 to 6 fitting sector and sub-sector tags from the NGOAB list.
- Internal links: link 2 or 3 earlier Devlens stories on the same topic inside the story text, and link the matching Jobs, Funding or Events page where it fits.
- Use the full names people search for at first mention (e.g. "Rohingya refugees in Cox's Bazar", "NGO Affairs Bureau (NGOAB)").

## Scheduled stories and leads (26-27 Nov 2026)
- A post may carry `publishAt` (ISO time, Dhaka). It stays out of the site (pages, homepage, sitemap, feeds) until the first build after that time.
- `home.json` may carry `scheduledLead` = {`from`, `slug`, `label`, `headline`, `summary`, `special`}. From the first build after `from`, the site shows it as the lead (and as the Devlens Special when `special` is true); the previous lead becomes the main "Also today" item and the old main item moves to the front of `plus`.
- The workflow `scheduled-publish.yml` rebuilds the site at 08:02 and 08:32 Dhaka when a scheduled time has just passed.
- The daily run, when it finds a `scheduledLead` whose time has passed: make it the real `lead` in home.json (and `special` if `special` is true), move the previous lead to Also today as above, delete `scheduledLead`, and remove `publishAt` from the post. Do NOT replace that lead in the same run; the run's own top new story goes into Also today. If the time has not yet passed, leave both untouched.
- 27 Nov 2026: the Devlens Explainer "Bad COP, worse COP: what COP31 left Bangladesh" is scheduled as the lead and Devlens Special from 07:55 (owner request). Keep it as the lead for the whole of 27 November.

## Photos (owner rule, 26 Nov 2026)
- Every story published on the site must have a photo. Never leave `"image": null`. If the first search fails, search again with broader terms (the place, the institution's building, the sector) and use a free-licence file photo with a "File photo" credit.

## Always
- Keep the Beta label (in `src/layouts/Base.astro`). Do not remove it.
- The site date comes from the build. Push at least once a day so it stays current.
- After editing, check the built `dist/index.html` shows the new lead.

## Spotlight format (concise, from 27 Nov 2026)
- `today.headline`: one line, at most 80 characters, says what happened today.
- `today.text`: at most two sentences (about 300 characters). One fact or quote, one figure. No background paragraph.
- `today.sources`: two at most, external source first.
- Stats: mark the four strongest with `"highlight": true` and give each a `short` label (under 45 characters). Everything else sits under "more figures".
- New Devlens stories go at the front of `stories`. The first one is shown with its photo.
- Help numbers go in `links` with `tel:` URLs and appear in the orange help box. Other links appear as "Follow the campaign" pills.

## Devlens Special section (automatic)
- The newest live post in the `devlens-special` category is shown as a news card with photo. The next five appear as links under "Earlier specials".
- No home.json edit is needed. A special with a future `publishAt` stays hidden until it goes live.
