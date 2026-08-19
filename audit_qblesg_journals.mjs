import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => JSON.parse(fs.readFileSync(path.isAbsolute(file) ? file : path.join(root, file), "utf8"));
const write = (file, value) => fs.writeFileSync(path.join(root, file), JSON.stringify(value, null, 2));
const stripRefs = (value) => String(value ?? "").replace(/\[reference:\d+\]/g, "").replace(/\s+/g, " ").trim();
const normal = (value) => stripRefs(value)
  .replace(/\([^)]*\)/g, " ")
  .replace(/[أإآ]/g, "ا")
  .replace(/ة/g, "ه")
  .replace(/ى/g, "ي")
  .replace(/[^\p{L}\p{N}]+/gu, "")
  .toLowerCase();
const country = (value) => stripRefs(value).replaceAll("_", " ").replace("سلطنة عُمان", "سلطنة عمان");
const urlOf = (value) => {
  let link = stripRefs(value);
  if (!/^https?:\/\//i.test(link)) return null;
  try {
    const url = new URL(link);
    url.hash = "";
    return url.href.replace(/\/$/, "");
  } catch {
    return null;
  }
};

const input = read("/home/ubuntu/upload/pasted_file_qBLeSG_deepseek_json_20260819_b6802f.json");
const items = read("items.json");
const records = Object.entries(input["المجلات_والنشرات_القانونية_الجديدة_2026"] || {})
  .flatMap(([countryName, journals]) => journals.map((journal) => ({ country: country(countryName), journal })));
const existingLinks = new Set(items.map((item) => urlOf(item.link_direct)).filter(Boolean));
const existingJournalTitles = new Set(
  items
    .filter((item) => String(item.id).startsWith("journal_link_"))
    .map((item) => `${country(item.country || "")}|${normal(item.title)}`)
);

const genericOrUnverifiedHosts = new Set([
  "platform.openjournals.nl",
  "www.inlibra.com",
  "inlibra.com",
  "lynxlex.com",
  "www.lynxlex.com",
]);
const result = { candidates_for_confirmation: [], existing_duplicates: [], needs_specific_official_url: [], unavailable_or_social_only: [] };

for (const { country: countryName, journal } of records) {
  const title = stripRefs(journal["الاسم"]);
  const publisher = stripRefs(journal["الناشر"]);
  const link = urlOf(journal["الرابط"]);
  const item = { country: countryName, title, publisher, link: link || stripRefs(journal["الرابط"]), notes: stripRefs(journal["ملاحظات"]) };
  if (!link) {
    result.unavailable_or_social_only.push(item);
    continue;
  }
  const key = `${countryName}|${normal(title)}`;
  if (existingLinks.has(link) || existingJournalTitles.has(key)) {
    result.existing_duplicates.push(item);
    continue;
  }
  if (genericOrUnverifiedHosts.has(new URL(link).hostname.toLowerCase())) {
    result.needs_specific_official_url.push(item);
    continue;
  }
  result.candidates_for_confirmation.push(item);
}

const summary = Object.fromEntries(Object.entries(result).map(([key, value]) => [key, value.length]));
write("audit_qblesg_journals_report.json", { summary, ...result });
console.log(JSON.stringify({ summary, candidates: result.candidates_for_confirmation }, null, 2));
