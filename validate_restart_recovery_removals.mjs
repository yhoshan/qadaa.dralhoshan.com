import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const unwrap = (data) => Array.isArray(data) ? data : data.items ?? [];
const manifest = load('restart_recovery_removal_manifest.json');
const execution = load('restart_recovery_execution_report.json');
const beforeItems = unwrap(load('backups/recovery_after_restart_2026-08-25/items_primary.json'));
const beforePublished = unwrap(load('backups/recovery_after_restart_2026-08-25/items_published.json'));
const items = unwrap(load('items.json'));
const publishedItems = unwrap(load('client/public/items.json'));
const stats = load('stats.json');
const publishedStats = load('client/public/stats.json');
const targetIds = new Set(manifest.all_target_ids);
const protectedIds = new Set(manifest.protected_ids);
const beforeIds = new Set(beforeItems.map((item) => item.id));
const beforePublishedIds = new Set(beforePublished.map((item) => item.id));
const afterIds = new Set(items.map((item) => item.id));
const afterPublishedIds = new Set(publishedItems.map((item) => item.id));
const removedMain = [...beforeIds].filter((id) => !afterIds.has(id));
const removedPublished = [...beforePublishedIds].filter((id) => !afterPublishedIds.has(id));
const duplicateIds = [...new Set(items.map((item) => item.id).filter((id, index, ids) => ids.indexOf(id) !== index))];
const checks = {
  final_count: items.length === 11295,
  execution_count: execution.final_count === items.length && execution.removed_count === 61,
  targets_absent_main: [...targetIds].every((id) => !afterIds.has(id)),
  targets_absent_published: [...targetIds].every((id) => !afterPublishedIds.has(id)),
  protected_present_main: [...protectedIds].every((id) => afterIds.has(id)),
  protected_present_published: [...protectedIds].every((id) => afterPublishedIds.has(id)),
  only_target_main_losses: removedMain.length === 61 && removedMain.every((id) => targetIds.has(id)),
  only_target_published_losses: removedPublished.length === 61 && removedPublished.every((id) => targetIds.has(id)),
  primary_published_ids_match: items.length === publishedItems.length && [...afterIds].every((id) => afterPublishedIds.has(id)) && [...afterPublishedIds].every((id) => afterIds.has(id)),
  stats_match_published: JSON.stringify(stats) === JSON.stringify(publishedStats),
  stats_match_items: stats.total_items === items.length && stats.books_count === items.length && stats.with_download_links === items.filter((item) => item.link_telegram || item.link_drive || item.link_direct).length,
  source_counts: items.filter((item) => item.source === 'المكتبة القانونية الكبرى').length === 1671 && items.filter((item) => item.source === 'قناة الرسائل العلمية').length === 430,
  no_duplicate_ids: duplicateIds.length === 0,
};
const output = { final_count: items.length, source_counts_after: { great_law: items.filter((item) => item.source === 'المكتبة القانونية الكبرى').length, academic_theses: items.filter((item) => item.source === 'قناة الرسائل العلمية').length }, removed_main: removedMain, removed_published: removedPublished, duplicate_ids_after: duplicateIds, protected_remaining: [...protectedIds].map((id) => ({ id, title: items.find((item) => item.id === id)?.title ?? null })), checks };
output.passed = Object.values(checks).every(Boolean);
writeFileSync(path.join(root, 'restart_recovery_post_validation.json'), `${JSON.stringify(output, null, 2)}\n`);
console.log(JSON.stringify({ final_count: output.final_count, source_counts_after: output.source_counts_after, removed_main: output.removed_main.length, protected: output.protected_remaining.length, passed: output.passed }, null, 2));
if (!output.passed) process.exit(1);
