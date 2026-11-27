# Devlens job sources

Up to 10 new jobs per run. Check a rotating subset of the sources below (not all every run) and note which ones in the run log.

## Aggregators (check most runs)
- ReliefWeb Bangladesh jobs: RSS `https://reliefweb.int/jobs/rss.xml?advanced-search=%28C31%29` (the API returns 403 without an approved appname)
- Impactpool (IRC, NRC, DRC, UNHCR, IOM, UNOPS, CIMMYT, GiveDirectly, EU Delegation)
- UNjobs.org Bangladesh (FHI 360, Winrock, Ipas, Heifer, IOM, Fred Hollows)
- unvacancies.org (UNHCR, UN Women, World Bank)
- Bangladesh NGO job boards: nextjobz.com.bd, dohaj.com, alokitojobs.com, bdrecruit.net, students.bd

## Careers pages (rotate)
- UN: UNICEF (jobs.unicef.org), UNDP, UNFPA, WFP, WHO, UNHCR, IOM, ILO, UN Women, UNOPS
- Lenders and donors: World Bank (worldbankgroup.csod.com), ADB, JICA, EU Delegation, FCDO, GIZ
- International NGOs: Save the Children, Plan International, ActionAid Bangladesh, IRC, NRC, DRC, CARE, Oxfam, World Vision, HELVETAS, MSF, The Asia Foundation, Winrock, FHI 360
- National NGOs and institutes: BRAC, icddr,b, Dhaka Ahsania Mission, SAJIDA Foundation, Rupantar, NGO Forum for Public Health, Pulse Bangladesh, Mukti Cox's Bazar, WAVE Foundation, PKSF, TIB, BIDS

## Rules
- Only jobs based in Bangladesh, or regional roles that can be based in Bangladesh.
- Open the original advert and confirm title, organisation, location and deadline. Link to the employer's own page when it exists.
- Skip duplicates (check `url` and `ref` in `src/data/jobs.json`).
- Remove jobs whose `deadline` is before today. Jobs with no deadline: remove after 30 days from `added`.

## Schema (src/data/jobs.json, `jobs` list)
```json
{
  "title": "Media and Advocacy Consultant, 12 months",
  "org": "UNICEF",
  "badge": "UNICEF",
  "sector": "development-cooperation",
  "url": "https://jobs.unicef.org/en-us/job/597003",
  "location": "Dhaka (office-based with travel)",
  "nationals": true,
  "consultancy": true,
  "contract": "National consultancy · 12 months",
  "ref": "Ref: UNICEF 597003",
  "deadline": "2026-11-26",
  "deadlineText": "26 November 2026",
  "button": "View advert",
  "added": "2026-11-19",
  "featured": "UN AGENCY"
}
```
- `sector`: one of the ids in `jobs.json` `sectors`.

## Job pages and Google for Jobs (do this for every new job)
A job with a `description` gets its own page at `/jobs/<slug>/` with schema.org JobPosting data, so it can show in Google's job search. Jobs without one stay on the list only and get no search traffic. So for every new job, while the advert is open:
- `description` (required for a page): the advert's own job description as simple HTML (`<p>`, `<ul>`, `<li>`, `<strong>`, `<h3>`): purpose, responsibilities, qualifications, how to apply. Copy it from the advert; do not write or pad it. Leave out the employer's boilerplate about benefits only if it is very long. Needs at least 60 words or no page is built. If the advert is a PDF or image only, skip the field.
- `posted`: the date the advert was published, `YYYY-MM-DD`, when the advert shows it. Otherwise leave it out and `added` is used.
- Optional, only when the advert states it: `employmentType` (`FULL_TIME`, `PART_TIME`, `CONTRACTOR`, `TEMPORARY`, `INTERN`, `VOLUNTEER`; consultancies default to `CONTRACTOR`), `city` (the duty-station town, if `location` is vague), `remote: true` (fully home-based in Bangladesh), `salary` (`{"min": 80000, "max": 120000, "currency": "BDT", "unit": "MONTH"}`), `orgUrl` (employer's homepage), `summary` (one or two plain sentences for the top of the page).
- Never invent a description, salary or date. Google penalises job data that does not match the advert.
- Do not change a job's `title`, `badge` or `url` after it is added: the page address is built from them. If one must change, set `"id"` to the old slug (shown in the page URL) to keep the address.
- `featured`: optional, `"UN AGENCY"` or `"NATIONAL NGO"`.
- Copy the field set of an existing job of the same kind; omit optional fields rather than inventing values.
