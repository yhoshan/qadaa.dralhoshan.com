import { mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const raw = JSON.parse(readFileSync(path.join(root, 'items.json'), 'utf8'));
const items = Array.isArray(raw) ? raw : raw.items;
const sourceName = 'القانون الدولي العام';
const bySource = items.filter((item) => String(item.source ?? '') === sourceName);
const byLink = items.filter((item) => [item.link_telegram, item.link_drive, item.link_direct].some((link) => String(link ?? '').includes('ibrazx40')));
const sourceIds = new Set(bySource.map((item) => item.id));
const linkIds = new Set(byLink.map((item) => item.id));
const onlyLink = [...linkIds].filter((id) => !sourceIds.has(id));
const onlySource = [...sourceIds].filter((id) => !linkIds.has(id));
if (!bySource.length) throw new Error('لم يعثر على أي سجل باسم المصدر القانون الدولي العام.');
const isHttp = (value) => /^https?:\/\/[^\s]+$/i.test(String(value ?? '').trim());
const project = bySource.map((item, index) => ({
  sequence: index + 1,
  id: item.id,
  title: item.title ?? '', author: item.author ?? '', investigator: item.investigator ?? '', publisher: item.publisher ?? '', year: item.year ?? '',
  source: item.source ?? '', category: item.category ?? '', material_type: item.material_type ?? '', file_type: item.file_type ?? '',
  link_telegram: item.link_telegram ?? '', link_drive: item.link_drive ?? '', link_direct: item.link_direct ?? '',
  file_size: item.file_size ?? '', pages_count: item.pages_count ?? '', download_links_count: item.download_links_count ?? 0,
}));
const badLinks = project.filter((item) => ![item.link_telegram, item.link_drive, item.link_direct].some(isHttp)).map((item) => ({ id: item.id, title: item.title, link_telegram: item.link_telegram, link_drive: item.link_drive, link_direct: item.link_direct }));
const normalize = (text) => String(text ?? '').toLowerCase().replace(/\.pdf$/i, '').replace(/[أإآا]/g, 'ا').replace(/[٠-٩]/g, (d) => '٠١٢٣٤٥٦٧٨٩'.indexOf(d)).replace(/[\W_]+/g, ' ').trim();
const grouped = new Map();
for (const item of project) { const key = normalize(item.title); if (!key) continue; grouped.set(key, [...(grouped.get(key) ?? []), item]); }
const exactTitleGroups = [...grouped.values()].filter((group) => group.length > 1).map((group) => group.map((item) => item.id));
const audit = { generated_at: new Date().toISOString(), source_name: sourceName, link_identifier: 'ibrazx40', total: project.length, by_source_count: bySource.length, by_link_count: byLink.length, source_link_scope_mismatch: { link_only: onlyLink, source_only: onlySource }, bad_links: badLinks, exact_title_groups: exactTitleGroups, records: project };
writeFileSync(path.join(root, 'ibrazx40_source_audit_records.json'), `${JSON.stringify(audit, null, 2)}\n`);
const chunkDir = path.join(root, 'ibrazx40_source_audit_chunks');
rmSync(chunkDir, { recursive: true, force: true }); mkdirSync(chunkDir);
for (const record of project) writeFileSync(path.join(chunkDir, `record_${String(record.sequence).padStart(3, '0')}.json`), `${JSON.stringify(record, null, 2)}\n`);
console.log(JSON.stringify({ total: project.length, by_source_count: bySource.length, by_link_count: byLink.length, source_only: onlySource.length, link_only: onlyLink.length, bad_links: badLinks.length, exact_title_groups: exactTitleGroups.length, chunk_directory: chunkDir }, null, 2));
