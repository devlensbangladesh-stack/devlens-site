"""End-to-end tests on a full copy of the real Devlens site.

These call the real Astro build (Node.js and the site's node_modules are
required; the tests fail, not skip, without them) and the installed
cli-anything-devlens command.

Set DEVLENS_SOURCE_SITE to the site checkout to copy (default: the repo this
harness lives in). Set CLI_ANYTHING_FORCE_INSTALLED=1 to require the installed
command rather than the python -m fallback.
"""

import html
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from cli_anything.devlens.core import build, home, jobs, media, posts, validate
from cli_anything.devlens.core.site import Site, is_site

HERE = Path(__file__).resolve()


def _source_site() -> Path:
    env = os.environ.get("DEVLENS_SOURCE_SITE")
    if env:
        return Path(env).resolve()
    for p in HERE.parents:
        if is_site(p):
            return p
    raise RuntimeError("Set DEVLENS_SOURCE_SITE to a Devlens site checkout")


SOURCE = _source_site()


def _resolve_cli(name):
    """Resolve installed CLI command; falls back to python -m for dev.

    Set env CLI_ANYTHING_FORCE_INSTALLED=1 to require the installed command.
    """
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    module = name.replace("cli-anything-", "cli_anything.") + "." + name.split("-")[-1] + "_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


def copy_site(dest: Path) -> Path:
    """Copy the real site (hard-linking images; the CLI replaces files atomically)."""
    dest.mkdir(parents=True)
    shutil.copytree(SOURCE / "src", dest / "src")
    def link_or_copy(src, dst):
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)

    shutil.copytree(SOURCE / "public", dest / "public", copy_function=link_or_copy)
    for f in ("astro.config.mjs", "package.json", "package-lock.json"):
        if (SOURCE / f).exists():
            shutil.copy2(SOURCE / f, dest / f)
    nm = SOURCE / "node_modules"
    if not (nm / "astro").is_dir():
        raise RuntimeError(f"{nm} has no Astro; run 'npm ci' in {SOURCE}")
    (dest / "node_modules").symlink_to(nm)
    return dest


def data_snapshot(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in (root / "src" / "data").rglob("*.json")}


@pytest.fixture
def real_site(tmp_path):
    return copy_site(tmp_path / "site")


@pytest.fixture
def out_dir(tmp_path):
    return tmp_path / "dist"


def page_text(path: Path) -> str:
    return html.unescape(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- real data
class TestRealData:
    def test_round_trip_is_byte_identical(self, real_site):
        site = Site(real_site)
        before = data_snapshot(real_site)
        for rel in before:
            site.write_json(rel, site.read_json(rel))
        assert site.session.pending() == []
        site.session.commit("round trip")
        assert data_snapshot(real_site) == before
        print(f"\n  Rewrote {len(before)} real JSON files with no byte changes")

    def test_real_content_validates(self, real_site):
        r = validate.run(Site(real_site))
        assert r["ok"], r["errors"]
        assert r["checked"]["posts"] >= 100
        print(f"\n  {r['checked']} — {len(r['warnings'])} warning(s)")


# ---------------------------------------------------------------- true backend
class TestAstroBuild:
    def test_build_real_site(self, real_site, out_dir):
        r = build.run(Site(real_site), str(out_dir))
        assert r["ok"], r["problems"]
        n_posts = len(Site(real_site).post_slugs())
        assert r["stories_checked"] == n_posts
        assert r["astro_pages"] and r["html_pages"] >= n_posts
        idx = out_dir / "index.html"
        assert idx.read_text(encoding="utf-8")[:15].lower() == "<!doctype html>"
        assert (out_dir / "sitemap.xml").read_text()[:5] == "<?xml"
        print(f"\n  Built: {idx} ({idx.stat().st_size:,} bytes), {r['html_pages']} pages in {r['seconds']}s")

    def test_verify_detects_missing_page(self, real_site, out_dir):
        site = Site(real_site)
        build.run(site, str(out_dir))
        victim = site.posts()[0]
        shutil.rmtree(build.post_page(out_dir, victim).parent)
        r = build.verify(site, str(out_dir))
        assert not r["ok"] and any(victim["slug"] in p for p in r["problems"])

    def test_build_fails_loudly_on_broken_data(self, real_site, out_dir):
        from cli_anything.devlens.utils.astro_backend import BackendError
        (real_site / "src/data/home.json").write_text("{broken")
        with pytest.raises(BackendError, match="astro build failed"):
            build.run(Site(real_site), str(out_dir))


# ---------------------------------------------------------------- workflows
class TestWorkflows:
    def test_morning_news_run(self, real_site, out_dir, tmp_path):
        site = Site(real_site)
        # a new photo, two stories, homepage changes, jobs and funding
        photo = next((SOURCE / "public/media").rglob("*.jpg"))
        img = media.add(site, str(photo), month="2026-11", name="e2e-photo.jpg")
        a = posts.add(site, "E2E: Flood relief reaches 20,000 families in Sunamganj",
                      "Aid groups say supplies reached most villages.", ["news"], ["health"],
                      content="<p>Relief arrived &amp; was shared.</p>", date="2026-11-19T11:00",
                      image=img["src"], image_alt="Relief boats")
        b = posts.add(site, "E2E analysis: what the budget means for NGOs", "Short read.",
                      ["analysis"], [], content="<p>Analysis body.</p>", date="2026-11-19T12:00")
        home.set_lead(site, a["slug"], label="Climate · Floods", demote=True)
        home.plus_add(site, b["slug"])
        jobs.add(site, "E2E Field Officer", "BRAC", "health-nutrition", "https://example.org/e2e-job-1",
                 "Sunamganj", deadline="2026-12-15")
        jobs.add(site, "E2E Consultant", "UNDP", "development-cooperation", "https://example.org/e2e-job-2",
                 "Dhaka", deadline="2026-12-20", consultancy=True)
        pruned = jobs.prune(site, today="2026-11-27")
        home.funding_add(site, "E2E grant", "EU", "2026-12-31", "https://example.org/e2e-grant")
        home.funding_prune(site, today="2026-11-27")
        home.pills_set(site, funding_open=len(site.home()["funding"]))
        site.session.commit("morning run")

        assert validate.run(site, today="2026-11-27")["ok"]
        r = build.run(site, str(out_dir))
        assert r["ok"], r["problems"]

        page_a = build.post_page(out_dir, posts.get(site, a["slug"]))
        assert a["title"] in page_text(page_a)
        assert img["src"] in page_a.read_text(encoding="utf-8")
        assert a["title"] in page_text(out_dir / "index.html")
        built_img = out_dir / img["src"].lstrip("/")
        assert media.image_size(built_img.read_bytes())[1:] == (img["width"], img["height"])
        jobs_html = page_text(out_dir / "jobs" / "index.html")
        assert "E2E Field Officer" in jobs_html
        for gone in pruned["removed_jobs"][:5]:
            still = [j for j in site.jobs_data()["jobs"] if j["title"] == gone["title"]]
            if not still:
                assert gone["title"] not in jobs_html
        print(f"\n  Story page: {page_a}\n  Homepage: {out_dir / 'index.html'}\n  Pruned {pruned['removed']} jobs")

    def test_correction_and_rollback(self, real_site, out_dir):
        site = Site(real_site)
        before_home = (real_site / "src/data/home.json").read_bytes()
        slug = site.posts()[3]["slug"]
        posts.update(site, slug, title="Corrected headline for E2E", excerpt="Corrected excerpt.")
        site.session.commit("fix")
        home.set_lead(site, slug)
        site.session.commit("bad lead")
        site.session.undo()
        assert (real_site / "src/data/home.json").read_bytes() == before_home
        site.session.redo()
        assert site.home()["lead"]["slug"] == slug
        site.session.undo()
        assert (real_site / "src/data/home.json").read_bytes() == before_home
        r = build.run(site, str(out_dir))
        assert r["ok"], r["problems"]
        assert "Corrected headline for E2E" in page_text(build.post_page(out_dir, posts.get(site, slug)))

    def test_safe_removal(self, real_site, out_dir):
        site = Site(real_site)
        lead = site.home()["lead"]["slug"]
        plus_slug = site.home()["alsoToday"]["plus"][0]
        with pytest.raises(Exception, match="homepage"):
            posts.remove(site, lead)
        old = posts.get(site, plus_slug)
        r = posts.remove(site, plus_slug, force=True)
        assert r["homepage_refs"] == ["alsoToday.plus"]
        site.session.commit("remove")
        assert validate.run(site)["ok"]
        res = build.run(site, str(out_dir))
        assert res["ok"], res["problems"]
        assert not build.post_page(out_dir, old).exists()

    def test_undo_stress(self, real_site):
        site = Site(real_site)
        before = data_snapshot(real_site)
        slugs = [p["slug"] for p in site.posts()[:6]]
        steps = [
            lambda: home.set_lead(site, slugs[1], demote=True),
            lambda: home.set_also(site, slugs[2]),
            lambda: home.plus_trim(site, 5),
            lambda: home.number_add(site, "9%", "E2E", "Test", keep=3),
            lambda: home.funding_prune(site, today="2027-01-01"),
            lambda: jobs.prune(site, today="2027-01-01"),
            lambda: posts.update(site, slugs[3], title="Stress title"),
            lambda: posts.update(site, slugs[4], add_tags=["governance"]),
            lambda: posts.add(site, "Stress new story", "E", ["news"], content="<p>x</p>"),
            lambda: posts.remove(site, "stress-new-story"),
            lambda: home.pills_set(site, key_numbers=99),
            lambda: home.set_special(site, slugs[5], published="2026-11-19"),
        ]
        n = 0
        for step in steps:
            step()
            if site.session.commit("step")["committed"]:
                n += 1
        assert n == 12
        for _ in range(n):
            site.session.undo()
        assert data_snapshot(real_site) == before


# ---------------------------------------------------------------- subprocess
class TestCLISubprocess:
    CLI_BASE = _resolve_cli("cli-anything-devlens")

    def _run(self, args, check=True):
        return subprocess.run(self.CLI_BASE + args, capture_output=True, text=True, check=check)

    def test_help(self):
        r = self._run(["--help"])
        assert r.returncode == 0
        for group in ("post", "job", "home", "media", "build", "session", "site"):
            assert group in r.stdout

    def test_version(self):
        assert "1.0.0" in self._run(["--version"]).stdout

    def test_site_info_json(self, real_site):
        r = self._run(["--site", str(real_site), "--json", "site", "info"])
        data = json.loads(r.stdout)
        assert data["posts"] >= 100 and data["site"] == str(real_site.resolve())

    def test_error_is_json_and_exit_1(self, real_site):
        r = self._run(["--site", str(real_site), "--json", "post", "show", "no-such-story"], check=False)
        assert r.returncode == 1
        assert "No story" in json.loads(r.stdout)["error"]

    def test_not_a_site(self, tmp_path):
        r = self._run(["--site", str(tmp_path), "site", "info"], check=False)
        assert r.returncode == 1 and "Not a Devlens site" in r.stderr

    def test_dry_run_writes_nothing(self, real_site):
        before = data_snapshot(real_site)
        r = self._run(["--site", str(real_site), "--json", "--dry-run", "job", "prune", "--today", "2027-01-01"])
        data = json.loads(r.stdout)
        assert data["dry_run"] is True and data["saved"] is False and data["removed"] > 0
        assert data["changes"] == [{"path": "src/data/jobs.json", "action": "modify"}]
        assert data_snapshot(real_site) == before

    def test_full_cli_workflow_with_build(self, real_site, out_dir, tmp_path):
        s = ["--site", str(real_site), "--json"]
        body = tmp_path / "body.html"
        body.write_text('<p class="wp-block-paragraph">CLI body.</p>', encoding="utf-8")
        photo = next((SOURCE / "public/media").rglob("*.jpg"))
        img = json.loads(self._run(s + ["media", "add", str(photo), "--month", "2026-11", "--name", "cli-e2e.jpg"]).stdout)
        assert img["saved"] and img["width"] > 0
        add = json.loads(self._run(s + [
            "post", "add", "--title", "CLI E2E: Teachers' strike enters third day",
            "--excerpt", "Schools in 12 districts stay shut.", "--category", "news", "--tag", "governance",
            "--content-file", str(body), "--date", "2026-11-19T13:00", "--image", img["src"],
            "--image-alt", "A closed school gate"]).stdout)
        slug = add["added"]
        assert add["changes"][0]["action"] == "create"
        self._run(s + ["home", "set-lead", slug, "--label", "Education · Strike", "--demote"])
        self._run(s + ["job", "add", "--title", "CLI E2E Officer", "--org", "Save the Children",
                       "--sector", "education", "--url", "https://example.org/cli-e2e-job",
                       "--location", "Rangpur", "--deadline", "2026-12-12"])
        hist = json.loads(self._run(s + ["session", "history"]).stdout)
        assert len(hist) == 4
        r = self._run(s + ["build", "run", "--out", str(out_dir)], check=False)
        assert r.returncode == 0, r.stdout + r.stderr
        report = json.loads(r.stdout)
        assert report["ok"] and report["stories_checked"] >= 100
        y, m, d = "2026", "11", "19"
        page = out_dir / y / m / d / slug / "index.html"
        assert "CLI E2E: Teachers' strike enters third day" in page_text(page)
        assert "CLI E2E: Teachers' strike enters third day" in page_text(out_dir / "index.html")
        assert "CLI E2E Officer" in page_text(out_dir / "jobs" / "index.html")
        print(f"\n  Story page: {page} ({page.stat().st_size:,} bytes)")
        # undo everything through the CLI
        for _ in range(4):
            self._run(s + ["session", "undo"])
        assert not (real_site / f"src/data/posts/{slug}.json").exists()
        assert not (real_site / "public/media/2026/11/cli-e2e.jpg").exists()
        assert data_snapshot(real_site) == data_snapshot(SOURCE)
