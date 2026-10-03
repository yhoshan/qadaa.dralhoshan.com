#!/usr/bin/env python3
"""Download and inventory the public KSU Law & Political Sciences journal archive.

This script only creates source inventory files outside the web project data files.
It downloads official issue PDFs temporarily to extract article metadata later.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ARCHIVE_URL = "https://clps.ksu.edu.sa/en/node/1070"
WORKDIR = Path("/home/ubuntu/ksu-law-journal-archive-2026-10-03")
PDF_DIR = WORKDIR / "issues"
MANIFEST_PATH = WORKDIR / "archive_manifest.json"
HTML_PATH = WORKDIR / "archive_page.html"
USER_AGENT = "Makanez-Catalogue-Research/1.0 (+https://qadaa.dralhoshan.com)"
EXPECTED_ISSUES = 32
WORKERS = 4
TIMEOUT = (15, 180)


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def issue_filename(index: int, title: str) -> str:
    safe = re.sub(r"[^0-9A-Za-z._-]+", "_", title).strip("_")
    return f"{index:02d}_{safe[:100] or 'issue'}.pdf"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def request(url: str) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT, stream=True)
            response.raise_for_status()
            return response
        except Exception as exc:  # retry transient server/network failures
            last_error = exc
            if attempt == 3:
                raise
            time.sleep(attempt * 1.5)
    raise RuntimeError(str(last_error))


def fetch_issue(row: dict[str, Any]) -> dict[str, Any]:
    target = PDF_DIR / row["local_filename"]
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        if target.exists() and target.stat().st_size > 1024 and target.read_bytes()[:4] == b"%PDF":
            row.update({
                "download_status": "cached",
                "local_path": str(target),
                "bytes": target.stat().st_size,
                "sha256": sha256(target),
            })
            return row
        response = request(row["official_issue_url"])
        temp = target.with_suffix(".part")
        with temp.open("wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)
        if temp.stat().st_size <= 1024 or temp.read_bytes()[:4] != b"%PDF":
            temp.unlink(missing_ok=True)
            raise RuntimeError("Response is not a valid PDF")
        temp.replace(target)
        row.update({
            "download_status": "downloaded",
            "local_path": str(target),
            "bytes": target.stat().st_size,
            "sha256": sha256(target),
            "content_type": response.headers.get("content-type", ""),
        })
    except Exception as exc:
        row.update({"download_status": "failed", "error": f"{type(exc).__name__}: {exc}"})
    return row


def main() -> None:
    WORKDIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    response = request(ARCHIVE_URL)
    html = response.text
    HTML_PATH.write_text(html, encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    issues: list[dict[str, Any]] = []
    for a in soup.select("a[href]"):
        href = a.get("href", "").strip()
        title = compact(a.get_text(" ", strip=True))
        if not href.lower().split("?")[0].endswith(".pdf"):
            continue
        official_url = urljoin(ARCHIVE_URL, href)
        if official_url in seen:
            continue
        seen.add(official_url)
        issues.append({
            "archive_index": len(issues) + 1,
            "issue_label": title,
            "official_issue_url": official_url,
            "local_filename": issue_filename(len(issues) + 1, title),
        })
    if len(issues) != EXPECTED_ISSUES:
        raise RuntimeError(f"Expected {EXPECTED_ISSUES} public issue PDFs; found {len(issues)}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        issues = list(executor.map(fetch_issue, issues))
    failures = [x for x in issues if x["download_status"] == "failed"]
    result = {
        "source": "مجلة جامعة الملك سعود - الحقوق والعلوم السياسية",
        "archive_url": ARCHIVE_URL,
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "expected_issues": EXPECTED_ISSUES,
        "issue_count": len(issues),
        "downloaded_count": len(issues) - len(failures),
        "failed_count": len(failures),
        "issues": issues,
    }
    MANIFEST_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("issue_count", "downloaded_count", "failed_count")}, ensure_ascii=False))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
