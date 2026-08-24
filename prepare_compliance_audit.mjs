import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const ITEMS_PATH = path.join(ROOT, 'items.json');
const JOURNALS_PATH = path.join(ROOT, 'client/src/data/officialJournals.ts');
const OUTPUT_DIR = path.join(ROOT, 'compliance_audit_inputs');
const CHUNK_SIZE = 100;

const items = JSON.parse(fs.readFileSync(ITEMS_PATH, 'utf8')).map((item) => ({
  ...item,
  record_origin: 'items.json',
}));
const journalsSource = fs.readFileSync(JOURNALS_PATH, 'utf8');
const journalsMatch = journalsSource.match(/OFFICIAL_JOURNALS:[^=]+=\s*(\[[\s\S]*\])\s*;?\s*$/);
if (!journalsMatch) {
  throw new Error('تعذر استخراج بيانات المجلات الرسمية من الملف المصدر.');
}
const journals = JSON.parse(journalsMatch[1]).map((journal, index) => ({
  id: `official_journal_${String(index + 1).padStart(4, '0')}`,
  title: journal.name,
  author: '',
  investigator: '',
  publisher: '',
  year: '',
  source: 'قسم المجلات الرسمية',
  category: 'مجلة قانونية أو قضائية',
  material_type: 'مجلة',
  file_type: 'رابط',
  file_size: '',
  pages_count: '',
  link_telegram: '',
  link_drive: '',
  link_direct: journal.officialLink || '',
  country: journal.country || '',
  issn: '',
  frequency: '',
  notes: '',
  description: journal.description || '',
  topic: '',
  import_origin: 'officialJournals.ts',
  record_origin: 'officialJournals.ts',
}));
const allRecords = [...items, ...journals];
fs.rmSync(OUTPUT_DIR, { recursive: true, force: true });
fs.mkdirSync(OUTPUT_DIR, { recursive: true });

const knownFields = new Set();
const fieldPopulation = {};
const categoryCounts = {};
const sourceCounts = {};

const auditRecords = allRecords.map((item, index) => {
  Object.entries(item).forEach(([key, value]) => {
    knownFields.add(key);
    if (value !== '' && value !== null && value !== undefined) {
      fieldPopulation[key] = (fieldPopulation[key] || 0) + 1;
    }
  });

  const source = item.source || 'غير محدد';
  const category = item.category || 'غير محدد';
  sourceCounts[source] = (sourceCounts[source] || 0) + 1;
  categoryCounts[category] = (categoryCounts[category] || 0) + 1;

  const metadata = {
    id: item.id || `row_${index + 1}`,
    title: item.title || '',
    author: item.author || '',
    investigator: item.investigator || '',
    publisher: item.publisher || '',
    year: item.year || '',
    source: item.source || '',
    category: item.category || '',
    material_type: item.material_type || '',
    file_type: item.file_type || '',
    file_size: item.file_size || '',
    pages_count: item.pages_count || '',
    link_telegram: item.link_telegram || '',
    link_drive: item.link_drive || '',
    link_direct: item.link_direct || '',
    country: item.country || '',
    issn: item.issn || '',
    frequency: item.frequency || '',
    notes: item.notes || '',
    description: item.description || '',
    topic: item.topic || '',
    import_origin: item.import_origin || '',
    record_origin: item.record_origin || '',
  };

  return {
    row_number: index + 1,
    metadata,
    source_record_keys: Object.keys(item).sort(),
  };
});

const chunks = [];
for (let start = 0; start < auditRecords.length; start += CHUNK_SIZE) {
  const chunkNumber = chunks.length + 1;
  const records = auditRecords.slice(start, start + CHUNK_SIZE);
  const filename = `chunk_${String(chunkNumber).padStart(3, '0')}.json`;
  fs.writeFileSync(
    path.join(OUTPUT_DIR, filename),
    JSON.stringify(records, null, 2),
  );
  chunks.push({
    chunk_number: chunkNumber,
    filename,
    first_row: records[0].row_number,
    last_row: records.at(-1).row_number,
    count: records.length,
  });
}

const summary = {
  generated_at: new Date().toISOString(),
  primary_data_files: [ITEMS_PATH, JOURNALS_PATH],
  item_records: items.length,
  journal_records: journals.length,
  total_records: auditRecords.length,
  chunk_size: CHUNK_SIZE,
  chunk_count: chunks.length,
  chunks,
  fields_seen: [...knownFields].sort(),
  field_population: fieldPopulation,
  category_counts: categoryCounts,
  source_counts: sourceCounts,
  duplicate_id_count:
    auditRecords.length - new Set(auditRecords.map((record) => record.metadata.id)).size,
};

fs.writeFileSync(
  path.join(ROOT, 'compliance_audit_metadata_manifest.json'),
  JSON.stringify(summary, null, 2),
);

console.log(
  JSON.stringify(
    {
      total_records: summary.total_records,
      chunk_count: summary.chunk_count,
      fields_seen: summary.fields_seen,
      duplicate_id_count: summary.duplicate_id_count,
    },
    null,
    2,
  ),
);
