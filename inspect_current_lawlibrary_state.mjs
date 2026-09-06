import { readFile, writeFile } from 'node:fs/promises';

const root = process.cwd();
const unwrap = (raw) => Array.isArray(raw) ? raw : raw.items;
const items = unwrap(JSON.parse(await readFile(`${root}/items.json`, 'utf8')));
const lawlibrary = items.filter((item) => item.source === 'مكتبة القانون');
const byId = lawlibrary.reduce((map, item) => { map[item.id] = { title: item.title, link_direct: item.link_direct, category: item.category, material_type: item.material_type }; return map; }, {});
const ranges = Object.keys(byId).filter((id) => /^lawlibrary_\d+$/.test(id)).map((id) => Number(id.split('_')[1])).sort((a, b) => a - b);
const stats = JSON.parse(await readFile(`${root}/stats.json`, 'utf8'));
const result = {
  total_items: items.length,
  lawlibrary_count: lawlibrary.length,
  lawlibrary_numeric_id_min: ranges[0] ?? null,
  lawlibrary_numeric_id_max: ranges.at(-1) ?? null,
  lawlibrary_numeric_ids: ranges.length,
  lawlibrary_tail: lawlibrary.slice(-12).map((item) => ({ id: item.id, title: item.title, category: item.category, link_direct: item.link_direct })),
  stats_lawlibrary: stats.sourceCounts?.['مكتبة القانون'] ?? null,
};
await writeFile(`${root}/lawlibrary_current_state_after_reset.json`, `${JSON.stringify(result, null, 2)}\n`);
console.log(JSON.stringify(result, null, 2));
