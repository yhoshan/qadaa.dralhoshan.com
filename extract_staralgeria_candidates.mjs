import fs from 'node:fs/promises';

const root = process.cwd();
const sourcePage = 'https://www.staralgeria.net/t1950-topic/';
const source = 'Star Algeria';
const post = JSON.parse(await fs.readFile(`${root}/staralgeria_post_4265.json`, 'utf8'));
const data = JSON.parse(await fs.readFile(`${root}/items.json`, 'utf8'));
const items = Array.isArray(data) ? data : data.items;
const content = post?.content?.rendered ?? '';

function decodeEntities(value = '') {
  return value
    .replace(/&nbsp;|&#160;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;|&apos;/gi, "'")
    .replace(/&#x([\da-f]+);/gi, (_, code) => String.fromCodePoint(parseInt(code, 16)))
    .replace(/&#(\d+);/g, (_, code) => String.fromCodePoint(Number(code)));
}
function stripTags(value = '') {
  return decodeEntities(value.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ')).trim();
}
function normalizeArabic(value = '') {
  return String(value)
    .normalize('NFKD')
    .replace(/[\u064B-\u065F\u0670\u0640]/g, '')
    .replace(/[أإآٱ]/g, 'ا')
    .replace(/ى/g, 'ي')
    .replace(/ة/g, 'ه')
    .replace(/[ؤ]/g, 'و')
    .replace(/[ئ]/g, 'ي')
    .replace(/[^\p{L}\p{N}]+/gu, '')
    .toLowerCase();
}
function cleanTitle(value = '') {
  return stripTags(value)
    .replace(/\.(?:pdf|docx?|rar|zip|mp3)$/iu, '')
    .replace(/\s+/g, ' ')
    .replace(/^[-–—\s]+|[-–—\s]+$/g, '')
    .trim();
}
function categoryFor(title) {
  if (/(إثبات|اثبات|دعوى|دعواى|محكم|قاض|قضاء|مرافع|تنفيذ|طعن|نياب|إجراء|اجراء|تحقيق|جنح|جنائي|جزائي|عقوب|متهم|جريم)/u.test(title)) return 'المحاكم والمرافعات';
  if (/(إدار|ادار|دستور|صفقات عمومية|تشريع|سلطات الإدارة|سلطة المبادرة)/u.test(title)) return 'القانون الإداري والدستوري';
  if (/(تجار|شركة|إفلاس|افلاس|بنك|مصرف|كمرك|جمرك|تأمين|عقد|بيع|ملكية|عقار|مستهلك|عمل|مالية|ضرائب|نقل|بحري|جوي|امتياز)/u.test(title)) return 'القانون التجاري والاستثمار';
  if (/(أسرة|اسرة|أحوال شخصية|حضانه|زواج|طلاق|وصاية|ميراث|مواريث)/u.test(title)) return 'الأحوال الشخصية';
  if (/(دولي|إنسان|انسان|محكمة العدل)/u.test(title)) return 'القانون الدولي';
  return 'الأنظمة والتشريعات';
}
function appearsSubstantive(title) {
  if (title.length < 8) return false;
  if (/^(رسائل ماجستير|مذكرات|بحوث|قانون|سلطات)$/u.test(title)) return false;
  if (/(كلمة السر|فهرس|تحميل أكثر من|المواضيع|ملاحظة مهمة)/u.test(title)) return false;
  if (/(أصول الفقه|القواعد الفقهية|المدخل إلى الفقه الإسلامي|القضاء والقدر)/u.test(title)) return false;
  return true;
}

const existingByTitle = new Map();
const existingLinks = new Set();
for (const item of items) {
  const normalized = normalizeArabic(item.title ?? '');
  if (normalized && !existingByTitle.has(normalized)) existingByTitle.set(normalized, item);
  for (const link of [item.link_direct, item.link_drive, item.link_telegram]) if (link) existingLinks.add(String(link).trim());
}

const anchors = [...content.matchAll(/<a\b[^>]*href\s*=\s*["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/giu)];
const allLinks = anchors.map((match) => ({
  title: cleanTitle(match[2]),
  url: decodeEntities(match[1]).trim(),
}));

const uniqueSeen = new Set();
const candidates = [];
const excluded = [];
for (const row of allLinks) {
  const key = normalizeArabic(row.title);
  let reason = '';
  if (!row.url || !/^https?:\/\//iu.test(row.url)) reason = 'ليس رابط ملف خارجي صالحاً';
  else if (!appearsSubstantive(row.title)) reason = 'عنوان تجميعي أو غير متخصص أو خارج نطاق المكنز';
  else if (uniqueSeen.has(key)) reason = 'تكرار عنوان داخل المقال';
  else if (existingByTitle.has(key)) reason = `عنوان موجود: ${existingByTitle.get(key).id}`;
  else if (existingLinks.has(row.url)) reason = 'رابط موجود في المكنز';
  if (reason) {
    excluded.push({ ...row, reason });
  } else {
    uniqueSeen.add(key);
    candidates.push({
      title: row.title,
      url: row.url,
      source,
      source_page: sourcePage,
      category: categoryFor(row.title),
      material_type: 'بحث',
      file_type: row.url.toLowerCase().includes('.pdf') ? 'PDF' : row.url.toLowerCase().includes('.doc') ? 'Word' : 'ZIP',
    });
  }
}
const output = {
  generated_at: new Date().toISOString(),
  source_page: sourcePage,
  source_title: cleanTitle(post?.title?.rendered ?? ''),
  totals: { links_found: allLinks.length, candidates: candidates.length, excluded: excluded.length },
  candidates,
  excluded,
};
await fs.writeFile(`${root}/staralgeria_legal_candidates.json`, JSON.stringify(output, null, 2));
await fs.writeFile(`${root}/staralgeria_legal_candidates.txt`, [
  `مصدر الصفحة: ${sourcePage}`,
  `عنوان الصفحة: ${output.source_title}`,
  `إجمالي روابط الملفات المستخرجة: ${allLinks.length}`,
  `مرشحات قانونية جديدة مبدئية: ${candidates.length}`,
  `مستبعدة أو موجودة: ${excluded.length}`,
  '',
  'المرشحات:',
  ...candidates.map((item, index) => `${index + 1}. ${item.title}\n   ${item.url}\n   ${item.category}`),
  '',
  'المستبعدات:',
  ...excluded.map((item, index) => `${index + 1}. ${item.title} | ${item.reason}`),
].join('\n'));
console.log(JSON.stringify(output.totals));
