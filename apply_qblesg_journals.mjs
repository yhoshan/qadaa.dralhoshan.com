import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => JSON.parse(fs.readFileSync(path.join(root, file), "utf8"));
const write = (file, value) => fs.writeFileSync(path.join(root, file), JSON.stringify(value, null, 2));
const stripRefs = (value) => String(value ?? "").replace(/\[reference:\d+\]/g, "").replace(/\s+/g, " ").trim();
const normalize = (value) => stripRefs(value)
  .replace(/\([^)]*\)/g, " ")
  .replace(/[أإآ]/g, "ا")
  .replace(/ة/g, "ه")
  .replace(/ى/g, "ي")
  .replace(/[^\p{L}\p{N}]+/gu, "")
  .toLowerCase();

const audit = read("audit_qblesg_journals_report.json");
const input = JSON.parse(fs.readFileSync("/home/ubuntu/upload/pasted_file_qBLeSG_deepseek_json_20260819_b6802f.json", "utf8"));
const items = read("items.json");
const publicItems = read("client/public/items.json");
const stats = read("client/public/stats.json");

if (items.length !== publicItems.length) throw new Error("تعارض بين نسخة البيانات الخاصة والعامة");

const rawRecords = Object.entries(input["المجلات_والنشرات_القانونية_الجديدة_2026"] || {})
  .flatMap(([country, journals]) => journals.map((journal) => ({ country, journal })));
const originalByIdentity = new Map(rawRecords.map(({ country, journal }) => [`${country}|${stripRefs(journal["الاسم"])}`, journal]));
const existingLinks = new Set(items.map((item) => String(item.link_direct || "").replace(/\/$/, "")).filter(Boolean));
const existingIds = new Set(items.map((item) => String(item.id)));

const journals = audit.candidates_for_confirmation.map((candidate) => {
  const source = originalByIdentity.get(`${candidate.country}|${candidate.title}`);
  if (!source) throw new Error(`تعذّر استرجاع بيانات: ${candidate.title}`);
  const identity = `${candidate.country}|${normalize(candidate.title)}|${normalize(candidate.publisher)}`;
  const id = `journal_link_${crypto.createHash("sha1").update(`${identity}|${candidate.link}`).digest("hex").slice(0, 16)}`;
  return {
    id,
    title: candidate.title,
    author: "",
    investigator: "",
    publisher: candidate.publisher,
    year: stripRefs(source["سنة_التأسيس"]),
    link_telegram: "",
    link_drive: "",
    link_direct: candidate.link,
    source: `فهرس المجلات المتخصصة — ${candidate.country}`,
    category: "المجلات القانونية",
    material_type: "مجلة",
    file_type: "رابط",
    file_size: "",
    pages_count: "",
    is_featured: false,
    download_links_count: 1,
    country: candidate.country,
    issn: stripRefs(source["ISSN"]),
    frequency: stripRefs(source["التردد"]),
    notes: candidate.notes,
    import_origin: "ملف المجلات الجديد qBLeSG",
  };
});

const conflicts = journals.filter((journal) => existingIds.has(journal.id) || existingLinks.has(journal.link_direct));
if (conflicts.length) throw new Error(`تكرار قبل الإدماج: ${conflicts.map((item) => item.title).join("، ")}`);

const stamp = new Date().toISOString().replace(/[:.]/g, "-").replace("T", "_").replace("Z", "");
const backup = path.join(root, "backups", `official-journals-qblesg-${stamp}`);
fs.mkdirSync(backup, { recursive: true });
for (const file of ["items.json", "client/public/items.json", "client/public/stats.json", "client/src/data/officialJournals.ts"]) {
  const source = path.join(root, file);
  if (fs.existsSync(source)) fs.copyFileSync(source, path.join(backup, file.replaceAll("/", "_")));
}

const nextItems = [...items, ...journals];
write("items.json", nextItems);
write("client/public/items.json", nextItems);
write("client/public/stats.json", { ...stats, total_items: nextItems.length, total: nextItems.length, last_updated: "2026-08-19" });

const palette = { السعودية: "oklch(0.48 0.12 68)", العراق: "oklch(0.55 0.12 155)", سوريا: "oklch(0.58 0.12 250)", لبنان: "oklch(0.67 0.13 35)", الأردن: "oklch(0.55 0.12 75)", مصر: "oklch(0.60 0.13 28)", الإمارات: "oklch(0.52 0.13 165)", الكويت: "oklch(0.60 0.14 215)", البحرين: "oklch(0.57 0.15 15)", قطر: "oklch(0.54 0.16 355)", "سلطنة عمان": "oklch(0.61 0.13 50)", المغرب: "oklch(0.53 0.14 25)", الجزائر: "oklch(0.54 0.13 140)", تونس: "oklch(0.57 0.14 20)", ليبيا: "oklch(0.60 0.12 210)", السودان: "oklch(0.50 0.12 42)", موريتانيا: "oklch(0.52 0.11 70)", اليمن: "oklch(0.48 0.11 32)", فلسطين: "oklch(0.46 0.12 150)", دولية: "oklch(0.53 0.12 260)" };
const official = nextItems
  .filter((item) => String(item.id).startsWith("journal_link_"))
  .sort((a, b) => String(a.country || "").localeCompare(String(b.country || ""), "ar") || String(a.title).localeCompare(String(b.title), "ar"))
  .map((journal) => ({ name: journal.title, country: journal.country || "غير محدد", description: `${journal.country || "غير محدد"} · ${journal.publisher || "رابط رسمي"}`, countLabel: "رابط رسمي", color: palette[journal.country] || "oklch(0.48 0.12 68)", officialLink: journal.link_direct }));
const moduleCode = `/* بيانات روابط المجلات الرسمية؛ تصميم المكنز الأخضر مع فلتر بلد الإصدار. */\nexport type OfficialJournal = { name: string; country: string; description: string; countLabel: string; color: string; officialLink: string }\n\nexport const OFFICIAL_JOURNALS: OfficialJournal[] = ${JSON.stringify(official, null, 2)}\n`;
fs.writeFileSync(path.join(root, "client/src/data/officialJournals.ts"), moduleCode);

const hookPath = path.join(root, "client/src/hooks/useItems.ts");
const hook = fs.readFileSync(hookPath, "utf8");
fs.writeFileSync(hookPath, hook.replace(/items\.json\?v=[^'"`\s)]+/, "items.json?v=official-journals-qblesg-2026-08-19").replace(/stats\.json\?v=[^'"`\s)]+/, "stats.json?v=official-journals-qblesg-2026-08-19"));

const report = { added_count: journals.length, total_before: items.length, total_after: nextItems.length, total_official_journal_links: official.length, by_country: Object.fromEntries([...new Set(journals.map((journal) => journal.country))].map((country) => [country, journals.filter((journal) => journal.country === country).length])), backup };
write("official_journals_qblesg_report.json", report);
console.log(JSON.stringify(report, null, 2));
