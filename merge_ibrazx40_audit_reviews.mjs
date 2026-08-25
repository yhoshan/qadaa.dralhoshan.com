import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
const root = process.cwd();
const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const initial = load('ibrazx40_source_initial_classifications.json').classifications;
const critical = new Map(load('ibrazx40_critical_reviews.json').reviews.map((row) => [row.id, row]));
const records = new Map(load('ibrazx40_source_audit_records.json').records.map((row) => [row.id, row]));
const merged = initial.map((row) => {
  const review = critical.get(row.id);
  const final = review ?? row;
  return { ...row, final_decision: final.decision, final_reason: final.reason, final_confidence: final.confidence, critical_review: review ?? null };
});
const candidates = merged.filter((row) => row.final_decision !== 'KEEP' || (row.critical_review && row.critical_review.decision !== row.decision)).map((row) => ({ record: records.get(row.id), merged: row }));
const output = { total: merged.length, merged, final_candidates: candidates };
writeFileSync(path.join(root, 'ibrazx40_merged_audit_reviews.json'), `${JSON.stringify(output, null, 2)}\n`);
console.log(JSON.stringify({ total: merged.length, final_candidates: candidates.length, decisions: Object.fromEntries(['KEEP','REMOVE','REVIEW'].map((d) => [d, merged.filter((r) => r.final_decision === d).length])) }, null, 2));
