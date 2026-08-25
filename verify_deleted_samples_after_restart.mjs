import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const items = JSON.parse(readFileSync(path.join(root, 'items.json'), 'utf8'));
const published = JSON.parse(readFileSync(path.join(root, 'client/public/items.json'), 'utf8'));
const unwrap = (value) => Array.isArray(value) ? value : value.items ?? [];
const mainItems = unwrap(items);
const publicItems = unwrap(published);
const samples = {
  great_law: ['great_law_1888', 'great_law_4949', 'great_law_4952', 'great_law_5091', 'great_law_16770'],
  academic_theses: ['risail_25652', 'risail_35582', 'risail_25519', 'risail_25951', 'risail_59962'],
  alexandria: ['alexandria_cbz_9566', 'alexandria_cbz_30657', 'alexandria_cbz_64598', 'alexandria_cbz_24605', 'alexandria_cbz_63753'],
  sanaa_block: ['legal_mag_196', 'legal_mag_201', 'legal_mag_202', 'legal_mag_203', 'legal_mag_204'],
};
const mainIds = new Set(mainItems.map((item) => item.id));
const publicIds = new Set(publicItems.map((item) => item.id));
const results = Object.fromEntries(Object.entries(samples).map(([group, ids]) => [group, ids.map((id) => ({ id, absent_main: !mainIds.has(id), absent_published: !publicIds.has(id) }))]));
const allAbsent = Object.values(results).flat().every((row) => row.absent_main && row.absent_published);
const output = { generated_at: new Date().toISOString(), samples, results, all_absent: allAbsent };
writeFileSync(path.join(root, 'deleted_samples_post_restart_verification.json'), `${JSON.stringify(output, null, 2)}\n`);
console.log(JSON.stringify({ groups: Object.fromEntries(Object.entries(results).map(([group, rows]) => [group, rows.every((row) => row.absent_main && row.absent_published)])), all_absent: allAbsent }, null, 2));
if (!allAbsent) process.exit(1);
