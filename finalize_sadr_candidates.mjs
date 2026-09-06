import fs from 'node:fs/promises';

const root = process.cwd();
const candidatesData = JSON.parse(await fs.readFile(`${root}/sadr_legal_candidates.json`, 'utf8'));
const verificationData = JSON.parse(await fs.readFile('/home/ubuntu/verify_sadr_public_documents.json', 'utf8'));
const data = JSON.parse(await fs.readFile(`${root}/items.json`, 'utf8'));
const items = Array.isArray(data) ? data : data.items;

function normalizeArabic(value = '') {
  return String(value).normalize('NFKD').replace(/[\u064B-\u065F\u0670\u0640]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه').replace(/ؤ/g, 'و').replace(/ئ/g, 'ي').replace(/[^\p{L}\p{N}]+/gu, '').toLowerCase();
}
function normalizeUrl(value = '') { return String(value).trim().replace(/[?&]key=\d+$/u, '').replace(/\/$/u, ''); }
const existingTitles = new Map();
const existingUrls = new Set();
for (const item of items) {
  const key = normalizeArabic(item.title ?? '');
  if (key && !existingTitles.has(key)) existingTitles.set(key, item);
  for (const link of [item.link_direct, item.link_drive, item.link_telegram]) if (link) existingUrls.add(normalizeUrl(link));
}
const verifiedByTitle = new Map();
for (const row of verificationData.results) {
  const output = row.output;
  if (row.error || !output?.is_publicly_open || output.http_status < 200 || output.http_status >= 400) continue;
  verifiedByTitle.set(normalizeArabic(output.title ?? row.input.split(' | ')[0]), output);
}
const ready = [];
const excluded = [];
for (const candidate of candidatesData.candidates) {
  const key = normalizeArabic(candidate.title);
  const verified = verifiedByTitle.get(key);
  let reason = '';
  if (!verified) reason = 'تعذر إثبات فتح رابط المستند للعامة';
  else if (existingTitles.has(key)) reason = `عنوان موجود: ${existingTitles.get(key).id}`;
  else if (existingUrls.has(normalizeUrl(verified.final_url || verified.url))) reason = 'رابط موجود في المكنز';
  if (reason) {
    excluded.push({ title: candidate.title, url: candidate.link_direct, reason });
    continue;
  }
  ready.push({
    ...candidate,
    link_direct: verified.final_url || verified.url,
    verification: { checked_at: new Date().toISOString(), status: verified.http_status, note: verified.notes },
  });
}
const output = {
  generated_at: new Date().toISOString(),
  source: candidatesData.source,
  source_page: candidatesData.source_page,
  totals: { initial_candidates: candidatesData.candidates.length, publicly_open: verifiedByTitle.size, accepted_for_addition: ready.length, excluded: excluded.length },
  candidates: ready,
  excluded,
};
await fs.writeFile(`${root}/sadr_final_candidates.json`, JSON.stringify(output, null, 2));
await fs.writeFile(`${root}/sadr_final_candidates.txt`, [
  `المصدر: ${output.source}`,
  `المرشحات المبدئية: ${output.totals.initial_candidates}`,
  `الروابط العامة التي ثبتت: ${output.totals.publicly_open}`,
  `الصالحة للإضافة بعد منع التكرار: ${output.totals.accepted_for_addition}`,
  `المستبعدة: ${output.totals.excluded}`,
  '',
  'سجلات جاهزة للإضافة:',
  ...ready.map((item, index) => `${index + 1}. ${item.title} | ${item.material_type} | ${item.category}\n   ${item.link_direct}`),
  '',
  'المستبعدة:',
  ...excluded.map((item, index) => `${index + 1}. ${item.title} | ${item.reason}`),
].join('\n'));
console.log(JSON.stringify(output.totals));
