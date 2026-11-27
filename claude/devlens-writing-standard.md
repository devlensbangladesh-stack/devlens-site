# Devlens writing standard

Devlens covers Bangladesh's development and NGO sector for people who work in it: NGO staff, donors, researchers, officials and journalists.

## Choosing stories
- Only content published in the previous 36 hours.
- Rank by relevance to development and NGOs: aid and funding, NGO operations and safety, health, education, labour, migration, gender, social protection, climate and disaster, Rohingya response, governance and rights, official data and research.
- Party politics, crime and business news only when there is a clear development angle.
- Skip anything already on the site (search `src/data/posts/` by topic and key figures).
- Each run needs at least one story from Bangla media and at least two from sources other than The Daily Star and The Business Standard.

## Fact checking
- Read the original article (and the original report or press release when it is online) for every story.
- Check names, titles, dates, figures, quotations and who said what.
- Attribute every claim: "the board chairman told reporters", "Prothom Alo reported".
- If a claim comes from one side only (a statement, a protest group, an allegation), say so, and say if Devlens could not verify it.
- If sources disagree on a figure, use the primary source (official, the speaker on record) and say which you used.
- Leave out anything that cannot be verified.
- When a published story turns out to be wrong, correct it in place, add a "Correction" section saying what changed, and update the homepage text if it repeats the error.

## Style
- Plain English, short sentences, active voice. No jargon, hype or opinion in news.
- First paragraph: who, what, when (day and date, e.g. "on Tuesday (24 November)"), source.
- Money: "Tk 15,700", "Tk 3.32 crore", "Tk 6 lakh", "$60 million", "CAD 45 million". Percentages: "44%".
- Dates: "24 November 2026". Use British spelling.
- Give people's full name and role on first mention.
- Bangla sources: translate headlines into English in the source list and mark "(Bangla)".

## News story structure (300 to 500 words)
1. Three to six paragraphs of facts, with attribution.
2. `Why it matters`: what it means for NGOs, communities and programmes.
3. `What to watch`: next decisions, dates or data.
4. `Sources`: list of links, "Outlet: Headline, D Month YYYY".

## Analysis and Research Summary (800 to 1,200 words, morning run)
- Title starts "Devlens Analysis:" or "Devlens Research Summary:", category `analysis`.
- Research Summary sections: intro, The source, Where things stand (if useful), Finding 1..n, What it means for the development sector, Limits of the evidence, The bottom line, Sources.
- Say plainly when Devlens relied on press reports and has not seen the full document.

## JSON (src/data/posts/<slug>.json)
Fields, in this order: `slug`, `date`, `modified`, `title`, `excerpt`, `categories`, `tags`, `image`, `content`.
- `slug`: lowercase, hyphens, descriptive, includes key figures. Never reuse a slug.
- `date`/`modified`: `YYYY-MM-DDTHH:MM:00`, Dhaka time.
- `excerpt`: one or two sentences, under about 200 characters.
- `categories`: from `src/data/categories.json` (usually `news`; `analysis`; add `data` for data stories).
- `tags`: NGOAB sectors and sub-sectors from `src/data/tags.json`, plus `national` or a place tag. Never invent a tag.
- `content`: HTML using `<p class="wp-block-paragraph">`, `<h3 class="wp-block-heading">`, `<ul class="wp-block-list">`. Links to outside sources use `target="_blank" rel="noopener"`. Internal links use `/YYYY/MM/DD/slug/`.
- `image`: see `devlens-needs-images.md`; `null` if no image yet.

## Story openings
- Start the body with the dateline paragraph (e.g. "DHAKA, 27 November 2026: ..."). Do not add a "DEVLENS ANALYSIS/EXPLAINER/SPECIAL · topic · date · byline" line or an italic summary at the top: the page already shows the categories, date, byline and excerpt above the story.
- Credit stories to "Devlens Bangladesh". Do not write "editorial team", "our editors" or "newsroom": Devlens does not have a team yet.
