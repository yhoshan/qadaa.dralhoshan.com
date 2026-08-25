import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const files = ['items.json', 'client/public/items.json', 'stats.json', 'client/public/stats.json'];
const sha256 = (file) => createHash('sha256').update(readFileSync(path.join(root, file))).digest('hex');
const baseline = JSON.parse(readFileSync(path.join(root, 'stable_state_pre_restart_verification.json'), 'utf8'));
const current = Object.fromEntries(files.map((file) => [file, JSON.parse(readFileSync(path.join(root, file), 'utf8'))]));
const unwrap = (value) => Array.isArray(value) ? value : value.items ?? [];
const items = unwrap(current['items.json']);
const publicItems = unwrap(current['client/public/items.json']);
const sourceCount = items.filter((item) => item.source === 'قناة الرسائل العلمية').length;
const hashes = Object.fromEntries(files.map((file) => [file, sha256(file)]));
const hashMatches = Object.fromEntries(files.map((file) => [file, hashes[file] === baseline.files[file].sha256]));
const output = {
  generated_at: new Date().toISOString(),
  total_items: items.length,
  public_total_items: publicItems.length,
  source_count_academic_theses: sourceCount,
  stats_total: current['stats.json'].total_items,
  public_stats_total: current['client/public/stats.json'].total_items,
  hashes_before: Object.fromEntries(files.map((file) => [file, baseline.files[file].sha256])),
  hashes_after: hashes,
  hash_matches: hashMatches,
  branch_head: null,
};
output.passed = output.total_items === 11295 && output.public_total_items === 11295 && output.source_count_academic_theses === 430 && output.stats_total === 11295 && output.public_stats_total === 11295 && Object.values(hashMatches).every(Boolean);
writeFileSync(path.join(root, 'stable_state_post_restart_verification.json'), `${JSON.stringify(output, null, 2)}\n`);
console.log(JSON.stringify({ total: output.total_items, academic_theses: output.source_count_academic_theses, hashes_match: Object.values(hashMatches).every(Boolean), details: hashMatches, passed: output.passed }, null, 2));
if (!output.passed) process.exit(1);
