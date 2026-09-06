import fs from 'node:fs/promises';

const root = process.cwd();
const source = 'شبكة مكتبة القانون';
const candidatesData = JSON.parse(await fs.readFile(`${root}/marqoom_legal_candidates.json`, 'utf8'));
const directData = JSON.parse(await fs.readFile('/home/ubuntu/verify_marqoom_direct_links.json', 'utf8'));
const data = JSON.parse(await fs.readFile(`${root}/items.json`, 'utf8'));
const items = Array.isArray(data) ? data : data.items;

function normalizeArabic(value = '') {
  return String(value).normalize('NFKD')
    .replace(/[\u064B-\u065F\u0670\u0640]/g, '')
    .replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه').replace(/ؤ/g, 'و').replace(/ئ/g, 'ي')
    .replace(/[^\p{L}\p{N}]+/gu, '').toLowerCase();
}
function verificationTitleKey(value = '') {
  return normalizeArabic(String(value).replace(/\(\s*\d+\s*(?:حقق|نظم)\s*\)/gu, ' '));
}
function normalizeUrl(value = '') {
  return String(value).trim().replace(/^http:\/\//iu, 'https://').replace(/\/$/u, '');
}
const existingTitles = new Map();
const existingUrls = new Set();
for (const item of items) {
  const titleKey = normalizeArabic(item.title ?? '');
  if (titleKey && !existingTitles.has(titleKey)) existingTitles.set(titleKey, item);
  for (const link of [item.link_direct, item.link_drive, item.link_telegram]) if (link) existingUrls.add(normalizeUrl(link));
}
const availableByTitle = new Map();
for (const row of directData.results) {
  const output = row.output;
  if (row.error || !output?.is_publicly_open || output.http_status < 200 || output.http_status >= 400) continue;
  const titleKey = verificationTitleKey(output.title ?? row.input.split(' | ')[0]);
  availableByTitle.set(titleKey, output);
}

const ready = [];
const excluded = [];
for (const candidate of candidatesData.candidates) {
  const key = normalizeArabic(candidate.title);
  const verified = availableByTitle.get(verificationTitleKey(candidate.title));
  let reason = '';
  if (!verified) reason = 'لم يكتمل التحقق من رابط التحميل أو ثبت تعذره';
  else if (existingTitles.has(key)) reason = `عنوان موجود: ${existingTitles.get(key).id}`;
  else if (existingUrls.has(normalizeUrl(verified.final_url || verified.url))) reason = 'رابط تحميل موجود في المكنز';
  if (reason) {
    excluded.push({ title: candidate.title, source_url: candidate.url, file_url: verified?.final_url || verified?.url || '', reason });
    continue;
  }
  ready.push({
    title: candidate.title,
    author: '',
    investigator: '',
    publisher: source,
    year: '',
    link_telegram: '',
    link_drive: '',
    link_direct: verified.final_url || verified.url,
    source,
    category: candidate.category,
    material_type: 'ملخص',
    file_type: 'رابط',
    file_size: '',
    pages_count: '',
    is_featured: false,
    download_links_count: 1,
    source_page: candidate.url,
    verification: { checked_at: new Date().toISOString(), status: verified.http_status, note: verified.notes },
  });
}
const output = {
  generated_at: new Date().toISOString(),
  source,
  source_page: 'https://www.m2r3.com/book/',
  totals: { initial_candidates: candidatesData.candidates.length, publicly_open: availableByTitle.size, accepted_for_addition: ready.length, excluded: excluded.length },
  candidates: ready,
  excluded,
};
await fs.writeFile(`${root}/marqoom_final_candidates.json`, JSON.stringify(output, null, 2));
await fs.writeFile(`${root}/marqoom_final_candidates.txt`, [
  `المصدر: ${source}`,
  `المرشحات المبدئية: ${output.totals.initial_candidates}`,
  `الروابط المفتوحة التي ثبتت: ${output.totals.publicly_open}`,
  `الصالحة للإضافة بعد منع التكرار: ${output.totals.accepted_for_addition}`,
  `المستبعدة أو المؤجلة: ${output.totals.excluded}`,
  '',
  'سجلات جاهزة للإضافة:',
  ...ready.map((item, index) => `${index + 1}. ${item.title}\n   ${item.link_direct}\n   ${item.category}`),
  '',
  'سجلات مستبعدة أو مؤجلة:',
  ...excluded.map((item, index) => `${index + 1}. ${item.title} | ${item.reason}`),
].join('\n'));
console.log(JSON.stringify(output.totals));
