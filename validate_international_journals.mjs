import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => JSON.parse(fs.readFileSync(path.join(root, file), "utf8"));
const items = read("items.json");
const publicItems = read("client/public/items.json");
const stats = read("client/public/stats.json");
const report = read("international_journals_report.json");
const batch = items.filter((item) => ["ملف المجلات الدولية lPep79", "ملف المجلات الدولية Ypr81X"].includes(item.import_origin));
const official = items.filter((item) => String(item.id).startsWith("journal_link_"));
const section = fs.readFileSync(path.join(root, "client/src/components/JournalsSection.tsx"), "utf8");
const countries = Array.from(new Set(official.map((item) => item.country))).sort((a, b) => {
  if (a === "السعودية") return -1;
  if (b === "السعودية") return 1;
  if (a === "دولية") return 1;
  if (b === "دولية") return -1;
  return a.localeCompare(b, "ar");
});

const checks = {
  public_private_data_match: items.length === publicItems.length,
  stats_match_item_count: stats.total_items === items.length && stats.total === items.length,
  accepted_batch_count_is_fifteen: batch.length === 15 && report.added_count === 15,
  accepted_batch_has_web_links: batch.every((item) => /^https?:\/\//.test(item.link_direct)),
  accepted_batch_has_unique_links: new Set(batch.map((item) => item.link_direct)).size === batch.length,
  official_journal_links_are_unique: new Set(official.map((item) => item.link_direct)).size === official.length,
  international_dropdown_label_exists: section.includes("المجلات الدولية باللغة الإنجليزية"),
  international_dropdown_filters_dawlia: section.includes('value={country}') && section.includes('country === "دولية"'),
  dropdown_order_is_saudi_first_and_international_last: countries[0] === "السعودية" && countries.at(-1) === "دولية",
};

if (!Object.values(checks).every(Boolean)) throw new Error(JSON.stringify({ checks, total_items: items.length, official_count: official.length }, null, 2));
console.log(JSON.stringify({ checks, total_items: items.length, official_count: official.length, international_journal_count: official.filter((item) => item.country === "دولية").length, dropdown_options: ["الكل", ...countries.map((country) => country === "دولية" ? "المجلات الدولية باللغة الإنجليزية" : country)] }, null, 2));
