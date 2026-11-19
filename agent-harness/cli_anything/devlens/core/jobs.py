"""Job listings in src/data/jobs.json."""

from __future__ import annotations

from cli_anything.devlens.core.site import (JOBS, Site, SiteError, check_date,
                                            long_date, today_dhaka)

FIELD_ORDER = ["title", "org", "badge", "sector", "url", "location", "nationals", "consultancy",
               "contract", "ref", "deadline", "deadlineText", "button", "added", "featured"]


def sectors(site: Site) -> list[dict]:
    return site.jobs_data()["sectors"]


def is_open(job: dict, today: str) -> bool:
    return not job.get("deadline") or job["deadline"] >= today


def list_jobs(site: Site, sector=None, status="all", org=None, today=None) -> list[dict]:
    today = today or today_dhaka()
    out = []
    for i, j in enumerate(site.jobs_data()["jobs"]):
        if sector and j.get("sector") != sector:
            continue
        if org and org.lower() not in j.get("org", "").lower():
            continue
        if status == "open" and not is_open(j, today):
            continue
        if status == "expired" and is_open(j, today):
            continue
        out.append({"index": i, **j, "open": is_open(j, today)})
    return out


def add(site: Site, title: str, org: str, sector: str, url: str, location: str,
        deadline: str | None = None, contract: str = "Full-time", ref: str = "",
        badge: str | None = None, nationals: bool = False, consultancy: bool = False,
        button: str = "View advert", featured: str | None = None,
        added: str | None = None, deadline_text: str | None = None) -> dict:
    data = site.jobs_data()
    ids = [s["id"] for s in data["sectors"]]
    if sector not in ids:
        raise SiteError(f"Unknown sector {sector!r}; choose one of: {', '.join(ids)}")
    if not url.startswith(("http://", "https://")):
        raise SiteError(f"Job url must start with http:// or https://, got {url!r}")
    if any(j.get("url") == url for j in data["jobs"]):
        raise SiteError(f"A job with this url is already listed: {url}")
    if deadline:
        check_date(deadline, "deadline")
    job = {
        "title": title.strip(), "org": org.strip(), "badge": (badge or org).strip(),
        "sector": sector, "url": url, "location": location.strip(),
        "nationals": nationals, "consultancy": consultancy, "contract": contract,
        "ref": ref, "deadline": deadline,
        "deadlineText": deadline_text or (long_date(deadline) if deadline else "Open until filled"),
        "button": button, "added": check_date(added or today_dhaka(), "added"),
    }
    if featured:
        job["featured"] = featured
    data["jobs"].insert(0, job)
    site.write_json(JOBS, data)
    return job


def _find(data: dict, url: str | None, index: int | None) -> int:
    if url is not None:
        for i, j in enumerate(data["jobs"]):
            if j.get("url") == url:
                return i
        raise SiteError(f"No job with url {url}")
    if index is not None:
        if not 0 <= index < len(data["jobs"]):
            raise SiteError(f"Job index out of range: {index}")
        return index
    raise SiteError("Pass --url or --index")


def remove(site: Site, url: str | None = None, index: int | None = None) -> dict:
    data = site.jobs_data()
    job = data["jobs"].pop(_find(data, url, index))
    site.write_json(JOBS, data)
    return {"removed": job["title"], "org": job.get("org"), "url": job.get("url")}


def update(site: Site, url: str | None = None, index: int | None = None, **fields) -> dict:
    data = site.jobs_data()
    i = _find(data, url, index)
    job = data["jobs"][i]
    fields = {k: v for k, v in fields.items() if v is not None}
    if not fields:
        raise SiteError("Nothing to update; pass at least one field")
    if "sector" in fields and fields["sector"] not in [s["id"] for s in data["sectors"]]:
        raise SiteError(f"Unknown sector {fields['sector']!r}")
    if "deadline" in fields:
        check_date(fields["deadline"], "deadline")
        fields.setdefault("deadlineText", long_date(fields["deadline"]))
    job.update(fields)
    site.write_json(JOBS, data)
    return {"index": i, "job": job, "changed": sorted(fields)}


def prune(site: Site, today: str | None = None) -> dict:
    today = check_date(today or today_dhaka(), "today")
    data = site.jobs_data()
    keep = [j for j in data["jobs"] if is_open(j, today)]
    gone = [j for j in data["jobs"] if not is_open(j, today)]
    if gone:
        data["jobs"] = keep
        site.write_json(JOBS, data)
    return {"today": today, "removed": len(gone), "remaining": len(keep),
            "removed_jobs": [{"title": j["title"], "org": j.get("org"), "deadline": j.get("deadline")}
                             for j in gone]}
