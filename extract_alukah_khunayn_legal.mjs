import fs from 'node:fs/promises';

const root = process.cwd();
const pages = [
  ['بحوث في القضاء', 'https://www.alukah.net/Web/khunayn/11945/'],
  ['بحوث في التحقيق', 'https://www.alukah.net/Web/khunayn/11947/'],
  ['بحوث في الأنظمة السعودية', 'https://www.alukah.net/Web/khunayn/11949/'],
  ['أحكام قضائية', 'https://www.alukah.net/Web/khunayn/11954/'],
  ['شرح مواد من نظام المرافعات الشرعية', 'https://www.alukah.net/Web/khunayn/11955/'],
  ['شرح مواد من نظام المرافعات الشرعية', 'https://www.alukah.net/Web/khunayn/11956/'],
];

const directArticle = {
  section: 'مقالات',
  title: 'المرافعة عن بعد',
  url: 'https://www.alukah.net/web/khunayn/0/140206/%d8%a7%d9%84%d9%85%d8%b1%d8%a7%d9%81%d8%b9%d8%a9-%d8%b9%d9%86-%d8%a8%d8%b9%d8%af/',
};

function decodeHtml(value = '') {
  return value
    .replace(/&nbsp;|&#160;/gi, ' ')
    .replace(/&amp;/gi, '&')
    .replace(/&quot;/gi, '"')
    .replace(/&#39;|&apos;/gi, "'")
    .replace(/&lt;/gi, '<')
    .replace(/&gt;/gi, '>')
    .replace(/&#(\\d+);/g, (_, code) => String.fromCodePoint(Number(code)))
    .replace(/&#x([\da-f]+);/gi, (_, code) => String.fromCodePoint(parseInt(code, 16)));
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
    .replace(/[\u200c\u200d]/g, '')
    .replace(/[^\p{L}\p{N}]+/gu, '')
    .toLowerCase();
}

function cleanTitle(title = '') {
  return title
    .replace(/\s*\(\s*PDF\s*\)(?:\s*\(\s*PDF\s*\))?/giu, '')
    .replace(/\s*\(\s*WORD\s*\)/giu, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function unwrap(data) {
  return Array.isArray(data) ? data : (data.items ?? []);
}

const rawItems = JSON.parse(await fs.readFile(`${root}/items.json`, 'utf8'));
const currentItems = unwrap(rawItems);
const existingTitleKeys = new Map();
const existingLinks = new Set();
for (const item of currentItems) {
  const key = normalizeTitle(item.title ?? '');
  if (key && !existingTitleKeys.has(key)) existingTitleKeys.set(key, item);
  for (const link of [item.link_direct, item.link_telegram, item.link_drive]) {
    if (typeof link === 'string' && link) existingLinks.add(link.trim());
  }
}

const extracted = [directArticle];
for (const [section, pageUrl] of pages) {
  const response = await fetch(pageUrl, { headers: { 'user-agent': 'Mozilla/5.0' } });
  const html = await response.text();
  const anchorRegex = /<a\b([^>]*)\bhref\s*=\s*["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi;
  let match;
  while ((match = anchorRegex.exec(html))) {
    const href = decodeHtml(match[2]);
    const title = cleanTitle(htmlText(match[3]));
    if (!title || !href || !/khunayn/i.test(href)) continue;
    if (/RSS|الصفحة|عودة|السيرة|موقع الشيخ/i.test(title)) continue;
    extracted.push({
      section,
      title,
      url: new URL(href, pageUrl).href,
    });
  }
}

const seen = new Set();
const candidates = [];
const duplicates = [];
for (const row of extracted) {
  const key = normalizeTitle(row.title);
  if (!key || seen.has(key)) continue;
  seen.add(key);
  const titleMatch = existingTitleKeys.get(key);
  const linkMatch = existingLinks.has(row.url);
  const enriched = {
    title: row.title,
    link_direct: row.url,
    author: 'الشيخ عبدالله بن محمد بن سعد آل خنين',
    publisher: 'شبكة الألوكة',
    source: 'شبكة الألوكة',
    category: row.section.includes('التحقيق') ? 'التحقيق الجنائي' : row.section.includes('الأنظمة') ? 'الأنظمة السعودية' : row.section.includes('أحكام') ? 'أحكام قضائية' : row.section.includes('مرافعات') ? 'المحاكم والمرافعات' : 'القضاء الشرعي',
    material_type: row.title.includes('PDF') ? 'بحث' : 'مقال',
    file_type: 'رابط',
    file_size: '',
    pages_count: '',
    is_featured: false,
    download_links_count: 1,
    origin_section: row.section,
    title_match_id: titleMatch?.id ?? null,
    title_match_source: titleMatch?.source ?? null,
    link_match: linkMatch,
  };
  (titleMatch || linkMatch ? duplicates : candidates).push(enriched);
}

const output = {
  generated_at: new Date().toISOString(),
  source_page: 'https://www.alukah.net/authors/view/home/4179/',
  totals: { extracted_unique_titles: seen.size, new_candidates: candidates.length, existing_or_duplicate: duplicates.length },
  candidates,
  duplicates,
};
await fs.writeFile(`${root}/alukah_khunayn_legal_candidates.json`, JSON.stringify(output, null, 2));
await fs.writeFile(`${root}/alukah_khunayn_legal_candidates.txt`, [
  `تقرير مرشحات الشيخ عبدالله آل خنين من الألوكة: ${output.generated_at}`,
  `العناوين الفريدة المستخرجة: ${seen.size}`,
  `المرشحات الجديدة: ${candidates.length}`,
  `المكررات أو الموجود سابقاً: ${duplicates.length}`,
  '',
  'المرشحات الجديدة:',
  ...candidates.map((item, index) => `${index + 1}. ${item.title}\n   القسم: ${item.origin_section}\n   الرابط: ${item.link_direct}`),
  '',
  'الموجود أو المكرر:',
  ...duplicates.map((item, index) => `${index + 1}. ${item.title}\n   السجل القائم: ${item.title_match_id ?? 'مطابقة رابط'} | المصدر: ${item.title_match_source ?? ''}`),
].join('\n'));

console.log(JSON.stringify(output.totals));
