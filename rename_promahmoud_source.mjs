import fs from 'node:fs/promises';

const root = process.cwd();
const oldSource = 'مكتبة الدكتور محمود لطفي عبد العزيز القانونية';
const newSource = 'موقع الأستاذ محمود';
const paths = [
  `${root}/items.json`,
  `${root}/client/public/items.json`,
];

let updated = 0;
for (const path of paths) {
  const raw = JSON.parse(await fs.readFile(path, 'utf8'));
  const items = Array.isArray(raw) ? raw : raw.items;
  for (const item of items) {
    if (item.id?.startsWith('promahmoud_') && item.source === oldSource) {
      item.source = newSource;
      updated += 1;
    }
  }
  await fs.writeFile(path, JSON.stringify(Array.isArray(raw) ? items : { ...raw, items }, null, 2));
}

const mainRaw = JSON.parse(await fs.readFile(`${root}/items.json`, 'utf8'));
const items = Array.isArray(mainRaw) ? mainRaw : mainRaw.items;
const countBy = field => Object.fromEntries([...items.reduce((map, item) => {
  const value = String(item[field] ?? '');
  map.set(value, (map.get(value) ?? 0) + 1);
  return map;
}, new Map()).entries()].sort((a, b) => b[1] - a[1]));
const stats = {
  total_items: items.length,
  categories: countBy('category'),
  sources: countBy('source'),
  material_types: countBy('material_type'),
  file_types: countBy('file_type'),
  featured_count: items.filter(item => item.is_featured).length,
  with_download_links: items.filter(item => Number(item.download_links_count ?? 0) > 0).length,
};
await fs.writeFile(`${root}/stats.json`, JSON.stringify(stats, null, 2));
await fs.writeFile(`${root}/client/public/stats.json`, JSON.stringify(stats, null, 2));
let hook = await fs.readFile(`${root}/client/src/hooks/useItems.ts`, 'utf8');
hook = hook.replace(/(\/items\.json\?v=)[^'"`\s)]+/g, '$1promahmoud-source-reference-2026-09-06');
hook = hook.replace(/(\/stats\.json\?v=)[^'"`\s)]+/g, '$1promahmoud-source-reference-2026-09-06');
await fs.writeFile(`${root}/client/src/hooks/useItems.ts`, hook);
const summary = { old_source: oldSource, new_source: newSource, records_updated_across_copies: updated, source_count: stats.sources[newSource] ?? 0, total_items: items.length };
await fs.writeFile(`${root}/promahmoud_source_rename_execution.json`, JSON.stringify(summary, null, 2));
console.log(JSON.stringify(summary));
