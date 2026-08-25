import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const requestedText = readFileSync('/home/ubuntu/upload/pasted_content_3.txt', 'utf8');
const targetIds = [...new Set(requestedText.match(/alexandria_cbz_\d+/g) ?? [])];
const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const unwrap = (data) => Array.isArray(data) ? data : data.items ?? [];
const main = unwrap(load('items.json'));
const published = unwrap(load('client/public/items.json'));
const stats = load('stats.json');
const publicStats = load('client/public/stats.json');
const execution = load('alexandria_184_removal_execution_report.json');
const duplicateIds = (items) => [...new Set(items.map((item) => item.id).filter((id, index, ids) => ids.indexOf(id) !== index))];
const missingBasicFields = main.filter((item) => !item.id || !item.title || !item.source || !item.category).map((item) => item.id);
const remainingTargetsMain = main.filter((item) => targetIds.includes(item.id)).map((item) => item.id);
const remainingTargetsPublic = published.filter((item) => targetIds.includes(item.id)).map((item) => item.id);
const mainAndPublicMatch = JSON.stringify(main) === JSON.stringify(published);
const report = {
  generated_at: new Date().toISOString(),
  final_count_main: main.length,
  final_count_published: published.length,
  expected_final_count: execution.final_count,
  stats_total: stats.total_items,
  public_stats_total: publicStats.total_items,
  requested_count: targetIds.length,
  removed_count: execution.removed_count,
  remaining_target_ids_main: remainingTargetsMain,
  remaining_target_ids_published: remainingTargetsPublic,
  duplicate_ids_main: duplicateIds(main),
  duplicate_ids_published: duplicateIds(published),
  records_missing_basic_fields: missingBasicFields,
  main_and_published_match: mainAndPublicMatch,
  count_equation_valid: execution.before_count - execution.removed_count === main.length,
  non_target_records_preserved_by_count: execution.non_target_records_preserved_by_count,
};
report.safe = report.final_count_main === report.expected_final_count
  && report.final_count_published === report.expected_final_count
  && report.stats_total === report.expected_final_count
  && report.public_stats_total === report.expected_final_count
  && report.remaining_target_ids_main.length === 0
  && report.remaining_target_ids_published.length === 0
  && report.duplicate_ids_main.length === 0
  && report.duplicate_ids_published.length === 0
  && report.records_missing_basic_fields.length === 0
  && report.main_and_published_match
  && report.count_equation_valid
  && report.non_target_records_preserved_by_count;
writeFileSync(path.join(root, 'alexandria_184_removal_validation.json'), `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ safe: report.safe, final_count: report.final_count_main, remaining_targets: report.remaining_target_ids_main.length, duplicate_ids: report.duplicate_ids_main.length, missing_basic_fields: report.records_missing_basic_fields.length }, null, 2));
if (!report.safe) process.exit(1);
