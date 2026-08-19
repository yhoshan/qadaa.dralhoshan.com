import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => JSON.parse(fs.readFileSync(path.join(root, file), "utf8"));
const items = read("items.json");
const publicItems = read("client/public/items.json");
const stats = read("client/public/stats.json");
const report = read("official_journals_qblesg_report.json");
const batch = items.filter((item) => item.import_origin === "ملف المجلات الجديد qBLeSG");
const official = items.filter((item) => String(item.id).startsWith("journal_link_"));
const section = fs.readFileSync(path.join(root, "client/src/components/JournalsSection.tsx"), "utf8");
const dropdownCountries = Array.from(new Set(official.map((item) => item.country))).sort((a, b) => {
  if (a === "السعودية") return -1;
  if (b === "السعودية") return 1;
  return a.localeCompare(b, "ar");
});

const checks = {
  public_private_data_match: items.length === publicItems.length,
  stats_match_item_count: stats.total_items === items.length && stats.total === items.length,
  approved_batch_count_is_nine: batch.length === 9 && report.added_count === 9,
  approved_batch_links_are_https: batch.every((item) => /^https:\/\//.test(item.link_direct)),
  approved_batch_has_no_duplicate_links: new Set(batch.map((item) => item.link_direct)).size === batch.length,
  official_journal_links_are_unique: new Set(official.map((item) => item.link_direct)).size === official.length,
  total_official_journal_links_match_report: official.length === report.total_official_journal_links,
  dropdown_sorts_saudi_first: section.includes('if (a === "السعودية") return -1;'),
  dropdown_has_all_option: section.includes('<option value="all">الكل</option>'),
  dropdown_countries_exist_in_data: dropdownCountries.every(Boolean),
  dropdown_country_order_is_saudi_then_alphabetical: dropdownCountries[0] === "السعودية" && dropdownCountries.slice(1).every((country, index, array) => index === 0 || array[index - 1].localeCompare(country, "ar") <= 0),
};

if (!Object.values(checks).every(Boolean)) throw new Error(JSON.stringify({ checks, total_items: items.length, official_count: official.length }, null, 2));
console.log(JSON.stringify({ checks, total_items: items.length, official_count: official.length, countries_added: [...new Set(batch.map((item) => item.country))], dropdown_options: ["الكل", ...dropdownCountries] }, null, 2));
