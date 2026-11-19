"""Homepage content in src/data/home.json."""

from __future__ import annotations

from cli_anything.devlens.core import posts as posts_mod
from cli_anything.devlens.core.site import HOME, Site, SiteError, check_date, today_dhaka

SECTIONS = ["lead", "alsoToday", "special", "pills", "numbers", "funding", "pinnedSpecials", "spotlight"]


def show(site: Site, section: str | None = None):
    home = site.home()
    if section is None:
        return home
    if section not in home:
        raise SiteError(f"Unknown homepage section {section!r}; choose one of: {', '.join(home)}")
    return home[section]


def _feature(site: Site, slug: str, label, headline, summary) -> dict:
    post = posts_mod.get(site, slug)
    if not label:
        cats = {c["slug"]: c["name"] for c in site.categories()}
        label = cats.get(post["categories"][0], post["categories"][0])
    return {"slug": slug, "label": label, "headline": headline or post["title"],
            "summary": summary or post["excerpt"]}


def set_lead(site: Site, slug: str, label=None, headline=None, summary=None,
             demote: bool = False) -> dict:
    home = site.home()
    old = home.get("lead", {}).get("slug")
    home["lead"] = _feature(site, slug, label, headline, summary)
    plus = home.setdefault("alsoToday", {}).setdefault("plus", [])
    if slug in plus:
        plus.remove(slug)
    if demote and old and old != slug and old not in plus:
        plus.insert(0, old)
    site.write_json(HOME, home)
    return {"lead": home["lead"], "previous": old, "demoted": bool(demote and old and old != slug)}


def set_also(site: Site, slug: str, label=None, headline=None, summary=None) -> dict:
    home = site.home()
    also = home.setdefault("alsoToday", {})
    old = also.get("slug")
    plus = also.get("plus", [])
    if slug in plus:
        plus.remove(slug)
    also.update(_feature(site, slug, label, headline, summary))
    also["plus"] = plus
    # keep key order: slug, label, headline, summary, plus
    home["alsoToday"] = {k: also[k] for k in ("slug", "label", "headline", "summary", "plus")}
    site.write_json(HOME, home)
    return {"alsoToday": {k: v for k, v in home["alsoToday"].items() if k != "plus"}, "previous": old}


def set_special(site: Site, slug: str, label=None, headline=None, summary=None,
                published: str | None = None) -> dict:
    home = site.home()
    feat = _feature(site, slug, label or "Special report", headline, summary)
    feat["published"] = check_date(published or today_dhaka(), "published")
    old = home.get("special", {}).get("slug")
    home["special"] = feat
    site.write_json(HOME, home)
    return {"special": feat, "previous": old}


def plus_list(site: Site) -> list[str]:
    return site.home().get("alsoToday", {}).get("plus", [])


def plus_add(site: Site, slug: str, position: int = 0) -> dict:
    posts_mod.get(site, slug)
    home = site.home()
    plus = home.setdefault("alsoToday", {}).setdefault("plus", [])
    if slug in (home.get("lead", {}).get("slug"), home["alsoToday"].get("slug")):
        raise SiteError(f"{slug} is already the lead or 'Also today' story")
    if slug in plus:
        plus.remove(slug)
    plus.insert(max(0, min(position, len(plus))), slug)
    site.write_json(HOME, home)
    return {"added": slug, "position": plus.index(slug), "count": len(plus)}


def plus_remove(site: Site, slug: str) -> dict:
    home = site.home()
    plus = home.get("alsoToday", {}).get("plus", [])
    if slug not in plus:
        raise SiteError(f"{slug} is not in the 'Also today' list")
    plus.remove(slug)
    site.write_json(HOME, home)
    return {"removed": slug, "count": len(plus)}


def plus_trim(site: Site, keep: int) -> dict:
    home = site.home()
    plus = home.get("alsoToday", {}).get("plus", [])
    dropped = plus[keep:]
    home["alsoToday"]["plus"] = plus[:keep]
    if dropped:
        site.write_json(HOME, home)
    return {"kept": len(plus[:keep]), "dropped": dropped}


def number_add(site: Site, value: str, label: str, source: str, position: int = 0,
               keep: int | None = None) -> dict:
    home = site.home()
    nums = home.setdefault("numbers", [])
    nums.insert(max(0, min(position, len(nums))), {"value": value, "label": label, "source": source})
    dropped = []
    if keep is not None and len(nums) > keep:
        dropped = nums[keep:]
        del nums[keep:]
    site.write_json(HOME, home)
    return {"numbers": nums, "dropped": dropped}


def number_remove(site: Site, index: int) -> dict:
    home = site.home()
    nums = home.get("numbers", [])
    if not 0 <= index < len(nums):
        raise SiteError(f"Number index out of range: {index}")
    gone = nums.pop(index)
    site.write_json(HOME, home)
    return {"removed": gone, "count": len(nums)}


def funding_add(site: Site, title: str, funder: str, deadline: str, url: str) -> dict:
    check_date(deadline, "deadline")
    if not url.startswith(("http://", "https://")):
        raise SiteError(f"Funding url must start with http:// or https://, got {url!r}")
    home = site.home()
    funding = home.setdefault("funding", [])
    if any(f.get("url") == url for f in funding):
        raise SiteError(f"A funding call with this url is already listed: {url}")
    item = {"title": title, "funder": funder, "deadline": deadline, "url": url}
    funding.append(item)
    funding.sort(key=lambda f: f.get("deadline", ""))
    site.write_json(HOME, home)
    return {"added": item, "count": len(funding)}


def funding_remove(site: Site, url: str) -> dict:
    home = site.home()
    funding = home.get("funding", [])
    for i, f in enumerate(funding):
        if f.get("url") == url:
            funding.pop(i)
            site.write_json(HOME, home)
            return {"removed": f, "count": len(funding)}
    raise SiteError(f"No funding call with url {url}")


def funding_prune(site: Site, today: str | None = None) -> dict:
    today = check_date(today or today_dhaka(), "today")
    home = site.home()
    funding = home.get("funding", [])
    gone = [f for f in funding if f.get("deadline", "") < today]
    if gone:
        home["funding"] = [f for f in funding if f.get("deadline", "") >= today]
        site.write_json(HOME, home)
    return {"today": today, "removed": gone, "remaining": len(funding) - len(gone)}


def pills_set(site: Site, funding_open=None, new_reports=None, key_numbers=None) -> dict:
    home = site.home()
    pills = home.setdefault("pills", {})
    for key, val in (("fundingOpen", funding_open), ("newReports", new_reports), ("keyNumbers", key_numbers)):
        if val is not None:
            if val < 0:
                raise SiteError(f"{key} cannot be negative")
            pills[key] = val
    site.write_json(HOME, home)
    return pills


def spotlight_set_today(site: Site, date: str, text: str, sources: list[str]) -> dict:
    home = site.home()
    spot = home.get("spotlight")
    if not spot:
        raise SiteError("There is no spotlight on the homepage")
    parsed = []
    for s in sources:
        if "|" not in s:
            raise SiteError(f"Source must be 'Name|https://url', got {s!r}")
        name, url = s.split("|", 1)
        parsed.append({"name": name.strip(), "url": url.strip()})
    spot["today"] = {"date": date, "text": text, "sources": parsed}
    site.write_json(HOME, home)
    return spot["today"]
