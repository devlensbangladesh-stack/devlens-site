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
- `featured`: optional, `"UN AGENCY"` or `"NATIONAL NGO"`.
- Copy the field set of an existing job of the same kind; omit optional fields rather than inventing values.
