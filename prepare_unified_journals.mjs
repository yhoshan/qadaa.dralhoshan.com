import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => JSON.parse(fs.readFileSync(path.isAbsolute(file) ? file : path.join(root, file), "utf8"));
const write = (file, value) => fs.writeFileSync(path.join(root, file), JSON.stringify(value, null, 2));

const stripRefs = (value) => String(value ?? "")
  .replace(/\[reference:\d+\]/g, "")
  .replace(/\s+/g, " ")
  .trim();

const normalizeText = (value) => stripRefs(value)
  .replace(/\([^)]*\)/g, " ")
  .replace(/[أإآ]/g, "ا")
  .replace(/ة/g, "ه")
  .replace(/ى/g, "ي")
  .replace(/[^\p{L}\p{N}]+/gu, "")
  .toLowerCase();

const normalizeCountry = (value) => stripRefs(value).replaceAll("_", " ").replace("سلطنة عُمان", "سلطنة عمان");

const blockedHosts = new Set([
  "facebook.com",
  "www.facebook.com",
  "t.me",
  "telegram.me",
  "search.emarefa.net",
  "mohamah.net",
  "www.mohamah.net",
]);

const knownCuratedJournalKeys = new Set([
  "السعودية|مجلهالعدل",
  "السعودية|مجلهقضاء",
]);

const tunisianCodes = new Set([
  "مجلهالالتزاماتوالعقود",
  "مجلهالاحوالالشخصيه",
  "المجلهالتجاريه",
  "مجلهالشركاتالتجاريه",
  "مجلهالمرافعاتالمدنيوالتجاريه",
  "المجلهالجزائيه",
]);

function officialUrl(raw) {
  let value = stripRefs(raw);
  if (!value || /^(?:-|غير محدد|غير متوفر|غير متوفر حالياً)$/u.test(value)) return null;
  value = value.split(" ")[0].replace(/[،؛,.]+$/u, "");
  if (!/^https?:\/\//i.test(value)) value = `https://${value}`;
  try {
    const url = new URL(value);
    if (!url.hostname.includes(".") || blockedHosts.has(url.hostname.toLowerCase())) return null;
    url.hash = "";
    return url.href.replace(/\/$/, "");
  } catch {
    return null;
  }
}

function makeItem({ country, journal, origin }) {
  const title = stripRefs(journal["الاسم"]);
  const publisher = stripRefs(journal["الناشر"]);
  const link = officialUrl(journal["الرابط"]);
  if (!title || title.startsWith("لا توجد مجلات") || !link) return null;
  const identity = `${normalizeCountry(country)}|${normalizeText(title)}|${normalizeText(publisher)}`;
  const id = `journal_link_${crypto.createHash("sha1").update(`${identity}|${link}`).digest("hex").slice(0, 16)}`;
  return {
    id,
    title,
    author: "",
    investigator: "",
    publisher,
    year: stripRefs(journal["سنة_التأسيس"]),
    link_telegram: "",
    link_drive: "",
    link_direct: link,
    source: `فهرس المجلات المتخصصة — ${country}`,
    category: "المجلات القانونية",
    material_type: "مجلة",
    file_type: "رابط",
    file_size: "",
    pages_count: "",
    is_featured: false,
    download_links_count: 1,
    country,
    issn: stripRefs(journal["ISSN"]),
    frequency: stripRefs(journal["التردد"]),
    notes: stripRefs(journal["ملاحظات"]),
    import_origin: origin,
  };
}

function isPeriodical(item) {
  return !(item.country === "تونس" && tunisianCodes.has(normalizeText(item.title)));
}

const main = read("/home/ubuntu/upload/pasted_file_c3D7gq_deepseek_json_20260819_413a3e.json");
const supplementA = read("/home/ubuntu/upload/pasted_file_WLLPOi_deepseek_json_20260819_a9fdcf.json");
const supplementB = read("/home/ubuntu/upload/pasted_file_88TUTf_deepseek_json_20260819_ad46ef.json");
const existingItems = read("items.json");

const raw = [];
const mainJournals = main["المجلات_القانونية"];
for (const [country, records] of Object.entries(mainJournals["الدول_العربية"] || {})) {
  for (const journal of records) raw.push({ country: normalizeCountry(country), journal, origin: "الفهرس الموحّد — الدول العربية" });
}
for (const records of Object.values(mainJournals["المجلات_الدولية_باللغة_الإنجليزية"] || {})) {
  for (const journal of records) raw.push({ country: "دولية", journal, origin: "الفهرس الموحّد — مجلات دولية باللغة الإنجليزية" });
}
for (const [country, records] of Object.entries(supplementA["المجلات_والنشرات_القانونية_المضافة"] || {})) {
  for (const journal of records) raw.push({ country: normalizeCountry(country), journal, origin: "الملف الإضافي الأول" });
}
for (const [country, records] of Object.entries(supplementB["المجلات_والنشرات_القانونية_الجديدة"] || {})) {
  for (const journal of records) raw.push({ country: normalizeCountry(country), journal, origin: "الملف الإضافي الثاني" });
}

const existingJournalKeys = new Set(
  existingItems
    .filter((item) => String(item.id).startsWith("journal_link_"))
    .map((item) => `${normalizeCountry(item.country || item.source?.replace("فهرس المجلات المتخصصة — ", "") || "")}|${normalizeText(item.title)}`)
);
const existingJournalLinks = new Set(
  existingItems
    .map((item) => officialUrl(item.link_direct))
    .filter(Boolean)
);

const candidates = [];
const seenKeys = new Set();
const seenLinks = new Set();
const skipped = { invalid_or_nonofficial_link: [], not_a_periodical: [], already_imported: [], duplicate_within_inputs: [] };

for (const source of raw) {
  const item = makeItem(source);
  if (!item) {
    skipped.invalid_or_nonofficial_link.push({ country: source.country, title: stripRefs(source.journal["الاسم"]), link: stripRefs(source.journal["الرابط"]), origin: source.origin });
    continue;
  }
  const key = `${normalizeCountry(item.country)}|${normalizeText(item.title)}`;
  if (!isPeriodical(item)) {
    skipped.not_a_periodical.push({ country: item.country, title: item.title, link: item.link_direct, origin: item.import_origin });
    continue;
  }
  if (knownCuratedJournalKeys.has(key) || existingJournalKeys.has(key) || existingJournalLinks.has(item.link_direct)) {
    skipped.already_imported.push({ country: item.country, title: item.title, link: item.link_direct, origin: item.import_origin });
    continue;
  }
  if (seenKeys.has(key) || seenLinks.has(item.link_direct)) {
    skipped.duplicate_within_inputs.push({ country: item.country, title: item.title, link: item.link_direct, origin: item.import_origin });
    continue;
  }
  seenKeys.add(key);
  seenLinks.add(item.link_direct);
  candidates.push(item);
}

const candidateDuplicateLinks = [...new Set(candidates.map((item) => item.link_direct))]
  .map((link) => ({ link, titles: candidates.filter((item) => item.link_direct === link).map((item) => `${item.country} — ${item.title}`) }))
  .filter((entry) => entry.titles.length > 1);

const report = {
  total_raw_records: raw.length,
  accepted_candidates: candidates.length,
  by_country: Object.fromEntries([...new Set(candidates.map((item) => item.country))].sort((a, b) => a.localeCompare(b, "ar")).map((country) => [country, candidates.filter((item) => item.country === country).length])),
  skipped_counts: Object.fromEntries(Object.entries(skipped).map(([key, values]) => [key, values.length])),
  candidate_duplicate_links: candidateDuplicateLinks,
  skipped,
};

write("official_journals_unified_preview.json", { journals: candidates, report });
console.log(JSON.stringify(report, null, 2));
