import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const files = ['items.json', 'client/public/items.json', 'stats.json', 'client/public/stats.json'];
const sha256 = (file) => createHash('sha256').update(readFileSync(path.join(root, file))).digest('hex');
const data = Object.fromEntries(files.map((file) => [file, JSON.parse(readFileSync(path.join(root, file), 'utf8'))]));
const unwrap = (value) => Array.isArray(value) ? value : value.items ?? [];
const items = unwrap(data['items.json']);
const publicItems = unwrap(data['client/public/items.json']);
const sourceCount = items.filter((item) => item.source === 'قناة الرسائل العلمية').length;
const duplicateIds = [...new Set(items.map((item) => item.id).filter((id, index, all) => all.indexOf(id) !== index))];
const output = {
  generated_at: new Date().toISOString(),
  files: Object.fromEntries(files.map((file) => [file, { sha256: sha256(file), record_count: file.includes('items') ? unwrap(data[file]).length : data[file].total_items }])),
  total_items: items.length,
  public_total_items: publicItems.length,
  source_count_academic_theses: sourceCount,
  stats_total: data['stats.json'].total_items,
  public_stats_total: data['client/public/stats.json'].total_items,
  primary_public_ids_match: items.length === publicItems.length && new Set(items.map((item) => item.id)).size === new Set(publicItems.map((item) => item.id)).size && items.every((item) => publicItems.some((publicItem) => publicItem.id === item.id)),
  duplicate_ids: duplicateIds,
};
output.passed = output.total_items === 11295 && output.public_total_items === 11295 && output.source_count_academic_theses === 430 && output.stats_total === 11295 && output.public_stats_total === 11295 && output.primary_public_ids_match && output.duplicate_ids.length === 0;
writeFileSync(path.join(root, 'stable_state_pre_restart_verification.json'), `${JSON.stringify(output, null, 2)}\n`);
console.log(JSON.stringify({ total: output.total_items, academic_theses: output.source_count_academic_theses, stats: output.stats_total, primary_public_ids_match: output.primary_public_ids_match, duplicates: output.duplicate_ids.length, passed: output.passed }, null, 2));
if (!output.passed) process.exit(1);
