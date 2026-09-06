import fs from 'node:fs/promises';

const root = process.cwd();
const sourceUrl = 'https://promahmoud.blogspot.com/';

function decodeHtml(value = '') {
  return value
    .replace(/&nbsp;|&#160;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;|&apos;/gi, "'")
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>')
    .replace(/&#x([\da-f]+);/gi, (_, code) => String.fromCodePoint(parseInt(code, 16)))
    .replace(/&#(\d+);/g, (_, code) => String.fromCodePoint(Number(code)));
}

function htmlText(value = '') {
  return decodeHtml(value.replace(/<[^>]*>/g, ' ')).replace(/\s+/g, ' ').trim();
}

function normalizeTitle(value = '') {
  return value
    .normalize('NFKD')
    .replace(/[\u064B-\u065F\u0670\u0640]/g, '')
    .replace(/[أإآٱ]/g, 'ا')
    .replace(/ى/g, 'ي')
    .replace(/ة/g, 'ه')
    .replace(/[^\p{L}\p{N}]+/gu, '')
    .toLowerCase();
}

function cleanTitle(value = '') {
  return value
    .replace(/\s*(?:د\.؟|دكتور|الأستاذ|استاذ|أ\.د\.|أ\.د|الدكتور)\s*\/?.*$/u, '')
    .replace(/\s+[-–—]\s+(?:مجلة|كلية|جامعة|قسم).*/u, '')
    .replace(/\s+/g, ' ')
    .replace(/^[\s\-–—:؛،]+|[\s\-–—:؛،]+$/g, '')
    .trim();
}

const legalTerms = /(قانون|قضائ|قضاء|محكم|تحكيم|دعوى|دعاوى|مرافع|تشريع|نظام|لائح|عقد|عقود|التزام|حقوق|اثبات|إثبات|جنائ|جريم|عقوب|إدار|دستور|تجار|مدن|منازع|مسؤولي|ملكي|تعويض|ضرر|شرك|استثمار|توقيع|إلكترون|الكترون|مصرف|بنك|عقار|بناء|تشييد|تنفيذ|حكم|أحكام|قاضي|محامي|وساط|تزوير|اختصاص|رقاب|فيـديك|فديك)/u;
const excludedTerms = /(باللغة الإنجليزية|باللغة الانجليزية|كتب قانونية باللغة الفرنسية|La liberté|Droit administratif|Principles of|Corporate Criminal|Philosophy and|Monnaie|Accidental Presidents|International Arbitration|Immunity of the arbitrator|Multiparties|Transforming disputes|Arbitrage,|Le juge Francais|Final Settlement|Procedural aspects|The Determination|JUDICIAL INTERVENTION|Judicial Review|The international arbitration ACT|E-version|Fair Process|PUBLIC POLICY|Essential Judge|The rules of the|Public construction|The vitality|Profit|The partner|Plurality|The liability|Protection of|A civil law|P rotection|The no|Pure economic|Construction rules|The right of|Statutory regulation|The impact|The future|Solving disputes|The resolution|Construction dispute)/iu;

const sourceData = JSON.parse(await fs.readFile(`${root}/items.json`, 'utf8'));
const currentItems = Array.isArray(sourceData) ? sourceData : sourceData.items;
const existingTitles = new Map();
const existingLinks = new Set();
for (const item of currentItems) {
  const key = normalizeTitle(item.title ?? '');
  if (key && !existingTitles.has(key)) existingTitles.set(key, item);
  for (const link of [item.link_direct, item.link_telegram, item.link_drive]) if (link) existingLinks.add(String(link).trim());
}

const response = await fetch(sourceUrl, { headers: { 'user-agent': 'Mozilla/5.0' } });
const html = await response.text();
const rawRows = [];

// Linked list items with their visible title.
const liPattern = /<li\b[^>]*>([\s\S]*?)<\/li>/gi;
let match;
while ((match = liPattern.exec(html))) {
  const fragment = match[1];
  const href = fragment.match(/href\s*=\s*["']([^"']+)["']/i)?.[1];
  if (!href) continue;
  const anchor = fragment.match(/<a\b[^>]*>([\s\S]*?)<\/a>/i)?.[1] ?? fragment;
  rawRows.push({ title: cleanTitle(htmlText(anchor)), href: decodeHtml(href), origin: 'قائمة الموقع' });
}

// Table rows with title in the first cell and a separate empty download-anchor in the second cell.
const trPattern = /<tr\b[^>]*>([\s\S]*?)<\/tr>/gi;
while ((match = trPattern.exec(html))) {
  const fragment = match[1];
  const href = fragment.match(/href\s*=\s*["']([^"']+)["']/i)?.[1];
  if (!href) continue;
  const cells = [...fragment.matchAll(/<t[dh]\b[^>]*>([\s\S]*?)<\/t[dh]>/gi)];
  if (!cells.length) continue;
  const title = cleanTitle(htmlText(cells[0][1]));
  rawRows.push({ title, href: decodeHtml(href), origin: 'جدول الموقع' });
}

const seen = new Set();
const candidates = [];
const excluded = [];
for (const row of rawRows) {
  const title = row.title;
  const href = row.href;
  const key = normalizeTitle(title);
  const isArabic = /[\u0600-\u06FF]/u.test(title);
  const absoluteUrl = new URL(href, sourceUrl).href;
  let reason = '';
  if (!title || title.length < 8) reason = 'عنوان ناقص أو عنصر تنقلي';
  else if (!isArabic) reason = 'عنوان غير عربي';
  else if (excludedTerms.test(title)) reason = 'كتاب أو عنوان بلغة غير عربية';
  else if (!legalTerms.test(title)) reason = 'لا تظهر صلة قانونية أو قضائية كافية';
  else if (seen.has(key)) reason = 'تكرار داخلي للعنوان';
  else if (existingTitles.has(key)) reason = `عنوان موجود: ${existingTitles.get(key).id}`;
  else if (existingLinks.has(absoluteUrl)) reason = 'رابط موجود في المكنز';
  if (reason) {
    excluded.push({ title, url: absoluteUrl, origin: row.origin, reason });
    continue;
  }
  seen.add(key);
  candidates.push({
    title,
    link_direct: absoluteUrl,
    author: 'د. محمود لطفي عبد العزيز',
    publisher: 'مكتبة الدكتور محمود لطفي عبد العزيز القانونية',
    source: 'مكتبة الدكتور محمود لطفي عبد العزيز القانونية',
    category: /تحكيم|منازع/u.test(title) ? 'المحاماة والتحكيم' : /قضائ|قضاء|محكم|دعوى|مرافع|حكم/u.test(title) ? 'المحاكم والمرافعات' : /اثبات|إثبات|توقيع/u.test(title) ? 'الإثبات والشهادة' : /جنائ|جريم|عقوب/u.test(title) ? 'الجنايات والحدود' : /إدار|دستور/u.test(title) ? 'القانون الإداري والدستوري' : /تجار|شرك|بنك|مصرف|عقد|استثمار/u.test(title) ? 'القانون التجاري والاستثمار' : 'الأنظمة والتشريعات',
    material_type: 'بحث',
    file_type: 'رابط',
    file_size: '',
    pages_count: '',
    is_featured: false,
    download_links_count: 1,
    origin: row.origin,
  });
}

const output = {
  generated_at: new Date().toISOString(),
  source_url: sourceUrl,
  totals: { raw_linked_rows: rawRows.length, arabic_legal_new_candidates: candidates.length, excluded_or_existing: excluded.length },
  candidates,
  excluded,
};
await fs.writeFile(`${root}/promahmoud_arabic_legal_candidates.json`, JSON.stringify(output, null, 2));
await fs.writeFile(`${root}/promahmoud_arabic_legal_candidates.txt`, [
  `فحص المواد العربية القانونية من ${sourceUrl}`,
  `صفوف الروابط المستخرجة: ${rawRows.length}`,
  `مرشحات عربية قانونية جديدة: ${candidates.length}`,
  `مستبعد أو موجود: ${excluded.length}`,
  '',
  'المرشحات:',
  ...candidates.map((item, index) => `${index + 1}. ${item.title}\n   الرابط: ${item.link_direct}\n   القسم: ${item.category}`),
  '',
  'المستبعد/الموجود:',
  ...excluded.map((item, index) => `${index + 1}. ${item.title || '[فارغ]'} | ${item.reason}`),
].join('\n'));
console.log(JSON.stringify(output.totals));
