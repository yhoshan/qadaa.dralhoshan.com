import fs from 'node:fs/promises';

const root = process.cwd();
const html = await fs.readFile('/home/ubuntu/browser_html/kenanaonline_com_324127_1788695054087.html', 'utf8');
const data = JSON.parse(await fs.readFile(`${root}/items.json`, 'utf8'));
const items = Array.isArray(data) ? data : data.items;
const source = 'كلية الحقوق (المكتبة القانونية)';
const sourcePage = 'http://kenanaonline.com/users/HalimLoi/posts/324127';

function decode(value = '') {
  return String(value).replace(/<[^>]+>/g, ' ').replace(/&nbsp;/giu, ' ').replace(/&amp;/giu, '&').replace(/&quot;/giu, '"').replace(/&#(?:x)?[0-9a-f]+;/giu, ' ').replace(/\s+/g, ' ').trim();
}
function normalizeArabic(value = '') {
  return decode(value).normalize('NFKD').replace(/[\u064B-\u065F\u0670\u0640]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه').replace(/ؤ/g, 'و').replace(/ئ/g, 'ي').replace(/[^\p{L}\p{N}]+/gu, '').toLowerCase();
}
function normalizeUrl(value = '') { return String(value).trim().replace(/^http:\/\//iu, 'https://').replace(/\/$/u, ''); }
function classify(title) {
  if (/(تحكيم|تسوية النزاع)/u.test(title)) return 'التحكيم وتسوية المنازعات';
  if (/(قضاء|قاضي|محكم|دعوى|محاكمات|تنفيذ|طعن|إثبات|حكم|سجناء|توقيف|قضائي)/u.test(title)) return 'المحاكم والمرافعات';
  if (/(جنائي|جريمة|عقوب|إرهاب|غسيل الأموال|مخدرات|الحدث الجانح|إعدام|نفي)/u.test(title)) return 'القانون الجنائي';
  if (/(دستور|برلمان|تشريع|إداري|السلطات|سيادة|قرار إداري|إدارة)/u.test(title)) return 'القانون الإداري والدستوري';
  if (/(ضريبة|جمرك|شيك|مصرف|تأمين|تجاري|إفلاس|بيع دولي)/u.test(title)) return 'القانون التجاري والاستثمار';
  if (/(دولي|جنسيات|لوكربي|اتفاقية فيينا)/u.test(title)) return 'القانون الدولي';
  if (/(مدني|عقد|مسؤولية|حيازة|إيجار|التزام|عقار|مستأجر|أسرة|أحوال شخصية|نسب|مدين|الغبن|ملكية|طبيب)/u.test(title)) return 'القانون المدني';
  return 'الأبحاث القانونية والقضائية';
}
const anchors = [...html.matchAll(/<a\b[^>]*href\s*=\s*(["'])(.*?)\1[^>]*>([\s\S]*?)<\/a>/giu)];
const raw = [];
for (const match of anchors) {
  const url = decode(match[2]);
  const title = decode(match[3]).replace(/\s+(?:pdf|docx?|رابط)$/iu, '').trim();
  if (!/dahsha\.com\/viewarticle\.php\?id=\d+/iu.test(url) || !title) continue;
  raw.push({ title, url });
}
const existingTitles = new Map();
const existingUrls = new Map();
for (const item of items) {
  const key = normalizeArabic(item.title);
  if (key && !existingTitles.has(key)) existingTitles.set(key, item.id);
  for (const link of [item.link_direct, item.link_drive, item.link_telegram]) if (link && !existingUrls.has(normalizeUrl(link))) existingUrls.set(normalizeUrl(link), item.id);
}
const fiqhOnly = /^(?:مناط التذرع عند الأصوليين وثمرته|بيان حكم خلو الرجل عند الفقهاء|المواقع الطارئة المسقطة للحد)$/u;
const legalClue = /(قانون|قض|قاضي|قضاء|محكم|دعوى|إثبات|شهادة|عقد|عقوب|جريمة|جنائي|مدني|دستور|تشريع|برلمان|إداري|تحكيم|ضرائب|جمرك|مصرف|تأمين|ملكية|إيجار|إفلاس|محامي|مدين|دائن|سجن|توقيف|جنسيات|اتفاق|تنفيذ|طعن|التزام|حقوق|دولي|شيك|رقابة|مسؤولية|حيازة|مستأجر|أسرة|نسب)/u;
const seenUrls = new Map();
const seenTitles = new Map();
const candidates = [];
const excluded = [];
for (const item of raw) {
  const titleKey = normalizeArabic(item.title);
  const urlKey = normalizeUrl(item.url);
  let reason = '';
  if (fiqhOnly.test(item.title)) reason = 'فقهي عام لا يثبت اتصاله بالقضاء أو النظام القانوني';
  else if (!legalClue.test(item.title)) reason = 'لا تظهر صلة قانونية أو قضائية كافية من العنوان';
  else if (existingTitles.has(titleKey)) reason = `عنوان موجود: ${existingTitles.get(titleKey)}`;
  else if (existingUrls.has(urlKey)) reason = `رابط موجود: ${existingUrls.get(urlKey)}`;
  else if (seenTitles.has(titleKey)) reason = `عنوان مكرر في الصفحة: ${seenTitles.get(titleKey)}`;
  else if (seenUrls.has(urlKey)) reason = `رابط مكرر في الصفحة: ${seenUrls.get(urlKey)}`;
  if (reason) {
    excluded.push({ ...item, reason });
    continue;
  }
  seenTitles.set(titleKey, item.title);
  seenUrls.set(urlKey, item.title);
  candidates.push({
    title: item.title,
    author: '',
    investigator: '',
    publisher: 'كلية الحقوق (المكتبة القانونية)',
    year: '',
    link_telegram: '',
    link_drive: '',
    link_direct: item.url,
    source,
    source_page: sourcePage,
    category: classify(item.title),
    material_type: 'بحث',
    file_type: 'رابط',
    file_size: '',
    pages_count: '',
    is_featured: false,
    download_links_count: 1,
  });
}
const output = { generated_at: new Date().toISOString(), source, source_page: sourcePage, totals: { raw_dahsha_links: raw.length, candidates: candidates.length, excluded: excluded.length }, candidates, excluded };
await fs.writeFile(`${root}/halimloi_legal_candidates.json`, JSON.stringify(output, null, 2));
await fs.writeFile(`${root}/halimloi_legal_candidates.txt`, [
  `المصدر: ${source}`,
  `المقال: ${sourcePage}`,
  `روابط Dahsha المستخرجة: ${output.totals.raw_dahsha_links}`,
  `مرشحات قانونية فريدة: ${output.totals.candidates}`,
  `مستبعدات أولية: ${output.totals.excluded}`,
  '',
  'المرشحات:',
  ...candidates.map((item, index) => `${index + 1}. ${item.title} | ${item.category}\n   ${item.link_direct}`),
  '',
  'المستبعدات:',
  ...excluded.map((item, index) => `${index + 1}. ${item.title} | ${item.reason}`),
].join('\n'));
console.log(JSON.stringify(output.totals));
