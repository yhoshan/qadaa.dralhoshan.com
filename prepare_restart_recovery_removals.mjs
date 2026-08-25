import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const greatLawSubject = [
  'great_law_4949', 'great_law_4952', 'great_law_5008', 'great_law_5010', 'great_law_5014', 'great_law_5137', 'great_law_5189', 'great_law_5206', 'great_law_5216', 'great_law_5227', 'great_law_5243', 'great_law_5347', 'great_law_8441', 'great_law_13315', 'great_law_13345', 'great_law_15295', 'great_law_15339', 'great_law_1888', 'great_law_4768', 'great_law_5204', 'great_law_5239', 'great_law_5409', 'great_law_5414', 'great_law_5443', 'great_law_8683', 'great_law_15188', 'great_law_15342', 'great_law_16770',
];
const greatLawDuplicates = ['great_law_4327', 'great_law_4364', 'great_law_5091'];
const academicSubject = ['risail_25652', 'risail_28874', 'risail_35582', 'risail_36568', 'risail_38256', 'risail_53246', 'risail_54760', 'risail_57563', 'risail_58948', 'risail_25519', 'risail_25520', 'risail_25951', 'risail_25952', 'risail_25953', 'risail_49409', 'risail_50406'];
const academicDuplicates = ['risail_6845', 'risail_8198', 'risail_8199', 'risail_25156', 'risail_9289', 'risail_24600', 'risail_29090', 'risail_28188', 'risail_25877', 'risail_31041', 'risail_29705', 'risail_30065', 'risail_37668', 'risail_59962'];
const protectedIds = [
  'great_law_2410', 'great_law_5355', 'great_law_5393', 'great_law_4316', 'great_law_4322', 'great_law_5090',
  'risail_6221', 'risail_7540', 'risail_11151', 'risail_23788', 'risail_5257', 'risail_8197', 'risail_9223', 'risail_9288', 'risail_15972', 'risail_20471', 'risail_21653', 'risail_25876', 'risail_27506', 'risail_27507', 'risail_28570', 'risail_37585', 'risail_59788',
];
const allTargets = [...greatLawSubject, ...greatLawDuplicates, ...academicSubject, ...academicDuplicates];
if (allTargets.length !== 61 || new Set(allTargets).size !== 61 || allTargets.some((id) => protectedIds.includes(id))) throw new Error('بيان الاستعادة غير صحيح أو يتعارض مع معرف محمي.');
const items = JSON.parse(readFileSync(path.join(root, 'items.json'), 'utf8'));
const published = JSON.parse(readFileSync(path.join(root, 'client/public/items.json'), 'utf8'));
const byId = new Map(items.map((item) => [item.id, item]));
const valid = (item) => {
  if (String(item.id).startsWith('great_law_')) return item.source === 'المكتبة القانونية الكبرى';
  if (String(item.id).startsWith('risail_')) return item.source === 'قناة الرسائل العلمية' && String(item.link_telegram ?? '').includes('t.me/c/1453973283');
  return false;
};
const targets = allTargets.map((id) => byId.get(id)).filter(Boolean);
const missing = allTargets.filter((id) => !byId.has(id));
const protectedRecords = protectedIds.map((id) => byId.get(id)).filter(Boolean);
const manifest = {
  generated_at: new Date().toISOString(),
  expected_before_count: 11356,
  expected_after_count: 11295,
  targets: {
    great_law: { subject: greatLawSubject, duplicates: greatLawDuplicates },
    academic_theses: { subject: academicSubject, duplicates: academicDuplicates },
  },
  all_target_ids: allTargets,
  protected_ids: protectedIds,
};
const verification = {
  before_count: items.length,
  target_count: allTargets.length,
  found_count: targets.length,
  missing_ids: missing,
  wrong_source_or_link: targets.filter((item) => !valid(item)).map((item) => ({ id: item.id, source: item.source, link_telegram: item.link_telegram ?? '', title: item.title })),
  protected_found_count: protectedRecords.length,
  missing_protected_ids: protectedIds.filter((id) => !byId.has(id)),
  primary_published_match: JSON.stringify(items) === JSON.stringify(published),
  targets: targets.map((item) => ({ id: item.id, title: item.title, source: item.source, category: item.category ?? '', type: greatLawSubject.includes(item.id) || academicSubject.includes(item.id) ? 'موضوعي' : 'تكرار زائد' })),
};
verification.passed = verification.before_count === 11356 && verification.target_count === 61 && verification.found_count === 61 && verification.missing_ids.length === 0 && verification.wrong_source_or_link.length === 0 && verification.protected_found_count === protectedIds.length && verification.missing_protected_ids.length === 0 && verification.primary_published_match;
writeFileSync(path.join(root, 'restart_recovery_removal_manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`);
writeFileSync(path.join(root, 'restart_recovery_precheck.json'), `${JSON.stringify(verification, null, 2)}\n`);
console.log(JSON.stringify({ before: verification.before_count, targets: verification.target_count, found: verification.found_count, missing: verification.missing_ids.length, wrong_source_or_link: verification.wrong_source_or_link.length, protected_found: verification.protected_found_count, passed: verification.passed }, null, 2));
if (!verification.passed) process.exit(1);
