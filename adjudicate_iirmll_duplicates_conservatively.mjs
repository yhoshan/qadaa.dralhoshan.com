import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const source = JSON.parse(readFileSync(path.join(root, 'iirmll_duplicate_candidates.json'), 'utf8'));
const nonempty = (value) => typeof value === 'string' && value.trim().length > 0;
const scorePair = (left, right) => {
  const sameTitle = left.normalized_title === right.normalized_title;
  const sameTelegram = nonempty(left.links?.link_telegram) && left.links.link_telegram === right.links.link_telegram;
  const metadataKeys = ['author', 'category', 'material_type', 'file_type', 'file_size', 'pages_count', 'description'];
  const sharedMetadata = metadataKeys.filter((key) => nonempty(left[key]) && left[key] === right[key]);
  return { sameTitle, sameTelegram, sharedMetadata, strong: sameTelegram || (sameTitle && sharedMetadata.length >= 3) };
};
const numericSuffix = (id) => Number(String(id).match(/(\d+)$/)?.[1] ?? Number.MAX_SAFE_INTEGER);
const adjudications = source.groups.map((group) => {
  const strongPairs = [];
  for (let left = 0; left < group.records.length; left += 1) for (let right = left + 1; right < group.records.length; right += 1) {
    const score = scorePair(group.records[left], group.records[right]);
    if (score.strong) strongPairs.push({ left: group.records[left].id, right: group.records[right].id, ...score });
  }
  const confirmedIds = new Set(strongPairs.flatMap((pair) => [pair.left, pair.right]));
  if (confirmedIds.size < 2) return {
    group_id: group.group_id,
    records: group.records,
    confirmed: false,
    recommended_keep_id: null,
    redundant_ids: [],
    reason: 'التشابه العنواني وحده أو تقارب الموضوع لا يثبت أن الوثائق نسخة واحدة؛ لا توجد مطابقة رابط أو قرائن وصفية كافية.',
    evidence: strongPairs,
  };
  const candidates = group.records.filter((record) => confirmedIds.has(record.id)).sort((a, b) => numericSuffix(a.id) - numericSuffix(b.id));
  const keep = candidates[0];
  return {
    group_id: group.group_id,
    records: group.records,
    confirmed: true,
    recommended_keep_id: keep.id,
    redundant_ids: candidates.slice(1).map((record) => record.id),
    reason: 'تطابق العنوان بعد التطبيع مقترناً بتطابق رابط أو بثلاث قرائن وصفية غير فارغة على الأقل؛ هذه توصية تنظيمية فقط لا تنفيذ لها.',
    evidence: strongPairs,
  };
});
const output = {
  total_candidate_groups: adjudications.length,
  confirmed_groups: adjudications.filter((group) => group.confirmed),
  unconfirmed_groups: adjudications.filter((group) => !group.confirmed),
};
writeFileSync(path.join(root, 'iirmll_duplicate_conservative_adjudications.json'), `${JSON.stringify(output, null, 2)}\n`);
console.log(JSON.stringify({ candidates: output.total_candidate_groups, confirmed_groups: output.confirmed_groups.length, redundant_ids: output.confirmed_groups.reduce((sum, group) => sum + group.redundant_ids.length, 0), unconfirmed_groups: output.unconfirmed_groups.length }, null, 2));
