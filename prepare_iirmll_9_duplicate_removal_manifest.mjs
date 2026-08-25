import { writeFileSync } from 'node:fs';
import path from 'node:path';

const removalIds = [
  'legal_lib_12307', 'legal_lib_12308', 'legal_lib_12492', 'legal_lib_12332', 'legal_lib_12312',
  'legal_lib_13449', 'legal_lib_12800', 'legal_lib_12633', 'legal_lib_13435',
];
const protectedIds = [
  'legal_lib_11384', 'legal_lib_11532', 'legal_lib_11661', 'legal_lib_11997', 'legal_lib_12259',
  'legal_lib_12630', 'legal_lib_13324', 'legal_lib_12629',
];
const manifest = {
  generated_at: new Date().toISOString(),
  source: 'المكتبة القانونية ⚖️',
  required_telegram_fragment: 't.me/iirmll/',
  removal_ids: removalIds,
  protected_ids: protectedIds,
  expected: { total_before: 11295, remove_count: 9, total_after: 11286, source_before: 510, source_after: 501 },
};
writeFileSync(path.join(process.cwd(), 'iirmll_9_duplicate_removal_manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`);
console.log(JSON.stringify({ removal_ids: removalIds.length, protected_ids: protectedIds.length, expected: manifest.expected }, null, 2));
