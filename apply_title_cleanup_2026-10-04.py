#!/usr/bin/env python3
"""Apply only the approved title-cleanup plan and isolate unclear titles privately."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLAN_PATH = ROOT / "title_cleanup_2026-10-04_final_plan.json"
ROOT_ITEMS = ROOT / "items.json"
PUBLIC_ITEMS = ROOT / "client/public/items.json"
ROOT_STATS = ROOT / "stats.json"
PUBLIC_STATS = ROOT / "client/public/stats.json"
INTERNAL_DIR = ROOT / "internal"
INTERNAL_PATH = INTERNAL_DIR / "title_review_2026-10-04.json"
EXECUTION = ROOT / "title_cleanup_2026-10-04_execution.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rebuild_stats(items: list[dict], previous: dict) -> dict:
    stats = dict(previous)
    stats.update({
        "total_items": len(items),
        "categories": dict(sorted(Counter(str(x.get("category") or "غير مصنف") for x in items).items())),
        "sources": dict(sorted(Counter(str(x.get("source") or "غير محدد") for x in items).items())),
        "material_types": dict(sorted(Counter(str(x.get("material_type") or "غير محدد") for x in items).items())),
        "file_types": dict(sorted(Counter(str(x.get("file_type") or "غير محدد") for x in items).items())),
        "featured_count": sum(bool(x.get("is_featured")) for x in items),
        "with_download_links": sum(int(x.get("download_links_count") or 0) > 0 for x in items),
    })
    return stats


def main() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    actions = {row["id"]: row for row in plan["items"]}
    assert len(actions) == len(plan["items"]), "duplicate IDs in title-cleanup plan"

    before_root_hash = digest(ROOT_ITEMS)
    before_public_hash = digest(PUBLIC_ITEMS)
    assert before_root_hash == before_public_hash, "root and public data differ before cleanup"
    before_items = json.loads(ROOT_ITEMS.read_text(encoding="utf-8"))
    public_items = json.loads(PUBLIC_ITEMS.read_text(encoding="utf-8"))
    assert before_items == public_items, "root and public JSON differ semantically before cleanup"
    before_ids = [row["id"] for row in before_items]
    assert len(before_ids) == len(set(before_ids)), "duplicate IDs before cleanup"
    assert set(actions) <= set(before_ids), "planned title ID missing from data"

    rewrite = {item_id: row for item_id, row in actions.items() if row["action"] == "REWRITE"}
    internal = {item_id: row for item_id, row in actions.items() if row["action"] == "INTERNAL"}
    assert set(rewrite).isdisjoint(internal)

    isolated: list[dict] = []
    after_items: list[dict] = []
    changed: list[dict] = []
    for item in before_items:
        item_id = item["id"]
        if item_id in internal:
            isolated.append({
                "record": item,
                "original_title": item.get("title", ""),
                "reason": internal[item_id]["reason"],
                "review_action": "INTERNAL",
                "isolated_at": "2026-10-04",
            })
            continue
        new_item = dict(item)
        if item_id in rewrite:
            new_title = rewrite[item_id]["final_title"].strip()
            assert new_title and new_title != item.get("title", ""), f"invalid rewrite for {item_id}"
            changed.append({"id": item_id, "before": item.get("title", ""), "after": new_title})
            new_item["title"] = new_title
        after_items.append(new_item)

    assert len(changed) == len(rewrite), (len(changed), len(rewrite))
    assert len(isolated) == len(internal), (len(isolated), len(internal))
    after_ids = [row["id"] for row in after_items]
    assert len(after_ids) == len(set(after_ids)), "duplicate IDs after cleanup"
    assert set(before_ids) == set(after_ids) | set(internal), "unexpected ID change"
    unchanged_before = {x["id"]: x for x in before_items if x["id"] not in rewrite and x["id"] not in internal}
    unchanged_after = {x["id"]: x for x in after_items if x["id"] in unchanged_before}
    assert unchanged_before == unchanged_after, "non-target record changed"

    previous_stats = json.loads(ROOT_STATS.read_text(encoding="utf-8"))
    stats = rebuild_stats(after_items, previous_stats)
    INTERNAL_DIR.mkdir(exist_ok=True)
    internal_payload = {
        "metadata": {
            "purpose": "سجلات عُزلت عن واجهة المكنز لأن عناوينها غير واضحة ولا يمكن تحريرها بثقة.",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "count": len(isolated),
            "publicly_visible": False,
        },
        "items": isolated,
    }

    for path, data in [(ROOT_ITEMS, after_items), (PUBLIC_ITEMS, after_items), (ROOT_STATS, stats), (PUBLIC_STATS, stats), (INTERNAL_PATH, internal_payload)]:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    assert digest(ROOT_ITEMS) == digest(PUBLIC_ITEMS), "root and public item hashes diverged"
    assert json.loads(ROOT_STATS.read_text(encoding="utf-8")) == json.loads(PUBLIC_STATS.read_text(encoding="utf-8"))
    execution = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "before_total": len(before_items),
        "after_public_total": len(after_items),
        "rewritten_titles": len(changed),
        "internally_isolated": len(isolated),
        "internal_file": str(INTERNAL_PATH.relative_to(ROOT)),
        "before_items_sha256": before_root_hash,
        "after_items_sha256": digest(ROOT_ITEMS),
        "changed": changed,
        "internal_ids": sorted(internal),
        "integrity": {
            "public_ids_preserved_except_internal": True,
            "non_target_records_unchanged": True,
            "no_duplicate_ids": True,
            "root_public_items_match": True,
            "root_public_stats_match": True,
        },
    }
    EXECUTION.write_text(json.dumps(execution, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: execution[k] for k in ["before_total", "after_public_total", "rewritten_titles", "internally_isolated", "internal_file"]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
