# Devlens Bangladesh website

Live site: https://devlensbd.pages.dev (Cloudflare Pages, built with Astro).
Every push to the `main` branch rebuilds and publishes the site.

## Where content lives
- `src/data/posts/*.json`: one file per story (slug, date, title, excerpt, categories, tags, image, HTML content).
- `src/data/pages/*.json`: About, Funding, Data and the other fixed pages.
- `src/data/jobs.json`: job listings and job sectors. Jobs past their deadline disappear on their own in visitors' browsers and are left out of the next build.
- `src/data/home.json`: lead story, "Also today", Devlens Special, homepage numbers and funding deadlines.
- `public/media/YYYY/MM/`: all images. Reference them as `/media/YYYY/MM/file.jpg`.

## Cloudflare Pages settings
- Build command: `npm run build`
- Build output directory: `dist`

## Automatic humanitarian figures (HDX)
- `scripts/fetch-hdx.py` pulls Rohingya refugee numbers and response-appeal funding from the Humanitarian Data Exchange into `src/data/indicators.json`. The Data page shows them in their own table.
- `.github/workflows/hdx.yml` runs it every morning. It needs a repository secret named `HDX_APP_IDENTIFIER` (free, generated at https://hapi.humdata.org/docs).
