# cli-anything-devlens: test plan and results

## Test inventory

- `test_core.py`: 67 unit tests on a small synthetic site built in a temp folder (no Node, no real content).
- `test_full_e2e.py`: 16 end-to-end tests on a full copy of the real site (all 143+ stories, real images), including real `astro build` runs and subprocess tests of the installed `cli-anything-devlens` command.

## Unit test plan (`test_core.py`)

| Module | What is tested | Edge cases |
|---|---|---|
| `core/session.py` | staging, reads see staged data, commit, undo, redo, history cap, state file locking, `.gitignore` in the state folder | undo with nothing to undo; undo refused after an outside edit; `--force` undo; redo cleared by a new commit; paths outside the site refused |
| `core/site.py` | site discovery (`--site`, `$DEVLENS_SITE`, parent folders), JSON style kept (indent 1 or 2, trailing newline), `slugify`, `long_date`, `check_date` | not a site; bad dates (`2026-02-30`); non-ASCII text (`·`, `€`) kept as-is |
| `core/posts.py` | add (slug from title, default date, image size read from file), update (fields, categories, tags, `modified`), remove, homepage-reference guard, list filters | duplicate slug; unknown category or tag; missing content; image outside `/media/`; image file missing; removing a story that is the lead |
| `core/jobs.py` | add (deadline text, badge default, inserted first), update, remove by url or index, prune by date, list by status | unknown sector; duplicate url; bad deadline; open-ended job (no deadline) never pruned |
| `core/home.py` | set lead (with `--demote`), set also-today, set special, plus add/remove/trim, numbers add/remove/keep, funding add (sorted)/remove/prune, pills, spotlight today | slug that does not exist; plus entry that is already the lead; bad source format |
| `core/media.py` | size reading for PNG, GIF, JPEG, WebP; add into `public/media/YYYY/MM/`; safe file names | unsupported file; existing file without `--overwrite` |
| `core/validate.py` | clean site passes; each error type detected | broken JSON; slug/file mismatch; missing image; homepage slug missing; expired jobs warned |

## E2E test plan (`test_full_e2e.py`)

All tests run on a fresh copy of the real site (`src/`, `public/`, `astro.config.mjs`, `package.json`, with `node_modules` linked) so the checkout is never touched.

- **Real data round trip**: read and rewrite every real JSON file through the CLI's writer; the bytes must not change.
- **Real validation**: `site validate` on the real content has no errors.
- **True backend build**: `build run` calls the real Astro build. Checks: `index.html` starts with `<!DOCTYPE html>`, every story has a page at `/YYYY/MM/DD/slug/index.html` that contains its title, `sitemap.xml` and `feed.xml` are XML, `/jobs/` exists, page count matches Astro's own count. Artifact paths are printed.
- **CLI subprocess tests** through `_resolve_cli("cli-anything-devlens")`, with no `cwd` set: `--help`, `--version`, `--json site info`, errors as JSON with exit 1, `--dry-run` leaves files unchanged.

## Realistic workflow scenarios

1. **Morning news run**
   - Simulates: the scheduled morning update.
   - Steps: `media add` a photo, `post add` two stories (one using the photo), `home set-lead` with `--demote`, `home plus add`, `job add` two jobs, `job prune`, `home funding add`, `home funding prune`, `home pills`, `site validate`, `build run`.
   - Verified: the new story pages exist in the build and contain their titles; the homepage HTML shows the new lead headline; the expired jobs are gone from the built jobs page; the new image is in the build output with the right size.
2. **Correction and rollback**
   - Simulates: an editor fixing a published story and then rolling back a bad homepage change.
   - Steps: `post update` title and excerpt, `home set-lead`, `session undo`, `session redo`, `session undo`.
   - Verified: after the undo, `home.json` is byte-identical to the original; the corrected title is in the rebuilt page.
3. **Safe removal**
   - Simulates: removing a story that is still on the homepage.
   - Steps: `post remove` (refused), `post remove --force`, `site validate`, `build run`.
   - Verified: the refusal names the homepage section; after `--force` the story's page is gone from the build and the site still builds.
4. **Undo stress**
   - Steps: 12 mutations in a row, then 12 undos.
   - Verified: every data file is byte-identical to the start.

## Test results

Last run: 2026-11-19, Python 3.13, Node v22.23.5, Astro v5.18.2, against a copy of the site at 143 stories and 97 jobs.
Command: `CLI_ANYTHING_FORCE_INSTALLED=1 python -m pytest cli_anything/devlens/tests/ -v --tb=no`

```
============================= test session starts ==============================
platform linux -- Python 3.13.18, pytest-9.2.0, pluggy-1.7.0 -- <venv>/bin/python
rootdir: agent-harness
collecting ... collected 83 items

cli_anything/devlens/tests/test_core.py::TestSite::test_find_site_explicit PASSED [  1%]
cli_anything/devlens/tests/test_core.py::TestSite::test_find_site_env PASSED [  2%]
cli_anything/devlens/tests/test_core.py::TestSite::test_find_site_parent PASSED [  3%]
cli_anything/devlens/tests/test_core.py::TestSite::test_not_a_site PASSED [  4%]
cli_anything/devlens/tests/test_core.py::TestSite::test_json_style_preserved PASSED [  6%]
cli_anything/devlens/tests/test_core.py::TestSite::test_non_ascii_kept PASSED [  7%]
cli_anything/devlens/tests/test_core.py::TestSite::test_slugify PASSED   [  8%]
cli_anything/devlens/tests/test_core.py::TestSite::test_long_date PASSED [  9%]
cli_anything/devlens/tests/test_core.py::TestSite::test_check_date PASSED [ 10%]
cli_anything/devlens/tests/test_core.py::TestSite::test_info PASSED      [ 12%]
cli_anything/devlens/tests/test_core.py::TestSession::test_staged_reads PASSED [ 13%]
cli_anything/devlens/tests/test_core.py::TestSession::test_commit_undo_redo PASSED [ 14%]
cli_anything/devlens/tests/test_core.py::TestSession::test_nothing_to_undo PASSED [ 15%]
cli_anything/devlens/tests/test_core.py::TestSession::test_undo_refuses_outside_edit PASSED [ 16%]
cli_anything/devlens/tests/test_core.py::TestSession::test_new_commit_clears_redo PASSED [ 18%]
cli_anything/devlens/tests/test_core.py::TestSession::test_history_cap PASSED [ 19%]
cli_anything/devlens/tests/test_core.py::TestSession::test_noop_commit PASSED [ 20%]
cli_anything/devlens/tests/test_core.py::TestSession::test_path_escape_refused PASSED [ 21%]
cli_anything/devlens/tests/test_core.py::TestSession::test_state_folder_ignored_by_git PASSED [ 22%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_add PASSED      [ 24%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_add_date_only PASSED [ 25%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_add_content_file PASSED [ 26%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_add_rejects[kwargs0-Unknown categories] PASSED [ 27%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_add_rejects[kwargs1-Unknown tags] PASSED [ 28%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_add_rejects[kwargs2-content is required] PASSED [ 30%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_add_rejects[kwargs3-must start with /media/] PASSED [ 31%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_add_rejects[kwargs4-No such image] PASSED [ 32%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_add_rejects[kwargs5-Slug must be] PASSED [ 33%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_add_rejects[kwargs6-already exists] PASSED [ 34%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_add_rejects[kwargs7-category] PASSED [ 36%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_update PASSED   [ 37%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_update_nothing PASSED [ 38%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_update_last_category PASSED [ 39%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_list_filters PASSED [ 40%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_remove_guarded PASSED [ 42%]
cli_anything/devlens/tests/test_core.py::TestPosts::test_new_post_visible_before_commit PASSED [ 43%]
cli_anything/devlens/tests/test_core.py::TestJobs::test_add PASSED       [ 44%]
cli_anything/devlens/tests/test_core.py::TestJobs::test_add_open_ended PASSED [ 45%]
cli_anything/devlens/tests/test_core.py::TestJobs::test_add_rejects[kw0-Unknown sector] PASSED [ 46%]
cli_anything/devlens/tests/test_core.py::TestJobs::test_add_rejects[kw1-already listed] PASSED [ 48%]
cli_anything/devlens/tests/test_core.py::TestJobs::test_add_rejects[kw2-must start with] PASSED [ 49%]
cli_anything/devlens/tests/test_core.py::TestJobs::test_add_rejects[kw3-deadline] PASSED [ 50%]
cli_anything/devlens/tests/test_core.py::TestJobs::test_prune PASSED     [ 51%]
cli_anything/devlens/tests/test_core.py::TestJobs::test_prune_nothing PASSED [ 53%]
cli_anything/devlens/tests/test_core.py::TestJobs::test_remove_and_update PASSED [ 54%]
cli_anything/devlens/tests/test_core.py::TestJobs::test_list_status PASSED [ 55%]
cli_anything/devlens/tests/test_core.py::TestHome::test_set_lead_demote PASSED [ 56%]
cli_anything/devlens/tests/test_core.py::TestHome::test_set_lead_missing PASSED [ 57%]
cli_anything/devlens/tests/test_core.py::TestHome::test_set_also_keeps_plus PASSED [ 59%]
cli_anything/devlens/tests/test_core.py::TestHome::test_set_special PASSED [ 60%]
cli_anything/devlens/tests/test_core.py::TestHome::test_plus PASSED      [ 61%]
cli_anything/devlens/tests/test_core.py::TestHome::test_plus_trim PASSED [ 62%]
cli_anything/devlens/tests/test_core.py::TestHome::test_numbers PASSED   [ 63%]
cli_anything/devlens/tests/test_core.py::TestHome::test_funding PASSED   [ 65%]
cli_anything/devlens/tests/test_core.py::TestHome::test_pills PASSED     [ 66%]
cli_anything/devlens/tests/test_core.py::TestHome::test_spotlight PASSED [ 67%]
cli_anything/devlens/tests/test_core.py::TestMedia::test_png PASSED      [ 68%]
cli_anything/devlens/tests/test_core.py::TestMedia::test_gif PASSED      [ 69%]
cli_anything/devlens/tests/test_core.py::TestMedia::test_jpeg PASSED     [ 71%]
cli_anything/devlens/tests/test_core.py::TestMedia::test_webp_vp8x PASSED [ 72%]
cli_anything/devlens/tests/test_core.py::TestMedia::test_unsupported PASSED [ 73%]
cli_anything/devlens/tests/test_core.py::TestMedia::test_add PASSED      [ 74%]
cli_anything/devlens/tests/test_core.py::TestMedia::test_add_bad_month PASSED [ 75%]
cli_anything/devlens/tests/test_core.py::TestValidate::test_clean PASSED [ 77%]
cli_anything/devlens/tests/test_core.py::TestValidate::test_detects_errors PASSED [ 78%]
cli_anything/devlens/tests/test_core.py::TestValidate::test_detects_content_problems PASSED [ 79%]
cli_anything/devlens/tests/test_core.py::TestValidate::test_warns_expired PASSED [ 80%]
cli_anything/devlens/tests/test_full_e2e.py::TestRealData::test_round_trip_is_byte_identical PASSED [ 81%]
cli_anything/devlens/tests/test_full_e2e.py::TestRealData::test_real_content_validates PASSED [ 83%]
cli_anything/devlens/tests/test_full_e2e.py::TestAstroBuild::test_build_real_site PASSED [ 84%]
cli_anything/devlens/tests/test_full_e2e.py::TestAstroBuild::test_verify_detects_missing_page PASSED [ 85%]
cli_anything/devlens/tests/test_full_e2e.py::TestAstroBuild::test_build_fails_loudly_on_broken_data PASSED [ 86%]
cli_anything/devlens/tests/test_full_e2e.py::TestWorkflows::test_morning_news_run PASSED [ 87%]
cli_anything/devlens/tests/test_full_e2e.py::TestWorkflows::test_correction_and_rollback PASSED [ 89%]
cli_anything/devlens/tests/test_full_e2e.py::TestWorkflows::test_safe_removal PASSED [ 90%]
cli_anything/devlens/tests/test_full_e2e.py::TestWorkflows::test_undo_stress PASSED [ 91%]
cli_anything/devlens/tests/test_full_e2e.py::TestCLISubprocess::test_help PASSED [ 92%]
cli_anything/devlens/tests/test_full_e2e.py::TestCLISubprocess::test_version PASSED [ 93%]
cli_anything/devlens/tests/test_full_e2e.py::TestCLISubprocess::test_site_info_json PASSED [ 95%]
cli_anything/devlens/tests/test_full_e2e.py::TestCLISubprocess::test_error_is_json_and_exit_1 PASSED [ 96%]
cli_anything/devlens/tests/test_full_e2e.py::TestCLISubprocess::test_not_a_site PASSED [ 97%]
cli_anything/devlens/tests/test_full_e2e.py::TestCLISubprocess::test_dry_run_writes_nothing PASSED [ 98%]
cli_anything/devlens/tests/test_full_e2e.py::TestCLISubprocess::test_full_cli_workflow_with_build PASSED [100%]

============================= 83 passed in 17.55s ==============================
```

**Summary**: 83 passed, 0 failed, 0 skipped in 17.55s (100% pass rate). With `-s`, the subprocess tests print `[_resolve_cli] Using installed command: .../bin/cli-anything-devlens`.

Artifacts checked in the run (printed with `-s`):
- Full real-site build: 243 HTML pages, all 143 story pages found and containing their titles; `index.html` about 41 KB.
- Rewrote all 159 real JSON data files through the CLI writer with no byte changes.
- Real content validation: 0 errors, 2 warnings (one story's `modified` is earlier than its `date`; one story uses the tag `development-cooperation`, which is not in `tags.json`).

## Coverage notes

- `build run` is tested end to end with the real Astro build; Cloudflare's own deploy step is not.
- The REPL is checked by hand (piped commands), not by an automated test.
- `pages/*.json` (About, Funding...) are read but not edited by the CLI.
- No browser rendering checks: page checks are on the generated HTML.
