import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => JSON.parse(fs.readFileSync(path.isAbsolute(file) ? file : path.join(root, file), "utf8"));
const write = (file, value) => fs.writeFileSync(path.join(root, file), JSON.stringify(value, null, 2));
const stripRefs = (value) => String(value ?? "").replace(/\[reference:\d+\]/g, "").replace(/\s+/g, " ").trim();
const normalize = (value) => stripRefs(value)
  .replace(/\([^)]*\)/g, " ")
  .replace(/[أإآ]/g, "ا")
  .replace(/ة/g, "ه")
  .replace(/ى/g, "ي")
  .replace(/[^\p{L}\p{N}]+/gu, "")
  .toLowerCase();
const officialUrl = (value) => {
  const raw = stripRefs(value);
  if (!/^https?:\/\//i.test(raw)) return null;
  try {
    const url = new URL(raw);
    url.hash = "";
    return url.href.replace(/\/$/, "");
  } catch {
    return null;
  }
};
const isOfficialJournalUrl = (value) => {
  const url = new URL(value);
  return !["scimagojr.com", "www.scimagojr.com", "heinonline.org", "www.heinonline.org"].includes(url.hostname);
};

const sourceFiles = [
  { path: "/home/ubuntu/upload/pasted_file_lPep79_deepseek_json_20260819_2785e0.json", rootKey: "المجلات_الدولية_المتخصصة", origin: "ملف المجلات الدولية lPep79" },
  { path: "/home/ubuntu/upload/pasted_file_Ypr81X_deepseek_json_20260819_c73d8f.json", rootKey: "المجلات_الدولية_التوسع_المستقبلي", origin: "ملف المجلات الدولية Ypr81X" },
  { path: "/home/ubuntu/upload/pasted_file_uvadjF_deepseek_json_20260819_484873.json", rootKey: "المجلات_الدولية_المتخصصة_النهائية", origin: "ملف المجلات الدولية uvadjF" },
  { path: "/home/ubuntu/upload/pasted_file_XWrDHY_deepseek_json_20260819_8e53e2.json", rootKey: "المجلات_الدولية_المتقدمة", origin: "ملف المجلات الدولية XWrDHY" },
  { path: "/home/ubuntu/upload/pasted_file_EOywHc_deepseek_json_20260819_7e1fc5.json", rootKey: "المجلات_الدولية_المتقدمة_الدفعة_الثالثة", origin: "ملف المجلات الدولية EOywHc" },
];
const items = read("items.json");
const existingLinks = new Set(items.map((item) => String(item.link_direct || "").replace(/\/$/, "")).filter(Boolean));
const existingKeys = new Set(items
  .filter((item) => String(item.id).startsWith("journal_link_"))
  .map((item) => `دولية|${normalize(item.title)}`));
const raw = sourceFiles.flatMap((source) => Object.entries(read(source.path)[source.rootKey] || {})
  .flatMap(([topic, journals]) => journals.map((journal) => ({ topic: topic.replaceAll("_", " "), journal, origin: source.origin }))));

const candidates = [];
const skipped = { unavailable_or_invalid_link: [], unverified_official_source: [], already_imported: [], duplicate_within_inputs: [] };
const seenTitles = new Set();
const seenLinks = new Set();
for (const source of raw) {
  const title = stripRefs(source.journal["الاسم"]);
  const link = officialUrl(source.journal["الرابط"]);
  const record = {
    country: "دولية",
    topic: source.topic,
    title,
    publisher: stripRefs(source.journal["الناشر"]),
    frequency: stripRefs(source.journal["التردد"]),
    issn: stripRefs(source.journal["ISSN"]),
    year: stripRefs(source.journal["سنة_التأسيس"]),
    notes: stripRefs(source.journal["ملاحظات"]),
    link: link || stripRefs(source.journal["الرابط"]),
    origin: source.origin,
  };
  if (!title || !link) {
    skipped.unavailable_or_invalid_link.push(record);
    continue;
  }
  if (!record.publisher || record.publisher === "غير محدد" || !isOfficialJournalUrl(link)) {
    skipped.unverified_official_source.push(record);
    continue;
  }
  const key = `دولية|${normalize(title)}`;
  if (existingKeys.has(key) || existingLinks.has(link)) {
    skipped.already_imported.push(record);
    continue;
  }
  if (seenTitles.has(key) || seenLinks.has(link)) {
    skipped.duplicate_within_inputs.push(record);
    continue;
  }
  seenTitles.add(key);
  seenLinks.add(link);
  candidates.push(record);
}

const report = {
  total_raw_records: raw.length,
  accepted_candidates: candidates.length,
  accepted_by_topic: Object.fromEntries([...new Set(candidates.map((item) => item.topic))].map((topic) => [topic, candidates.filter((item) => item.topic === topic).length])),
  skipped_counts: Object.fromEntries(Object.entries(skipped).map(([key, values]) => [key, values.length])),
  skipped,
};
write("international_journals_preview.json", { journals: candidates, report });
console.log(JSON.stringify(report, null, 2));
