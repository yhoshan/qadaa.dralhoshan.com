#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "backups/title_cleanup_2026-10-04"
PLAN = json.loads((ROOT / "title_cleanup_2026-10-04_final_plan.json").read_text(encoding="utf-8"))
EXECUTION = json.loads((ROOT / "title_cleanup_2026-10-04_execution.json").read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    before = load(BACKUP / "items_root_before.json")
    items = load(ROOT / "items.json")
    public = load(ROOT / "client/public/items.json")
    stats = load(ROOT / "stats.json")
    public_stats = load(ROOT / "client/public/stats.json")
    internal = load(ROOT / "internal/title_review_2026-10-04.json")
    actions = {x["id"]: x for x in PLAN["items"]}
    rewrite = {item_id: x for item_id, x in actions.items() if x["action"] == "REWRITE"}
    hidden = {item_id: x for item_id, x in actions.items() if x["action"] == "INTERNAL"}
    before_by_id = {x["id"]: x for x in before}
    after_by_id = {x["id"]: x for x in items}

    assert sha(ROOT / "items.json") == sha(ROOT / "client/public/items.json")
    assert items == public
    assert stats == public_stats
    assert len(before) == 45830
    assert len(items) == 45814
    assert stats["total_items"] == len(items)
    assert len(items) == len({x["id"] for x in items})
    assert len(hidden) == 16 and len(rewrite) == 1414
    assert set(before_by_id) == set(after_by_id) | set(hidden)
    assert not (set(hidden) & set(after_by_id))
    assert len(internal["items"]) == len(hidden)
    assert internal["metadata"]["publicly_visible"] is False

    isolated_by_id = {x["record"]["id"]: x for x in internal["items"]}
    assert set(isolated_by_id) == set(hidden)
    for item_id, action in hidden.items():
        assert isolated_by_id[item_id]["record"] == before_by_id[item_id]
        assert isolated_by_id[item_id]["original_title"] == before_by_id[item_id]["title"]
    for item_id, action in rewrite.items():
        before_record = before_by_id[item_id]
        after_record = after_by_id[item_id]
        assert after_record["title"] == action["final_title"]
        expected = dict(before_record)
        expected["title"] = action["final_title"]
        assert after_record == expected, item_id
        assert after_record["title"].strip()
    for item_id, before_record in before_by_id.items():
        if item_id not in rewrite and item_id not in hidden:
            assert after_by_id[item_id] == before_record, item_id

    assert EXECUTION["before_total"] == len(before)
    assert EXECUTION["after_public_total"] == len(items)
    assert EXECUTION["rewritten_titles"] == len(rewrite)
    assert EXECUTION["internally_isolated"] == len(hidden)
    assert set(EXECUTION["internal_ids"]) == set(hidden)
    assert stats["qadaa_count"] + stats["nizam_count"] + stats["mohama_count"] == len(items)
    assert sum(stats["categories"].values()) == len(items)
    assert sum(stats["sources"].values()) == len(items)
    assert sum(stats["material_types"].values()) == len(items)
    assert sum(stats["file_types"].values()) == len(items)

    public_titles = "\n".join(x["title"] for x in items)
    # Scan only updated titles for noisy file suffixes to avoid false positives in untouched records.
    noisy = []
    for item_id in rewrite:
        title = after_by_id[item_id]["title"]
        if title.lower().endswith((".pdf", ".doc", ".docx", ".zip", ".rar")) or "File كتاب" in title or " version " in title.lower():
            noisy.append((item_id, title))
    assert not noisy, noisy[:10]

    result = {
        "before_total": len(before),
        "after_public_total": len(items),
        "rewritten_titles": len(rewrite),
        "internally_isolated": len(hidden),
        "root_public_items_sha256": sha(ROOT / "items.json"),
        "root_public_stats_sha256": sha(ROOT / "stats.json"),
        "hero_counts": {k: stats[k] for k in ["qadaa_count", "nizam_count", "mohama_count"]},
        "checks": {
            "root_public_items_match": True,
            "root_public_stats_match": True,
            "non_target_records_unchanged": True,
            "rewrites_only_change_title": True,
            "internal_records_preserved_privately": True,
            "no_duplicate_ids": True,
            "no_empty_public_titles": True,
            "hero_total_matches": True,
            "updated_titles_have_no_file_suffix_noise": True,
        },
    }
    (ROOT / "title_cleanup_2026-10-04_validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
