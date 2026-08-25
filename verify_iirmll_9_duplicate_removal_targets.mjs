import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const itemsRaw = load('items.json');
const items = Array.isArray(itemsRaw) ? itemsRaw : itemsRaw.items;
const manifest = load('iirmll_9_duplicate_removal_manifest.json');
const byId = new Map(items.map((item) => [item.id, item]));
const inspect = (id) => {
  const item = byId.get(id);
  if (!item) return { id, exists: false };
  const matchesSource = item.source === manifest.source && String(item.link_telegram ?? '').includes(manifest.required_telegram_fragment);
  return { id, exists: true, title: item.title, source: item.source, link_telegram: item.link_telegram ?? '', matches_source: matchesSource };
};
const removals = manifest.removal_ids.map(inspect);
const protectedRows = manifest.protected_ids.map(inspect);
const iirmllCount = items.filter((item) => item.source === manifest.source && String(item.link_telegram ?? '').includes(manifest.required_telegram_fragment)).length;
const output = {
  generated_at: new Date().toISOString(),
  total_items: items.length,
  iirmll_count: iirmllCount,
  removals,
  protected: protectedRows,
  missing_removal_ids: removals.filter((row) => !row.exists).map((row) => row.id),
  wrong_source_removal_ids: removals.filter((row) => row.exists && !row.matches_source).map((row) => row.id),
  missing_protected_ids: protectedRows.filter((row) => !row.exists).map((row) => row.id),
  wrong_source_protected_ids: protectedRows.filter((row) => row.exists && !row.matches_source).map((row) => row.id),
};
writeFileSync(path.join(root, 'iirmll_9_duplicate_removal_precheck.json'), `${JSON.stringify(output, null, 2)}\n`);
console.log(JSON.stringify({ total_items: output.total_items, iirmll_count: output.iirmll_count, required: removals.length, missing_removal_ids: output.missing_removal_ids, wrong_source_removal_ids: output.wrong_source_removal_ids, missing_protected_ids: output.missing_protected_ids, wrong_source_protected_ids: output.wrong_source_protected_ids }, null, 2));
if (output.total_items !== manifest.expected.total_before || output.iirmll_count !== manifest.expected.source_before || output.missing_removal_ids.length || output.wrong_source_removal_ids.length || output.missing_protected_ids.length || output.wrong_source_protected_ids.length) process.exit(1);
