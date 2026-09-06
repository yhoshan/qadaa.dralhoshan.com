import fs from 'node:fs/promises';

const root = process.cwd();
const sourcePage = 'https://sadr.org/knowledge-center';
const source = 'المركز السعودي للتحكيم التجاري (صدر)';
const html = await fs.readFile(`${root}/sadr_knowledge_center.html`, 'utf8');
const data = JSON.parse(await fs.readFile(`${root}/items.json`, 'utf8'));
const items = Array.isArray(data) ? data : data.items;

function decodeEntities(value = '') {
  return value.replace(/&nbsp;|&#160;/gi, ' ').replace(/&amp;/gi, '&').replace(/&quot;/gi, '"').replace(/&#39;|&apos;/gi, "'").replace(/&#x([\da-f]+);/gi, (_, code) => String.fromCodePoint(parseInt(code, 16))).replace(/&#(\d+);/g, (_, code) => String.fromCodePoint(Number(code)));
}
function clean(value = '') { return decodeEntities(value.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ')).trim(); }
function normalizeArabic(value = '') {
  return String(value).normalize('NFKD').replace(/[\u064B-\u065F\u0670\u0640]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه').replace(/ؤ/g, 'و').replace(/ئ/g, 'ي').replace(/[^\p{L}\p{N}]+/gu, '').toLowerCase();
}
function normalizeUrl(value = '') { return String(value).trim().replace(/[?&]key=\d+$/u, '').replace(/\/$/u, ''); }
function classification(label, title) {
  const info = `${label} ${title}`;
  if (/دراسات|Studies/u.test(info)) return { category: 'التحكيم وتسوية المنازعات', material_type: 'بحث' };
  if (/(تحكيم|وساطة|تسوية المنازعات|القرارات الفنية|الأونسيترال)/u.test(info)) return { category: 'التحكيم وتسوية المنازعات', material_type: /دليل|معايير/u.test(info) ? 'دليل' : 'نظام' };
  if (/أحكام قضائية|الحكم رقم/u.test(info)) return { category: 'الأحكام القضائية', material_type: 'حكم قضائي' };
  return { category: 'التحكيم وتسوية المنازعات', material_type: 'نظام' };
}

const existingTitles = new Map();
const existingUrls = new Set();
for (const item of items) {
  const titleKey = normalizeArabic(item.title ?? '');
  if (titleKey && !existingTitles.has(titleKey)) existingTitles.set(titleKey, item);
  for (const link of [item.link_direct, item.link_drive, item.link_telegram]) if (link) existingUrls.add(normalizeUrl(link));
}

const cards = [...html.matchAll(/data-category="-([^"<>]+)-"[\s\S]*?<h3\b[^>]*>[\s\S]*?<a\b[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/giu)];
const parsed = cards.map((match) => ({ label: clean(match[1]), url: decodeEntities(match[2]), title: clean(match[3]) })).filter((row) => row.title && row.url.endsWith('.pdf') || row.url.includes('.pdf?'));
const seenTitles = new Set();
const candidates = [];
const excluded = [];
for (const row of parsed) {
  const titleKey = normalizeArabic(row.title);
  const urlKey = normalizeUrl(row.url);
  let reason = '';
  if (seenTitles.has(titleKey)) reason = 'تكرار داخلي في صفحة المصدر';
  else if (existingTitles.has(titleKey)) reason = `عنوان موجود: ${existingTitles.get(titleKey).id}`;
  else if (existingUrls.has(urlKey)) reason = 'رابط موجود في المكنز';
  if (reason) {
    excluded.push({ ...row, reason });
    continue;
  }
  seenTitles.add(titleKey);
  candidates.push({ ...row, ...classification(row.label, row.title), source, source_page: sourcePage, publisher: source, author: '', investigator: '', year: '', link_telegram: '', link_drive: '', link_direct: row.url, file_type: 'PDF', file_size: '', pages_count: '', is_featured: false, download_links_count: 1 });
}
const output = { generated_at: new Date().toISOString(), source, source_page: sourcePage, totals: { cards_found: parsed.length, candidates: candidates.length, excluded: excluded.length }, candidates, excluded };
await fs.writeFile(`${root}/sadr_legal_candidates.json`, JSON.stringify(output, null, 2));
await fs.writeFile(`${root}/sadr_legal_candidates.txt`, [
  `المصدر: ${source}`,
  `صفحة مركز المعرفة: ${sourcePage}`,
  `المواد الرسمية المستخرجة: ${parsed.length}`,
  `مرشحات قانونية غير مكررة مبدئياً: ${candidates.length}`,
  `مستبعدة لسبق وجودها أو لتكرار داخلي: ${excluded.length}`,
  '',
  'المرشحات:',
  ...candidates.map((item, index) => `${index + 1}. ${item.title}\n   النوع: ${item.material_type} | التصنيف: ${item.category}\n   ${item.link_direct}`),
  '',
  'المستبعدة:',
  ...excluded.map((item, index) => `${index + 1}. ${item.title} | ${item.reason}`),
].join('\n'));
console.log(JSON.stringify(output.totals));
