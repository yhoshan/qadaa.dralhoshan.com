import fs from 'node:fs/promises';

const root = process.cwd();
const pageUrl = 'https://www.m2r3.com/book/';
const html = await fs.readFile('/home/ubuntu/browser_html/m2r3_com_book_1788690930539.html', 'utf8');
const data = JSON.parse(await fs.readFile(`${root}/items.json`, 'utf8'));
const items = Array.isArray(data) ? data : data.items;

function decode(value = '') {
  return value
    .replace(/&nbsp;|&#160;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;|&apos;/gi, "'")
    .replace(/&#x([\da-f]+);/gi, (_, code) => String.fromCodePoint(parseInt(code, 16)))
    .replace(/&#(\d+);/g, (_, code) => String.fromCodePoint(Number(code)));
}
function text(value = '') { return decode(value.replace(/<[^>]*>/g, ' ')).replace(/\s+/g, ' ').trim(); }
function normalize(value = '') {
  return value.normalize('NFKD').replace(/[\u064B-\u065F\u0670\u0640]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه').replace(/[^\p{L}\p{N}]+/gu, '').toLowerCase();
}
function titleClean(value = '') {
  return value.replace(/\s*\(\s*\d+\s*(?:حقق|نظم)\s*\)\s*$/u, '').replace(/\s+/g, ' ').trim();
}
const legal = /(قانون|قضائ|قضاء|محكم|تحكيم|دعوى|مرافع|نظام|لائح|عقد|عقود|التزام|حقوق|اثبات|إثبات|جنائ|جريم|عقوب|إدار|دستور|تجار|مدن|منازع|مسؤولي|ملكي|تعويض|ضرر|شرك|استثمار|مصرف|بنك|عقار|تنفيذ|حكم|أحكام|قاضي|محامي|وساط|تزوير|إفلاس|افلاس|ضريب|زكاة|بحري|جوي|تأمين)/u;
const reject = /(أصول الفقه|القواعد الفقهية|المدخل إلى الفقه الإسلامي|نموذج أسئلة)/u;
const existingTitles = new Map();
const existingLinks = new Set();
for (const item of items) {
  const key = normalize(item.title ?? '');
  if (key && !existingTitles.has(key)) existingTitles.set(key, item);
  for (const link of [item.link_direct, item.link_telegram, item.link_drive]) if (link) existingLinks.add(String(link).trim());
}

const anchors = [...html.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a>/gi)];
const raw = [];
for (const match of anchors) {
  const href = match[1].match(/href\s*=\s*["']([^"']+)["']/i)?.[1];
  const title = titleClean(text(match[2]));
  if (!href || !title) continue;
  const url = new URL(decode(href), pageUrl).href;
  if (!/\/book-\d+\.html(?:$|[?#])/i.test(url) && !/[?&]s=book(?:&|$)/.test(url) && !/[?&]id=\d+/.test(url)) continue;
  raw.push({ title, url });
}

const seen = new Set();
const candidates = [];
const excluded = [];
for (const row of raw) {
  const key = normalize(row.title);
  let reason = '';
  if (!/[\u0600-\u06FF]/u.test(row.title)) reason = 'عنوان غير عربي';
  else if (reject.test(row.title)) reason = 'ملخص أو نموذج خارج النطاق القانوني المباشر';
  else if (!legal.test(row.title)) reason = 'لا تظهر صلة قانونية أو قضائية كافية';
  else if (seen.has(key)) reason = 'تكرار داخلي';
  else if (existingTitles.has(key)) reason = `عنوان موجود: ${existingTitles.get(key).id}`;
  else if (existingLinks.has(row.url)) reason = 'رابط موجود';
  if (reason) {
    excluded.push({ ...row, reason });
    continue;
  }
  seen.add(key);
  candidates.push({
    ...row,
    author: '',
    investigator: '',
    publisher: 'شبكة مكتبة القانون',
    source: 'شبكة مكتبة القانون',
    category: /قضائ|قضاء|مرافع|تنفيذ|دعوى|حكم/u.test(row.title) ? 'المحاكم والمرافعات' : /جنائ|جريم|عقوب/u.test(row.title) ? 'الجنايات والحدود' : /إدار|دستور/u.test(row.title) ? 'القانون الإداري والدستوري' : /تجار|شرك|إفلاس|افلاس|بنك|مصرف|عقد|ضريب|زكاة/u.test(row.title) ? 'القانون التجاري والاستثمار' : /ملكي|ملكية|حقوق|اثبات|إثبات/u.test(row.title) ? 'الإثبات والشهادة' : 'الأنظمة والتشريعات',
    material_type: /مذكرة/u.test(row.title) ? 'ملخص' : 'ملخص',
    file_type: 'رابط',
    file_size: '',
    pages_count: '',
    is_featured: false,
    download_links_count: 1,
  });
}
const result = { generated_at: new Date().toISOString(), source_url: pageUrl, totals: { raw_book_links: raw.length, candidates: candidates.length, excluded: excluded.length }, candidates, excluded };
await fs.writeFile(`${root}/marqoom_legal_candidates.json`, JSON.stringify(result, null, 2));
await fs.writeFile(`${root}/marqoom_legal_candidates.txt`, [
  `استخراج المواد القانونية من موقع مرقوم: ${pageUrl}`,
  `روابط الكتب المستخرجة: ${raw.length}`,
  `مرشحات قانونية عربية جديدة: ${candidates.length}`,
  `مستبعد أو موجود: ${excluded.length}`,
  '',
  'المرشحات:',
  ...candidates.map((item, index) => `${index + 1}. ${item.title}\n   ${item.url}\n   ${item.category}`),
  '',
  'المستبعد أو الموجود:',
  ...excluded.map((item, index) => `${index + 1}. ${item.title} | ${item.reason}`),
].join('\n'));
console.log(JSON.stringify(result.totals));
