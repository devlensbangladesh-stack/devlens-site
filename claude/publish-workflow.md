# Publish workflow

Repository `devlensbangladesh-stack/devlens-site`, branch `main`. Every push to `main` makes Cloudflare Pages rebuild https://devlensbd.org.

## 1. Start
- Append to `claude/devlens-run-log.md`: `- D Mon YYYY, HH:MM Dhaka, daily run, started` (note "fired late" if more than an hour off schedule).
- Attach the repo with push access (add_repo) if the session offers it; clone; `git fetch origin main` and work on top of `origin/main`.
- Apply any patches in `claude/pending/` with `git am` (oldest first). Delete them only after the site is live.
- Read `git log --oneline -15` to avoid repeating recent work.
- Test that sources are reachable (curl a few news sites). If none are, log the exact errors and stop; do not write from search snippets.

## 2. Lead photo
- The lead must have a photo before the run finishes. Follow "Lead photo" in `homepage-rules.md`. Check `image` on the lead post is not null before the final build.

## 3. Build
- Validate every JSON file in `src/data`.
- `npm install` if `node_modules` is missing, then `npm run build`. Fix every error before going on.
- Check `dist/index.html` shows the new lead.

## 4. Push, in this order
1. `git push origin HEAD:main`
2. If rejected: push to `auto/YYYY-MM-DD-daily`. The `auto-merge.yml` workflow checks the JSON, builds and merges it into `main`.
3. If both fail: `git format-patch origin/main --stdout > claude/pending/devlens-YYYY-MM-DD-daily.patch` and commit it to whatever branch can be pushed.
- Record the exact error text of every failed push.
- Commit messages: short summary of what changed. No model names.

## 5. Check
- Wait until https://devlensbd.org shows the new lead, and open at least one new story URL (`/YYYY/MM/DD/slug/`).

## 6. Finish
- Append the result to the run log: commit hash and story count, or the exact failure reason. Keep only the latest 60 entries.
- Commit and push the run log.
- Final report: lead (and its photo credit), number of stories and headlines, analysis title, jobs added and removed, funding changes, publish route, live check, outstanding issues.
- Do not post to social media. Do not send emails. Send one push notification with the summary when something was published or failed.

## Funding page (src/data/pages/funding.json)
- Status labels: OPEN, CLOSING SOON (deadline within 7 days), UPCOMING, CLOSED. The page currently has two sections, "Open now" and "Recently closed"; add an "Upcoming" section only when there is an item for it.
- Move items past their deadline to Recently closed. Update "Last checked: D Month YYYY."
- Keep `home.json` `funding` and `pills.fundingOpen` in step.

## Sectors and data
- Recount sector numbers in `src/data/pages/sectors.json` from the tags of all posts, and update "N stories published · Counts updated D Month YYYY".
- Data pages and key numbers use official figures only.

## Source access from cloud runs (checked 24 Nov 2026)
The egress proxy lets every source through. Some sites themselves block automated requests with a Cloudflare bot challenge (HTTP 403, header `cf-mitigated: challenge`). Do not try to get around these blocks (no headless browsers or other tricks). Use the sources that work, and cover blocked outlets' stories through other outlets that can be checked.
- Works with plain requests: The Daily Star, The Business Standard, Prothom Alo (Bangla and English), bdnews24 (English and Bangla), Bonik Barta, UNB (homepage `https://unb.com.bd/`), Financial Express (homepage `https://thefinancialexpress.com.bd/`), ReliefWeb (pages and RSS; its API returns 403 without an approved appname).
- Dhaka Post: RSS works at `https://www.dhakapost.com/rss/rss.xml`; the site itself is challenged.
- Blocked by Cloudflare challenge: Dhaka Tribune, New Age, Samakal, Kaler Kantho, BSS, Jugantor, Ittefaq, Desh Rupantor.
- Bangla requirement: Prothom Alo and bdnews24 Bangla are reliable; Bonik Barta and the Dhaka Post RSS are backups.
- To open the blocked sites, the owner would need to arrange access with the publishers (an allowlisted feed or API) or check those sites by hand in a manual browser session.
