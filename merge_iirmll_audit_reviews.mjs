import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const source = load('iirmll_source_audit_records.json');
const initial = load('iirmll_source_initial_classifications.json').classifications;
const critical = load('iirmll_critical_reviews.json').reviews;
const criticalById = new Map(critical.map((item) => [item.id, item]));
const recordById = new Map(source.records.map((item) => [item.id, item]));
const merged = [];
const adjudication = [];
for (const initialRow of initial) {
  const criticalRow = criticalById.get(initialRow.id);
  let provisional = initialRow.decision;
  let rationale = initialRow.reason;
  let needsAdjudication = false;
  if (criticalRow?.critical) {
    provisional = criticalRow.critical.decision;
    rationale = criticalRow.critical.reason;
    needsAdjudication = criticalRow.critical.decision !== initialRow.decision || initialRow.decision !== 'KEEP' || criticalRow.critical.decision !== 'KEEP';
  }
  const entry = { id: initialRow.id, title: initialRow.title, initial: initialRow, critical: criticalRow?.critical ?? null, provisional_decision: provisional, provisional_reason: rationale, needs_adjudication: needsAdjudication };
  merged.push(entry);
  if (needsAdjudication) adjudication.push({ record: recordById.get(initialRow.id), ...entry });
}
const output = { total_records: merged.length, merged, adjudication_queue: adjudication, adjudication_count: adjudication.length, critical_errors: critical.filter((item) => item.error).map((item) => item.id) };
writeFileSync(path.join(root, 'iirmll_merged_audit_reviews.json'), `${JSON.stringify(output, null, 2)}\n`);
console.log(JSON.stringify({ total_records: output.total_records, adjudication_count: output.adjudication_count, critical_errors: output.critical_errors.length }, null, 2));
if (output.total_records !== source.selected_count || output.critical_errors.length) process.exit(1);
