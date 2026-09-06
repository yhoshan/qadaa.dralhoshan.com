import fs from 'node:fs/promises';

const root = process.cwd();
const data = JSON.parse(await fs.readFile(`${root}/items.json`, 'utf8'));
const items = Array.isArray(data) ? data : data.items;
const marqoom = JSON.parse(await fs.readFile(`${root}/marqoom_final_candidates.json`, 'utf8'));
const sadr = JSON.parse(await fs.readFile(`${root}/sadr_final_candidates.json`, 'utf8'));

function normalizeArabic(value = '') {
  return String(value).normalize('NFKD').replace(/[\u064B-\u065F\u0670\u0640]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه').replace(/ؤ/g, 'و').replace(/ئ/g, 'ي').replace(/[^\p{L}\p{N}]+/gu, '').toLowerCase();
}
function normalizeUrl(value = '') { return String(value).trim().replace(/^http:\/\//iu, 'https://').replace(/[?&]key=\d+$/u, '').replace(/\/$/u, ''); }
const existingTitles = new Map();
const existingUrls = new Map();
for (const item of items) {
  const title = normalizeArabic(item.title ?? '');
  if (title && !existingTitles.has(title)) existingTitles.set(title, item.id);
  for (const link of [item.link_direct, item.link_drive, item.link_telegram]) if (link && !existingUrls.has(normalizeUrl(link))) existingUrls.set(normalizeUrl(link), item.id);
}
const input = [...marqoom.candidates, ...sadr.candidates];
const seenTitles = new Map();
const seenUrls = new Map();
const accepted = [];
const rejected = [];
for (const candidate of input) {
  const titleKey = normalizeArabic(candidate.title);
  const urlKey = normalizeUrl(candidate.link_direct);
  let reason = '';
  if (!candidate.title || !candidate.link_direct) reason = 'عنوان أو رابط مفقود';
  else if (existingTitles.has(titleKey)) reason = `عنوان موجود في المكنز: ${existingTitles.get(titleKey)}`;
  else if (existingUrls.has(urlKey)) reason = `رابط موجود في المكنز: ${existingUrls.get(urlKey)}`;
  else if (seenTitles.has(titleKey)) reason = `عنوان مكرر بين الدفعة: ${seenTitles.get(titleKey)}`;
  else if (seenUrls.has(urlKey)) reason = `رابط مكرر بين الدفعة: ${seenUrls.get(urlKey)}`;
  if (reason) {
    rejected.push({ id: candidate.id ?? '', title: candidate.title, source: candidate.source, link_direct: candidate.link_direct, reason });
    continue;
  }
  seenTitles.set(titleKey, candidate.title);
  seenUrls.set(urlKey, candidate.title);
  accepted.push(candidate);
}
const bySource = Object.fromEntries(Object.entries(accepted.reduce((acc, item) => { acc[item.source] = (acc[item.source] ?? 0) + 1; return acc; }, {})).sort(([a], [b]) => a.localeCompare(b, 'ar')));
const output = { generated_at: new Date().toISOString(), current_total: items.length, input_total: input.length, accepted_total: accepted.length, rejected_total: rejected.length, by_source: bySource, accepted, rejected };
await fs.writeFile(`${root}/marqoom_sadr_additions_preflight.json`, JSON.stringify(output, null, 2));
await fs.writeFile(`${root}/marqoom_sadr_additions_preflight.txt`, [
  `الإجمالي الحالي: ${output.current_total}`,
  `إجمالي المرشحات المستلمة: ${output.input_total}`,
  `الصالحة للإضافة: ${output.accepted_total}`,
  `المستبعدة في الفحص النهائي: ${output.rejected_total}`,
  '',
  'حسب المصدر:',
  ...Object.entries(bySource).map(([source, count]) => `- ${source}: ${count}`),
  '',
  'المواد الجاهزة للإضافة:',
  ...accepted.map((item, index) => `${index + 1}. ${item.title} | ${item.source} | ${item.category}`),
  '',
  'المستبعدات النهائية:',
  ...rejected.map((item, index) => `${index + 1}. ${item.title} | ${item.source} | ${item.reason}`),
].join('\n'));
console.log(JSON.stringify({ current_total: output.current_total, accepted_total: output.accepted_total, rejected_total: output.rejected_total, by_source: output.by_source }));
