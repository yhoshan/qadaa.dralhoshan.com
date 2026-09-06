import { readFile, writeFile } from 'node:fs/promises';

const root = process.cwd();
const norm = (value = '') => String(value).normalize('NFKD').replace(/[\u064B-\u065F\u0670]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي').toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');
const cat = (title, source) => {
  if (source === 'مكتبة فلسفة القانون' || /فلسف|نظريه القانون|قانون والحق|مدرسه.*قانون|منطق قانوني/.test(title)) return 'فلسفة القانون ونظرية الدولة';
  if (/نظام|لائح|مرسوم|تشريع|تعاميم/.test(title)) return 'الأنظمة والتشريعات';
  if (/محكم|قضاء|قاضي|دعوى|مراف|تنفيذ|اثبات|بينه|شهاد/.test(title)) return 'المحاكم والمرافعات';
  if (/محام|تحكيم|وساط/.test(title)) return 'المحاماة والتحكيم';
  if (/جريم|عقوب|جنا|سجن|نياب|تحقيق|توقيف/.test(title)) return 'القانون الجنائي';
  if (/عقد|التزام|عقار|ايجار|تجار|شرك|افلاس|شيك|تأمين/.test(title)) return 'المعاملات والالتزامات';
  if (/احوال|طلاق|خلع|حضان|نفق|تركات|مواريث/.test(title)) return 'الأحوال الشخصية';
  return 'القضاء والأنظمة والمحاماة';
};
const group = (category = '') => category === 'الأنظمة والتشريعات' ? 'nizam' : /محام|تحكيم/.test(category) ? 'mohama' : /محكم|قضاء|جنائي|إجراء|اثبات|عدال/.test(category) ? 'qadaa' : 'other';
const countBy = (rows, key) => Object.fromEntries([...rows.reduce((m, x) => m.set(x[key] || 'غير محدد', (m.get(x[key] || 'غير محدد') || 0) + 1), new Map()).entries()].sort((a, b) => b[1] - a[1]));
const raw = JSON.parse(await readFile(`${root}/items.json`, 'utf8'));
const items = Array.isArray(raw) ? raw : raw.items;
const analysis = JSON.parse(await readFile(`${root}/new_legal_channels_analysis.json`, 'utf8'));
const existing = new Set(items.map(item => norm(item.title)));
let philId = Math.max(0, ...items.map(i => Number((/^philosophy_law_(\d+)$/.exec(i.id || '') || [])[1] || 0))) + 1;
let legalId = Math.max(0, ...items.map(i => Number((/^iirmll_title_(\d+)$/.exec(i.id || '') || [])[1] || 0))) + 1;
const added = [];
for (const candidate of analysis.candidates) {
  const key = norm(candidate.title);
  if (existing.has(key)) continue;
  const isPhil = candidate.source === 'مكتبة فلسفة القانون';
  const record = {
    id: isPhil ? `philosophy_law_${String(philId++).padStart(3, '0')}` : `iirmll_title_${String(legalId++).padStart(3, '0')}`,
    title: candidate.title,
    author: '', investigator: '',
    publisher: candidate.source,
    year: candidate.date ? String(candidate.date).slice(0, 4) : '',
    link_telegram: '', link_drive: '', link_direct: '',
    source: candidate.source,
    category: cat(candidate.title, candidate.source),
    material_type: 'عنوان مرجعي',
    file_type: 'عنوان', file_size: '', pages_count: '',
    is_featured: false, download_links_count: 0,
  };
  items.push(record); added.push(record); existing.add(key);
}
if (!added.length) throw new Error('لا توجد عناوين جديدة لإضافتها.');
const previousStats = JSON.parse(await readFile(`${root}/stats.json`, 'utf8'));
const buckets = items.reduce((sum, item) => (sum[group(item.category)] += 1, sum), { qadaa: 0, nizam: 0, mohama: 0, other: 0 });
const stats = { ...previousStats, total_items: items.length, books_count: items.length, qadaa_count: buckets.qadaa, nizam_count: buckets.nizam, mohama_count: buckets.mohama, other_count: buckets.other, audio_count: items.filter(x => x.file_type === 'MP3').length, video_count: items.filter(x => x.file_type === 'MP4' || x.file_type === 'فيديو').length, categories: countBy(items, 'category'), sources: countBy(items, 'source'), file_types: countBy(items, 'file_type'), featured_count: items.filter(x => x.is_featured).length, with_download_links: items.filter(x => Number(x.download_links_count || 0) > 0).length };
const output = Array.isArray(raw) ? items : { ...raw, items };
for (const [file, content] of [[`${root}/items.json`, output], [`${root}/client/public/items.json`, output], [`${root}/stats.json`, stats], [`${root}/client/public/stats.json`, stats]]) await writeFile(file, `${JSON.stringify(content, null, 2)}\n`);
const hook = `${root}/client/src/hooks/useItems.ts`, code = await readFile(hook, 'utf8'), tag = 'philosophy-iirmll-titles-719-2026-09-06';
await writeFile(hook, code.replace(/items\.json\?v=[^`]+/g, `items.json?v=${tag}`).replace(/stats\.json\?v=[^`]+/g, `stats.json?v=${tag}`));
const bySource = countBy(added, 'source');
await writeFile(`${root}/new_legal_channels_title_additions_execution.json`, `${JSON.stringify({ previous_total: items.length - added.length, added_count: added.length, total: items.length, additions_by_source: bySource, first_id: added[0].id, last_id: added.at(-1).id, added }, null, 2)}\n`);
console.log(JSON.stringify({ previous_total: items.length - added.length, added: added.length, total: items.length, additions_by_source: bySource, first_id: added[0].id, last_id: added.at(-1).id }, null, 2));
