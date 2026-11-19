"""Unit tests on a small synthetic site. No Node or real content needed."""

import json
import os
import struct

import pytest

from cli_anything.devlens.core import home, jobs, media, posts, validate
from cli_anything.devlens.core.session import Session, SessionError
from cli_anything.devlens.core.site import (Site, SiteError, check_date, find_site, long_date,
                                            slugify)
from cli_anything.devlens.tests.conftest import make_png


def snapshot(root):
    out = {}
    for dirpath, _, files in os.walk(root):
        if ".devlens-cli" in dirpath:
            continue
        for f in files:
            p = os.path.join(dirpath, f)
            out[os.path.relpath(p, root)] = open(p, "rb").read()
    return out


@pytest.fixture
def site(mini_site):
    return Site(mini_site)


def commit(site, name="test"):
    return site.session.commit(name)


# ---------------------------------------------------------------- site.py
class TestSite:
    def test_find_site_explicit(self, mini_site):
        assert find_site(str(mini_site)) == mini_site.resolve()

    def test_find_site_env(self, mini_site, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("DEVLENS_SITE", str(mini_site))
        assert find_site() == mini_site.resolve()

    def test_find_site_parent(self, mini_site, monkeypatch):
        monkeypatch.delenv("DEVLENS_SITE", raising=False)
        monkeypatch.chdir(mini_site / "src" / "data")
        assert find_site() == mini_site.resolve()

    def test_not_a_site(self, tmp_path):
        with pytest.raises(SiteError):
            find_site(str(tmp_path))

    def test_json_style_preserved(self, site, mini_site):
        before = snapshot(mini_site)
        for rel in ["src/data/home.json", "src/data/jobs.json", "src/data/tags.json",
                    "src/data/posts/alpha-story.json", "src/data/posts/beta-story.json"]:
            site.write_json(rel, site.read_json(rel))
        assert site.session.pending() == []
        commit(site)
        assert snapshot(mini_site) == before

    def test_non_ascii_kept(self, site, mini_site):
        p = site.read_json("src/data/posts/alpha-story.json")
        p["title"] = "Grants · €10k"
        site.write_json("src/data/posts/alpha-story.json", p)
        commit(site)
        text = (mini_site / "src/data/posts/alpha-story.json").read_text(encoding="utf-8")
        assert "Grants · €10k" in text and "\\u" not in text

    def test_slugify(self):
        assert slugify("World Bank's 3.4% growth & reforms") == "world-banks-3-4-percent-growth-and-reforms"
        assert slugify("Dengue: 1,674 admissions") == "dengue-1674-admissions"
        assert len(slugify("word " * 50)) <= 90

    def test_long_date(self):
        assert long_date("2026-11-01") == "1 November 2026"

    def test_check_date(self):
        assert check_date("2026-02-28") == "2026-02-28"
        for bad in ("2026-02-30", "26-11-01", "", "2026/11/01"):
            with pytest.raises(SiteError):
                check_date(bad)

    def test_info(self, site):
        i = site.info(today="2026-11-25")
        assert i["posts"] == 3 and i["jobs"] == 3
        assert i["jobs_expired"] == 1 and i["funding_open"] == 1
        assert i["latest_post"] == "beta-story"


# ---------------------------------------------------------------- session.py
class TestSession:
    def test_staged_reads(self, mini_site):
        s = Session(mini_site)
        s.write_bytes("src/data/x.txt", b"hello")
        assert s.read_bytes("src/data/x.txt") == b"hello"
        assert not (mini_site / "src/data/x.txt").exists()

    def test_commit_undo_redo(self, mini_site):
        s = Session(mini_site)
        s.write_bytes("src/data/x.txt", b"hello")
        assert s.commit("add x")["committed"]
        assert (mini_site / "src/data/x.txt").read_bytes() == b"hello"
        s.undo()
        assert not (mini_site / "src/data/x.txt").exists()
        s.redo()
        assert (mini_site / "src/data/x.txt").read_bytes() == b"hello"

    def test_nothing_to_undo(self, mini_site):
        with pytest.raises(SessionError):
            Session(mini_site).undo()
        with pytest.raises(SessionError):
            Session(mini_site).redo()

    def test_undo_refuses_outside_edit(self, mini_site):
        s = Session(mini_site)
        s.write_bytes("src/data/x.txt", b"one")
        s.commit("x")
        (mini_site / "src/data/x.txt").write_bytes(b"edited by hand")
        with pytest.raises(SessionError, match="changed outside"):
            s.undo()
        s.undo(force=True)
        assert not (mini_site / "src/data/x.txt").exists()

    def test_new_commit_clears_redo(self, mini_site):
        s = Session(mini_site)
        s.write_bytes("a.txt", b"1"); s.commit("a")
        s.undo()
        s.write_bytes("b.txt", b"2"); s.commit("b")
        assert s.history()["redo"] == []

    def test_history_cap(self, mini_site):
        s = Session(mini_site)
        for i in range(35):
            s.write_bytes("n.txt", str(i).encode()); s.commit(f"n{i}")
        assert len(s.history()["undo"]) == 30

    def test_noop_commit(self, mini_site):
        s = Session(mini_site)
        data = (mini_site / "src/data/home.json").read_bytes()
        s.write_bytes("src/data/home.json", data)
        assert s.commit("noop")["committed"] is False
        assert s.history()["undo"] == []

    def test_path_escape_refused(self, mini_site):
        with pytest.raises(SessionError):
            Session(mini_site).write_bytes("../outside.txt", b"x")

    def test_state_folder_ignored_by_git(self, mini_site):
        s = Session(mini_site)
        s.write_bytes("a.txt", b"1"); s.commit("a")
        assert (mini_site / ".devlens-cli" / ".gitignore").read_text() == "*\n"
        json.loads((mini_site / ".devlens-cli" / "session.json").read_text())


# ---------------------------------------------------------------- posts.py
class TestPosts:
    def test_add(self, site, mini_site):
        p = posts.add(site, "New story: aid cuts", "Excerpt.", ["news"], ["health"],
                      content="<p>Body</p>", date="2026-11-19T10:30", image="/media/2026/11/a.png")
        assert p["slug"] == "new-story-aid-cuts"
        assert p["date"] == "2026-11-19T10:30:00" and p["modified"] == p["date"]
        assert p["image"]["width"] == 4 and p["image"]["height"] == 3
        commit(site)
        saved = json.loads((mini_site / "src/data/posts/new-story-aid-cuts.json").read_text())
        assert list(saved) == posts.FIELDS

    def test_add_date_only(self, site):
        p = posts.add(site, "T", "E", ["news"], content="<p>x</p>", date="2026-11-19")
        assert p["date"] == "2026-11-19T09:00:00"

    def test_add_content_file(self, site, tmp_path):
        f = tmp_path / "b.html"; f.write_text("<p>From file</p>")
        assert posts.add(site, "T2", "E", ["news"], content_file=str(f))["content"] == "<p>From file</p>"

    @pytest.mark.parametrize("kwargs,msg", [
        ({"categories": ["nope"]}, "Unknown categories"),
        ({"tags": ["nope"]}, "Unknown tags"),
        ({"content": ""}, "content is required"),
        ({"image": "https://x.org/a.jpg"}, "must start with /media/"),
        ({"image": "/media/2026/11/missing.png"}, "No such image"),
        ({"slug": "Bad Slug"}, "Slug must be"),
        ({"slug": "alpha-story"}, "already exists"),
        ({"categories": []}, "category"),
    ])
    def test_add_rejects(self, site, kwargs, msg):
        args = {"title": "T", "excerpt": "E", "categories": ["news"], "tags": [], "content": "<p>x</p>"}
        args.update(kwargs)
        with pytest.raises(SiteError, match=msg):
            posts.add(site, **args)

    def test_update(self, site):
        r = posts.update(site, "alpha-story", title="Alpha fixed", add_tags=["governance"],
                         remove_tags=["health"], add_categories=["analysis"])
        assert set(r["changed"]) == {"title", "tags", "categories"}
        p = posts.get(site, "alpha-story")
        assert p["title"] == "Alpha fixed" and p["tags"] == ["governance"]
        assert p["categories"] == ["news", "analysis"]
        assert p["modified"] >= p["date"]

    def test_update_nothing(self, site):
        with pytest.raises(SiteError, match="Nothing to update"):
            posts.update(site, "alpha-story")

    def test_update_last_category(self, site):
        with pytest.raises(SiteError, match="at least one category"):
            posts.update(site, "alpha-story", remove_categories=["news"])

    def test_list_filters(self, site):
        assert [p["slug"] for p in posts.list_posts(site)] == ["beta-story", "alpha-story", "gamma-special"]
        assert [p["slug"] for p in posts.list_posts(site, category="devlens-special")] == ["gamma-special"]
        assert [p["slug"] for p in posts.list_posts(site, since="2026-11-19")] == ["beta-story"]
        assert [p["slug"] for p in posts.list_posts(site, search="ALPHA")] == ["alpha-story"]
        assert len(posts.list_posts(site, limit=1)) == 1

    def test_remove_guarded(self, site, mini_site):
        with pytest.raises(SiteError, match="lead"):
            posts.remove(site, "beta-story")
        r = posts.remove(site, "gamma-special", force=True)
        assert set(r["homepage_refs"]) == {"special", "alsoToday.plus"}
        commit(site)
        assert not (mini_site / "src/data/posts/gamma-special.json").exists()
        assert "gamma-special" not in home.plus_list(site)

    def test_new_post_visible_before_commit(self, site):
        posts.add(site, "Staged", "E", ["news"], content="<p>x</p>")
        assert "staged" in site.post_slugs()
        site.session.discard()
        assert "staged" not in site.post_slugs()


# ---------------------------------------------------------------- jobs.py
class TestJobs:
    def test_add(self, site):
        j = jobs.add(site, "Officer", "WHO", "health-nutrition", "https://jobs.example/9", "Dhaka",
                     deadline="2026-12-03", featured="UN AGENCY", added="2026-11-19")
        assert j["deadlineText"] == "3 December 2026" and j["badge"] == "WHO"
        assert site.jobs_data()["jobs"][0]["url"] == "https://jobs.example/9"

    def test_add_open_ended(self, site):
        j = jobs.add(site, "Officer", "WHO", "education", "https://jobs.example/10", "Dhaka")
        assert j["deadline"] is None and j["deadlineText"] == "Open until filled"

    @pytest.mark.parametrize("kw,msg", [
        ({"sector": "space"}, "Unknown sector"),
        ({"url": "https://jobs.example/1"}, "already listed"),
        ({"url": "jobs.example/x"}, "must start with"),
        ({"deadline": "2026-13-01"}, "deadline"),
    ])
    def test_add_rejects(self, site, kw, msg):
        args = dict(title="T", org="O", sector="education", url="https://jobs.example/new", location="Dhaka")
        args.update(kw)
        with pytest.raises(SiteError, match=msg):
            jobs.add(site, **args)

    def test_prune(self, site):
        r = jobs.prune(site, today="2026-11-25")
        assert r["removed"] == 1 and r["remaining"] == 2
        assert [j["title"] for j in site.jobs_data()["jobs"]] == ["Job two", "Job open"]

    def test_prune_nothing(self, site):
        assert jobs.prune(site, today="2026-11-01")["removed"] == 0
        assert site.session.pending() == []

    def test_remove_and_update(self, site):
        jobs.update(site, url="https://jobs.example/2", deadline="2026-12-10")
        assert site.jobs_data()["jobs"][1]["deadlineText"] == "10 December 2026"
        assert jobs.remove(site, index=0)["removed"] == "Job one"
        with pytest.raises(SiteError):
            jobs.remove(site, url="https://nope")
        with pytest.raises(SiteError):
            jobs.remove(site, index=99)

    def test_list_status(self, site):
        assert len(jobs.list_jobs(site, status="open", today="2026-11-25")) == 2
        assert len(jobs.list_jobs(site, status="expired", today="2026-11-25")) == 1
        assert len(jobs.list_jobs(site, sector="education")) == 2
        assert len(jobs.list_jobs(site, org="unicef")) == 1


# ---------------------------------------------------------------- home.py
class TestHome:
    def test_set_lead_demote(self, site):
        r = home.set_lead(site, "alpha-story", demote=True)
        assert r["lead"]["headline"] == "Alpha story" and r["lead"]["label"] == "News"
        assert home.plus_list(site)[0] == "beta-story"

    def test_set_lead_missing(self, site):
        with pytest.raises(SiteError, match="No story"):
            home.set_lead(site, "nope")

    def test_set_also_keeps_plus(self, site):
        home.set_also(site, "beta-story", label="Health")
        h = site.home()["alsoToday"]
        assert h["slug"] == "beta-story" and h["plus"] == ["gamma-special"]
        assert list(h) == ["slug", "label", "headline", "summary", "plus"]

    def test_set_special(self, site):
        r = home.set_special(site, "alpha-story", published="2026-11-19")
        assert r["special"]["published"] == "2026-11-19"

    def test_plus(self, site):
        home.set_also(site, "gamma-special")
        r = home.plus_add(site, "alpha-story", position=5)
        assert r["position"] == 0 and home.plus_list(site) == ["alpha-story"]
        home.plus_remove(site, "alpha-story")
        home.set_also(site, "alpha-story")
        home.plus_add(site, "gamma-special")
        with pytest.raises(SiteError, match="already the lead"):
            home.plus_add(site, "beta-story")
        home.plus_remove(site, "gamma-special")
        assert home.plus_list(site) == []
        with pytest.raises(SiteError):
            home.plus_remove(site, "gamma-special")

    def test_plus_trim(self, site):
        assert home.plus_trim(site, 0)["dropped"] == ["gamma-special"]

    def test_numbers(self, site):
        r = home.number_add(site, "2%", "Two", "B", keep=1)
        assert [n["value"] for n in r["numbers"]] == ["2%"] and r["dropped"][0]["value"] == "1%"
        home.number_remove(site, 0)
        with pytest.raises(SiteError):
            home.number_remove(site, 0)

    def test_funding(self, site):
        home.funding_add(site, "Grant C", "F", "2026-11-25", "https://example.org/c")
        assert [f["title"] for f in site.home()["funding"]] == ["Grant A", "Grant C", "Grant B"]
        r = home.funding_prune(site, today="2026-11-26")
        assert [f["title"] for f in r["removed"]] == ["Grant A", "Grant C"]
        home.funding_remove(site, "https://example.org/b")
        assert site.home()["funding"] == []
        with pytest.raises(SiteError):
            home.funding_add(site, "X", "F", "soon", "https://example.org/x")

    def test_pills(self, site):
        assert home.pills_set(site, funding_open=5) == {"fundingOpen": 5, "newReports": 1, "keyNumbers": 3}
        with pytest.raises(SiteError):
            home.pills_set(site, new_reports=-1)

    def test_spotlight(self, site):
        t = home.spotlight_set_today(site, "19 Nov", "New text", ["UNB|https://unb.com.bd/x"])
        assert t["sources"] == [{"name": "UNB", "url": "https://unb.com.bd/x"}]
        with pytest.raises(SiteError, match="Name"):
            home.spotlight_set_today(site, "19 Nov", "x", ["no url"])


# ---------------------------------------------------------------- media.py
class TestMedia:
    def test_png(self):
        assert media.image_size(make_png(7, 5)) == ("png", 7, 5)

    def test_gif(self):
        assert media.image_size(b"GIF89a" + struct.pack("<HH", 12, 9) + b"\x00" * 10) == ("gif", 12, 9)

    def test_jpeg(self):
        sof = b"\xff\xc0" + struct.pack(">HBHH", 17, 8, 720, 1280) + b"\x00" * 12
        app0 = b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + b"\x00" * 9
        assert media.image_size(b"\xff\xd8" + app0 + sof) == ("jpeg", 1280, 720)

    def test_webp_vp8x(self):
        data = b"RIFF\x00\x00\x00\x00WEBPVP8X" + b"\x00" * 8 + (1919).to_bytes(3, "little") + (1079).to_bytes(3, "little")
        assert media.image_size(data) == ("webp", 1920, 1080)

    def test_unsupported(self):
        with pytest.raises(SiteError):
            media.image_size(b"hello world, not an image")

    def test_add(self, site, mini_site, tmp_path):
        f = tmp_path / "My Photo.PNG"; f.write_bytes(make_png(10, 6))
        r = media.add(site, str(f), month="2026-11")
        assert r["src"] == "/media/2026/11/my-photo.png" and (r["width"], r["height"]) == (10, 6)
        commit(site)
        assert (mini_site / "public/media/2026/11/my-photo.png").is_file()
        with pytest.raises(SiteError, match="already exists"):
            media.add(site, str(f), month="2026-11")
        assert media.add(site, str(f), month="2026-11", overwrite=True)["bytes"] == f.stat().st_size

    def test_add_bad_month(self, site, tmp_path):
        f = tmp_path / "a.png"; f.write_bytes(make_png(1, 1))
        with pytest.raises(SiteError, match="YYYY-MM"):
            media.add(site, str(f), month="Nov")


# ---------------------------------------------------------------- validate.py
class TestValidate:
    def test_clean(self, site):
        r = validate.run(site, today="2026-11-19")
        assert r["ok"], r["errors"]

    def test_detects_errors(self, site, mini_site):
        (mini_site / "src/data/posts/broken.json").write_text("{not json")
        r = validate.run(site)
        assert not r["ok"] and "invalid JSON" in r["errors"][0]["problem"]

    def test_detects_content_problems(self, site):
        p = posts.get(site, "alpha-story")
        p["slug"] = "other"
        p["image"]["src"] = "/media/2026/11/missing.jpg"
        p["categories"] = ["nope"]
        site.write_json(site.post_path("alpha-story"), p)
        h = site.home(); h["alsoToday"]["plus"].append("ghost")
        site.write_json("src/data/home.json", h)
        probs = " | ".join(e["problem"] for e in validate.run(site)["errors"])
        for needle in ("does not match the file name", "image file not found", "unknown category",
                       "story not found: ghost"):
            assert needle in probs

    def test_warns_expired(self, site):
        r = validate.run(site, today="2026-11-30")
        assert r["ok"]
        text = " | ".join(w["problem"] for w in r["warnings"])
        assert "past their deadline" in text and "deadline passed" in text
