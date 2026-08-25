import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const sourceLabel = 'المكتبة القانونية ⚖️';
const channelFragment = 't.me/iirmll/';
const itemsPath = path.join(root, 'items.json');
const publicItemsPath = path.join(root, 'client/public/items.json');
const items = JSON.parse(readFileSync(itemsPath, 'utf8'));
const published = JSON.parse(readFileSync(publicItemsPath, 'utf8'));
const unwrap = (value) => Array.isArray(value) ? value : value.items ?? [];
const mainItems = unwrap(items);
const publicItems = unwrap(published);
const normalize = (text = '') => String(text)
  .normalize('NFKD')
  .replace(/[\u064B-\u065F\u0670]/g, '')
  .replace(/[أإآ]/g, 'ا')
  .replace(/ى/g, 'ي')
  .replace(/ة/g, 'ه')
  .replace(/[٠-٩]/g, (digit) => '٠١٢٣٤٥٦٧٨٩'.indexOf(digit))
  .replace(/\.pdf\b/gi, '')
  .replace(/[^\p{L}\p{N}]+/gu, ' ')
  .replace(/\s+/g, ' ')
  .trim()
  .toLowerCase();
const linkFields = ['link_telegram', 'link_direct', 'link_drive', 'link'];
const structuralLinkState = (item) => {
  const values = linkFields.map((field) => item[field]).filter((value) => typeof value === 'string' && value.trim());
  const valid = values.some((value) => /^https?:\/\//i.test(value.trim()));
  return { values, valid, issue: valid ? null : values.length ? 'لا يوجد رابط HTTP(S) صالح بنيوياً' : 'لا يوجد رابط في الحقول المتاحة' };
};
const selected = mainItems.filter((item) => item.source === sourceLabel && String(item.link_telegram ?? '').includes(channelFragment));
const selectedIds = new Set(selected.map((item) => item.id));
const publishedSelected = publicItems.filter((item) => selectedIds.has(item.id));
const publicIds = new Set(publicItems.map((item) => item.id));
const sourceMismatches = selected.filter((item) => item.source !== sourceLabel || !String(item.link_telegram ?? '').includes(channelFragment))
  .map((item) => ({ id: item.id, source: item.source, title: item.title }));
const invalidLinks = selected.map((item) => ({ item, state: structuralLinkState(item) }))
  .filter(({ state }) => !state.valid)
  .map(({ item, state }) => ({ id: item.id, title: item.title, source: item.source, issue: state.issue, link_values: state.values }));
const groups = new Map();
for (const item of selected) {
  const key = normalize(item.title);
  if (!key) continue;
  groups.set(key, [...(groups.get(key) ?? []), item]);
}
const exactDuplicateGroups = [...groups.entries()]
  .filter(([, records]) => records.length > 1)
  .map(([normalized_title, records]) => ({ normalized_title, records: records.map((item) => ({ id: item.id, title: item.title, source: item.source, category: item.category, links: Object.fromEntries(linkFields.map((field) => [field, item[field] ?? ''])) })) }));
const chunksDir = path.join(root, 'iirmll_source_audit_chunks');
if (existsSync(chunksDir)) rmSync(chunksDir, { recursive: true, force: true });
mkdirSync(chunksDir, { recursive: true });
const records = selected.map((item, index) => {
  const linkState = structuralLinkState(item);
  const record = {
    audit_index: index + 1,
    id: item.id,
    title: item.title,
    author: item.author ?? '',
    investigator: item.investigator ?? '',
    source: item.source ?? '',
    category: item.category ?? '',
    material_type: item.material_type ?? '',
    file_type: item.file_type ?? '',
    file_size: item.file_size ?? '',
    pages_count: item.pages_count ?? '',
    description: item.description ?? item.notes ?? '',
    links: Object.fromEntries(linkFields.map((field) => [field, item[field] ?? ''])),
    has_structurally_valid_link: linkState.valid,
  };
  writeFileSync(path.join(chunksDir, `record_${String(index + 1).padStart(4, '0')}.json`), `${JSON.stringify(record, null, 2)}\n`);
  return record;
});
const sha256 = (file) => createHash('sha256').update(readFileSync(file)).digest('hex');
const output = {
  generated_at: new Date().toISOString(),
  scope: { channel_fragment: channelFragment, source: sourceLabel },
  total_main_items: mainItems.length,
  total_published_items: publicItems.length,
  selected_count: selected.length,
  selected_published_count: publishedSelected.length,
  selected_missing_from_published: selected.filter((item) => !publicIds.has(item.id)).map((item) => item.id),
  source_mismatches: sourceMismatches,
  invalid_links: invalidLinks,
  exact_duplicate_groups: exactDuplicateGroups,
  records,
  baseline_hashes: { items_json: sha256(itemsPath), public_items_json: sha256(publicItemsPath) },
};
writeFileSync(path.join(root, 'iirmll_source_audit_records.json'), `${JSON.stringify(output, null, 2)}\n`);
console.log(JSON.stringify({ selected_count: output.selected_count, selected_published_count: output.selected_published_count, source_mismatches: output.source_mismatches.length, invalid_links: output.invalid_links.length, exact_duplicate_groups: output.exact_duplicate_groups.length, chunks_dir: chunksDir }, null, 2));
if (output.total_main_items !== 11295 || output.total_published_items !== 11295 || output.selected_count !== output.selected_published_count || output.selected_missing_from_published.length || output.source_mismatches.length) process.exit(1);
