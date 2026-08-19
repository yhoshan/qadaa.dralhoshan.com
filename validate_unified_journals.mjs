import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (file) => JSON.parse(fs.readFileSync(path.join(root, file), "utf8"));
const items = read("items.json");
const publicItems = read("client/public/items.json");
const stats = read("client/public/stats.json");
const importReport = read("official_journals_unified_report.json");
const official = items.filter((item) => String(item.id).startsWith("journal_link_"));
const links = official.map((item) => item.link_direct);
const importedThisBatch = items.slice(-importReport.added_count);
const countries = [...new Set(official.map((item) => item.country).filter(Boolean))];
const dataModule = fs.readFileSync(path.join(root, "client/src/data/officialJournals.ts"), "utf8");
const hook = fs.readFileSync(path.join(root, "client/src/hooks/useItems.ts"), "utf8");

const checks = {
  public_private_item_count_match: items.length === publicItems.length,
  stats_total_matches_items: stats.total_items === items.length && stats.total === items.length,
  all_official_links_are_web_urls: links.every((link) => /^https?:\/\//.test(link)),
  all_newly_imported_links_are_https: importedThisBatch.every((item) => /^https:\/\//.test(item.link_direct)),
  official_links_are_unique: new Set(links).size === links.length,
  all_official_journals_have_country: official.every((item) => Boolean(item.country)),
  generated_cards_match_official_count: (dataModule.match(/officialLink/g) || []).length === official.length + 1,
  cache_busting_updated: hook.includes("official-journals-unified-2026-08-19"),
};

if (!Object.values(checks).every(Boolean)) {
  throw new Error(JSON.stringify({ checks, item_count: items.length, official_count: official.length, country_count: countries.length }, null, 2));
}

console.log(JSON.stringify({
  checks,
  item_count: items.length,
  official_journal_count: official.length,
  country_count: countries.length,
  countries,
}, null, 2));
