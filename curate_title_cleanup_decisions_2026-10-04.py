#!/usr/bin/env python3
"""Build the final, reviewable title-cleanup plan.
- Deterministic technical cleanup is applied only to safe candidates.
- Semantically unclear records are sent to a private internal review file.
- Manual overrides preserve conservative editorial judgment.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "title_cleanup_2026-10-04_model_review.json"
INVENTORY = ROOT / "title_cleanup_2026-10-04_inventory.json"
OUT = ROOT / "title_cleanup_2026-10-04_final_plan.json"

# Items whose core title is sufficiently visible even if the trailing file name was truncated.
MANUAL_REWRITES = {
    "alexandria_cbz_39663": "مد الباع لإثبات حرمة النكاح فوق الرباع — الكراسة الأولى",
    "archive_AAlexandrina-050213": "وثائق في أحكام القضاء الجنائي في الأندلس",
    "archive_AAlexandrina-050401": "أصول المرافعات ومذكرات الدفاع في الدعاوى والطعون",
    "archive_AAlexandrina-051245": "أصول صحف الدعاوى على ضوء آخر أحكام النقض",
    "archive_AAlexandrina-052024": "موسوعة القضاء التأديبي وطرق الطعن في الأحكام",
    "archive_AAlexandrina-113729": "شرح قانون العقوبات التكميلي في جرائم المخدرات والأسلحة",
    "archive_AAlexandrina-155691": "ظفر القاضي بما يجب في القضاء على القاضي",
    "archive_AAlexandrina-170866": "قانون العقوبات وفقًا للتعديلات المدخلة عليه",
    "archive_AAlexandrina-195144": "قانون العقوبات الأهلي مع التعديلات الطارئة عليه",
    "archive_AAlexandrina-196359": "نظام القضاء والإدارة",
    "archive_AAlexandrina-196360": "نظام القضاء والإدارة",
    "archive_AAlexandrina-438346": "مختصر كتاب مباحث المرافعات الشرعية",
    "archive_AAlexandrina-441442": "شرح قانون العقوبات التكميلي في جرائم المخدرات",
    "archive_AAlexandrina-464623": "القضاء الإداري: دراسة مقارنة",
    "archive_AAlexandrina-473625": "قانون الأحوال الشخصية على ضوء الفقه الجعفري",
    "archive_AAlexandrina-477556": "شرح قانون الإجراءات الجنائية: الدعوى الجنائية والاستدلالات",
    "archive_AAlexandrina-483271": "القضاء والانتهاكات الحكومية لحقوق الإنسان",
    "archive_AAlexandrina-483628": "شرح قانون العقوبات: القسم العام",
    "archive_AAskZad-1163518": "الموسوعة القضائية الحديثة في الشرح والتعليق على قانون الإثبات في المواد المدنية والتجارية",
    "archive_8719.": "القانون رقم 87-19 المتعلق بضبط كيفية استغلال الأراضي الفلاحية التابعة للأملاك الوطنية وتحديد حقوق المنتجين وواجباتهم",
    "muath_38": "أبرز الأخطاء في فهم التعميم",
    "muath_5": "مشروع اللائحة التنفيذية لنظام المحاماة",
    "muath_86": "كتاب الوسيط للسنهوري",
    "muath_9": "مبادرة تخفيض سداد غرامات المخالفات المرورية",
    "qadaa_10189": "الحسبة والسياسة الجنائية — سعد العريفي",
    "rasail_15188": "الحسبة والسياسة الجنائية",
    "rasail_17451": "الحسبة والسياسة الجنائية — الجزء الأول",
    "rasail_17452": "الحسبة والسياسة الجنائية — الجزء الثاني",
    "risail_19720": "الحسبة والسياسة الجنائية",
    "qadi_ahdal_102721": "نظام الضمانات",
    "qadi_ahdal_85445": "الجريمة الإلكترونية",
    "qadi_ahdal_85451": "إبرام العقد الإلكتروني",
    "suwaid_title_145": "المهارات الناعمة للمحامي",
    "suwaid_title_158": "خطط قانونية لاستغلال الأوقات",
    "suwaid_title_408": "سلسلة نظام مكافحة جريمة التحرش",
    "suwaid_title_803": "تعيين المصفي وعزله",
    "great_law_10068": "الأساس الاقتصادي لمنح الجنسية: دراسة قانونية مقارنة — رسالة ماجستير",
    "great_law_10297": "المسؤولية الجنائية عن الابتزاز الإلكتروني عبر مواقع التواصل الاجتماعي: دراسة مقارنة — رسالة ماجستير",
    "great_law_10301": "المسؤولية الجنائية الناشئة عن الابتزاز الإلكتروني: دراسة مقارنة — رسالة ماجستير",
    "great_law_13322": "التنظيم القانوني لنشاط التطوير العقاري: دراسة مقارنة — رسالة ماجستير",
    "great_law_3290": "جريدة الوقائع العراقية — العدد 4610",
    "great_law_8533": "الحماية المدنية للقاصر: دراسة مقارنة — أطروحة دكتوراه",
    "great_law_8547": "الإطار الدستوري للحق في الخصوصية الإنجابية وأثره على حق الجنين في الحياة: دراسة مقارنة",
    "great_law_8658": "الالتزام الدولي بحماية التنوع البيولوجي — أطروحة دكتوراه",
    "great_law_8670": "نفاذ أحكام القضاء الدستوري: دراسة مقارنة — رسالة ماجستير",
    "great_law_8689": "التنظيم القانوني لأوامر تغيير عقد الأشغال العامة — رسالة ماجستير",
    "great_law_8707": "المسؤولية عن الحماية في القانون الدولي — أطروحة دكتوراه",
    "great_law_9232": "تنازع القوانين في مجال الالتزامات غير التعاقدية: دراسة تأصيلية تحليلية مقارنة",
    "great_law_9270": "المسؤولية المدنية الناشئة عن نقل الأمراض المعدية — رسالة ماجستير",
    "great_law_9271": "أثر تغير الظروف في المرحلة السابقة على التعاقد: دراسة مقارنة — رسالة ماجستير",
    "great_law_9272": "التنظيم القانوني للحسابات المصرفية الخاملة: دراسة مقارنة — رسالة ماجستير",
    "great_law_9277": "قبول الأجنبي في إقليم الدولة: دراسة مقارنة — أطروحة دكتوراه",
}

# The title text cannot be made reliable without inventing missing content.
ADDITIONAL_INTERNAL = {
    "archive_AAlexandrina-422510",
    "archive_AAlexandrina-423703",
    "great_law_4174",
    "intlaw_90",
    "intlaw_91",
    "legal_lib_13376",
    "najran_art_14518",
    "najran_art_17529",
    "najran_art_17609",
    "rasail_16191",
    "risail_34829",
    "suwaid_title_224",
    "suwaid_title_354",
    "suwaid_title_448",
    "suwaid_title_530",
}


def main() -> None:
    rows = json.loads(INPUT.read_text(encoding="utf-8"))
    original_inventory = {
        row["id"]: row for row in json.loads(INVENTORY.read_text(encoding="utf-8"))
    }
    reviewed_ids = {row["id"] for row in rows}
    extra_safe_rows = [
        row for item_id, row in original_inventory.items()
        if item_id not in reviewed_ids
    ]
    assert all(row["safe_auto"] for row in extra_safe_rows), "Unreviewed semantic records are not allowed"
    rows.extend({
        **row,
        "decision": "REWRITE",
        "confidence": "high",
        "rationale": "تنظيف تقني محافظ لرقم فهرسة أرشيفي فقط.",
    } for row in extra_safe_rows)
    ids = {row["id"] for row in rows}
    assert set(MANUAL_REWRITES) <= ids
    assert ADDITIONAL_INTERNAL <= ids
    final = []
    for row in rows:
        record = dict(row)
        item_id = record["id"]
        if item_id in ADDITIONAL_INTERNAL:
            action = "INTERNAL"
            title = ""
            reason = "لا يظهر من النص عنوان مستقل مكتمل يمكن عرضه بموثوقية."
        elif item_id in MANUAL_REWRITES:
            action = "REWRITE"
            title = MANUAL_REWRITES[item_id]
            reason = "تحرير محافظ يستبقي الموضوع الظاهر ويزيل الضوضاء أو الانقطاع."
        elif record["decision"] == "INTERNAL":
            action = "INTERNAL"
            title = ""
            reason = record["rationale"]
        elif record["safe_auto"]:
            action = "REWRITE"
            # The semantic model is advisory only for safe technical records.
            # Preserve the deterministic proposal which only removes file-name noise.
            title = original_inventory[item_id]["proposed_title"]
            reason = "تنظيف تقني محافظ لاسم الملف أو تنسيق العنوان فقط."
        elif record["decision"] == "REWRITE" and record["confidence"] in {"high", "medium"}:
            action = "REWRITE"
            title = record["proposed_title"]
            reason = record["rationale"]
        else:
            action = "INTERNAL"
            title = ""
            reason = "عنوان غير مكتمل أو اقتراح منخفض الثقة؛ عُزل بدل عرض عنوان غير موثوق."
        if action == "REWRITE":
            assert title and len(title.strip()) >= 4
            assert not title.lower().endswith((".pdf", ".doc", ".docx", ".zip"))
        final.append({
            "id": item_id,
            "original_title": record["title"],
            "action": action,
            "final_title": title,
            "source": record["source"],
            "reason": reason,
        })
    summary = {
        "candidates": len(final),
        "rewrite": sum(x["action"] == "REWRITE" for x in final),
        "internal": sum(x["action"] == "INTERNAL" for x in final),
        "manual_rewrites": len(MANUAL_REWRITES),
        "additional_internal": len(ADDITIONAL_INTERNAL),
    }
    OUT.write_text(json.dumps({"summary": summary, "items": final}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
