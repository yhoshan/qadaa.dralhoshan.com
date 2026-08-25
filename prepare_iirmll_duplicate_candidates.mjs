import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const source = JSON.parse(readFileSync(path.join(root, 'iirmll_source_audit_records.json'), 'utf8'));
const records = source.records;
const normalize = (text = '') => String(text)
  .normalize('NFKD')
  .replace(/[\u064B-\u065F\u0670]/g, '')
  .replace(/[أإآ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه')
  .replace(/[٠-٩]/g, (digit) => '٠١٢٣٤٥٦٧٨٩'.indexOf(digit))
  .replace(/\.pdf\b/gi, '')
  .replace(/[^\p{L}\p{N}]+/gu, ' ')
  .replace(/\s+/g, ' ').trim().toLowerCase();
const sets = records.map((record) => new Set(normalize(record.title).split(' ').filter(Boolean)));
const parent = Array.from({ length: records.length }, (_, index) => index);
const find = (index) => parent[index] === index ? index : (parent[index] = find(parent[index]));
const join = (left, right) => { const a = find(left); const b = find(right); if (a !== b) parent[b] = a; };
const reasons = new Map();
const addReason = (left, right, reason) => { const key = `${Math.min(left, right)}:${Math.max(left, right)}`; reasons.set(key, reason); join(left, right); };
for (let left = 0; left < records.length; left += 1) {
  for (let right = left + 1; right < records.length; right += 1) {
    const a = normalize(records[left].title);
    const b = normalize(records[right].title);
    if (!a || !b) continue;
    if (a === b) { addReason(left, right, 'تطابق كامل بعد التطبيع'); continue; }
    const intersection = [...sets[left]].filter((token) => sets[right].has(token)).length;
    const union = new Set([...sets[left], ...sets[right]]).size;
    const jaccard = union ? intersection / union : 0;
    const contains = a.includes(b) || b.includes(a);
    if ((jaccard >= 0.86 && Math.min(sets[left].size, sets[right].size) >= 3) || (contains && Math.min(a.length, b.length) >= 18 && jaccard >= 0.7)) addReason(left, right, `تقارب عنواني مرتفع (Jaccard ${jaccard.toFixed(2)})`);
  }
}
const grouped = new Map();
records.forEach((record, index) => { const rootIndex = find(index); grouped.set(rootIndex, [...(grouped.get(rootIndex) ?? []), index]); });
const groups = [...grouped.values()].filter((indices) => indices.length > 1).map((indices, index) => {
  const pairReasons = [];
  for (let a = 0; a < indices.length; a += 1) for (let b = a + 1; b < indices.length; b += 1) {
    const key = `${Math.min(indices[a], indices[b])}:${Math.max(indices[a], indices[b])}`;
    if (reasons.has(key)) pairReasons.push(reasons.get(key));
  }
  return {
    group_id: `iirmll_dup_${String(index + 1).padStart(3, '0')}`,
    candidate_reasons: [...new Set(pairReasons)],
    records: indices.map((recordIndex) => ({ ...records[recordIndex], normalized_title: normalize(records[recordIndex].title) })),
  };
});
const output = { total_records: records.length, candidate_group_count: groups.length, groups };
writeFileSync(path.join(root, 'iirmll_duplicate_candidates.json'), `${JSON.stringify(output, null, 2)}\n`);
console.log(JSON.stringify({ total_records: records.length, candidate_group_count: groups.length }, null, 2));
