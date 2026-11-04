# Devlens Bangladesh website

Static site built with Astro and hosted free on Cloudflare Pages.

## How content is stored
- `src/data/posts/*.json`: one file per story (title, date, categories, image, HTML body).
- `src/data/pages/*.json`: About, Funding, Data and the other fixed pages.
- `src/data/jobs.json`: every job listing and the job sectors. Jobs past their deadline disappear on their own in visitors' browsers, and are left out of the next build.
- `src/data/home.json`: the lead story, "Also today", the Devlens Special, homepage numbers and funding deadlines.
- `public/media/`: images.

Every push to the `main` branch rebuilds and publishes the site on Cloudflare Pages.

## Cloudflare Pages settings
- Framework preset: Astro
- Build command: `npm run build`
- Build output directory: `dist`
- Environment variable (optional): `SITE_URL` = the site's final address

## One-time import from WordPress
In GitHub, open Actions, choose "Import from WordPress (run once)" and click "Run workflow". It copies every story, page and image from devlensbangladesh.wordpress.com into this repository.
