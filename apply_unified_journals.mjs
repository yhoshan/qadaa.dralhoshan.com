import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => JSON.parse(fs.readFileSync(path.join(root, file), "utf8"));
const write = (file, value) => fs.writeFileSync(path.join(root, file), JSON.stringify(value, null, 2));
const strip = (value) => String(value ?? "").replace(/\s+/g, " ").trim();

const input = read("official_journals_unified_preview.json");
const journals = input.journals;
const items = read("items.json");
const publicItems = read("client/public/items.json");
const stats = read("client/public/stats.json");

if (items.length !== publicItems.length) {
  throw new Error(`تعارض بين نسخة البيانات الخاصة والعامة: ${items.length} مقابل ${publicItems.length}`);
}

const existingIds = new Set(items.map((item) => String(item.id)));
const existingLinks = new Set(items.map((item) => strip(item.link_direct)).filter(Boolean));
const duplicateIds = journals.filter((journal) => existingIds.has(journal.id));
const duplicateLinks = journals.filter((journal) => existingLinks.has(strip(journal.link_direct)));
if (duplicateIds.length || duplicateLinks.length) {
  throw new Error(JSON.stringify({ duplicate_ids: duplicateIds.map((item) => item.title), duplicate_links: duplicateLinks.map((item) => item.title) }));
}

const stamp = new Date().toISOString().replace(/[:.]/g, "-").replace("T", "_").replace("Z", "");
const backup = path.join(root, "backups", `official-journals-unified-${stamp}`);
fs.mkdirSync(backup, { recursive: true });
for (const file of ["items.json", "client/public/items.json", "client/public/stats.json", "client/src/data/officialJournals.ts"]) {
  const source = path.join(root, file);
  if (fs.existsSync(source)) fs.copyFileSync(source, path.join(backup, file.replaceAll("/", "_")));
}

const nextItems = [...items, ...journals];
const nextStats = {
  ...stats,
  total_items: nextItems.length,
  total: nextItems.length,
  last_updated: "2026-08-19",
};

write("items.json", nextItems);
write("client/public/items.json", nextItems);
write("client/public/stats.json", nextStats);

const palette = {
  "السعودية": "oklch(0.48 0.12 68)",
  "العراق": "oklch(0.55 0.12 155)",
  "سوريا": "oklch(0.58 0.12 250)",
  "لبنان": "oklch(0.67 0.13 35)",
  "الأردن": "oklch(0.55 0.12 75)",
  "مصر": "oklch(0.60 0.13 28)",
  "الإمارات": "oklch(0.52 0.13 165)",
  "الكويت": "oklch(0.60 0.14 215)",
  "البحرين": "oklch(0.57 0.15 15)",
  "قطر": "oklch(0.54 0.16 355)",
  "سلطنة عمان": "oklch(0.61 0.13 50)",
  "المغرب": "oklch(0.53 0.14 25)",
  "الجزائر": "oklch(0.54 0.13 140)",
  "تونس": "oklch(0.57 0.14 20)",
  "ليبيا": "oklch(0.60 0.12 210)",
  "السودان": "oklch(0.50 0.12 42)",
  "موريتانيا": "oklch(0.52 0.11 70)",
  "اليمن": "oklch(0.48 0.11 32)",
  "فلسطين": "oklch(0.46 0.12 150)",
  "دولية": "oklch(0.53 0.12 260)",
};

const allOfficialJournals = nextItems
  .filter((item) => String(item.id).startsWith("journal_link_"))
  .sort((a, b) => String(a.country || "").localeCompare(String(b.country || ""), "ar") || String(a.title).localeCompare(String(b.title), "ar"))
  .map((journal) => ({
    name: journal.title,
    country: journal.country || "غير محدد",
    description: `${journal.country || "غير محدد"} · ${journal.publisher || "رابط رسمي"}`,
    countLabel: "رابط رسمي",
    color: palette[journal.country] || "oklch(0.48 0.12 68)",
    officialLink: journal.link_direct,
  }));

const dataModule = `/* بيانات روابط المجلات الرسمية؛ تصميم المكنز الأخضر مع فلاتر محلية حسب بلد الإصدار. */\nexport type OfficialJournal = { name: string; country: string; description: string; countLabel: string; color: string; officialLink: string }\n\nexport const OFFICIAL_JOURNALS: OfficialJournal[] = ${JSON.stringify(allOfficialJournals, null, 2)}\n`;
fs.mkdirSync(path.join(root, "client/src/data"), { recursive: true });
fs.writeFileSync(path.join(root, "client/src/data/officialJournals.ts"), dataModule);

const hookPath = path.join(root, "client/src/hooks/useItems.ts");
const hook = fs.readFileSync(hookPath, "utf8");
fs.writeFileSync(
  hookPath,
  hook
    .replace(/items\.json\?v=[^'"`\s)]+/, "items.json?v=official-journals-unified-2026-08-19")
    .replace(/stats\.json\?v=[^'"`\s)]+/, "stats.json?v=official-journals-unified-2026-08-19")
);

const report = {
  added_count: journals.length,
  total_before: items.length,
  total_after: nextItems.length,
  total_official_journal_links: allOfficialJournals.length,
  by_country: Object.fromEntries([...new Set(journals.map((journal) => journal.country))].sort((a, b) => a.localeCompare(b, "ar")).map((country) => [country, journals.filter((journal) => journal.country === country).length])),
  exclusions: input.report.skipped_counts,
  backup,
};
write("official_journals_unified_report.json", report);
console.log(JSON.stringify(report, null, 2));
