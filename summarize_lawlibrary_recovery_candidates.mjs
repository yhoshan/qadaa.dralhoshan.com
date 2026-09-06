import { readFile, writeFile } from 'node:fs/promises';

const root = process.cwd();
const data = JSON.parse(await readFile(`${root}/lawlibrary_recovery_candidates.json`, 'utf8'));
const grouped = new Map();
for (const row of data.candidates) {
  const key = `${row.recovery_group} | ${row.source || 'غير محدد'} | ${row.publisher || 'غير محدد'}`;
  const current = grouped.get(key) || { recovery_group: row.recovery_group, origin_source: row.source || 'غير محدد', publisher: row.publisher || 'غير محدد', count: 0, samples: [] };
  current.count += 1;
  if (current.samples.length < 4) current.samples.push({ id: row.id, title: row.title, url: row.link_direct });
  grouped.set(key, current);
}
const rows = [...grouped.values()].sort((a, b) => a.recovery_group.localeCompare(b.recovery_group, 'ar') || b.count - a.count || a.origin_source.localeCompare(b.origin_source, 'ar'));
await writeFile(`${root}/lawlibrary_recovery_candidate_source_summary.json`, `${JSON.stringify(rows, null, 2)}\n`);
await writeFile(`${root}/lawlibrary_recovery_candidate_source_summary.txt`, rows.map((row) => [
  `${row.recovery_group} | ${row.origin_source} | ${row.publisher}: ${row.count}`,
  ...row.samples.map((sample) => `  - ${sample.id} | ${sample.title}`),
].join('\n')).join('\n\n'));
console.log(JSON.stringify(rows.map((row) => ({ group: row.recovery_group, source: row.origin_source, publisher: row.publisher, count: row.count })), null, 2));
