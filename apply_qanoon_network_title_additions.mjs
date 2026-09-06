import fs from 'node:fs';
import path from 'node:path';

const root = '/home/ubuntu/makanez-qadaa';
const unwrap = (data) => Array.isArray(data) ? { items: data, wrapper: 'array' } : { items: data.items || [], wrapper: 'object', original: data };
const rewrap = ({ items, wrapper, original }) => wrapper === 'array' ? items : { ...original, items };
const normalize = (value = '') => String(value)
  .normalize('NFKD')
  .replace(/[\u064B-\u065F\u0670\u0640]/g, '')
  .replace(/[أإآٱ]/g, 'ا')
  .replace(/ى/g, 'ي')
  .replace(/ة/g, 'ه')
  .replace(/[\p{P}\p{S}\s_]/gu, '')
  .toLowerCase();
const countBy = (items, selector) => Object.fromEntries([...items.reduce((map, item) => {
  const key = selector(item) || 'غير مصنف';
  map.set(key, (map.get(key) || 0) + 1);
  return map;
}, new Map()).entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], 'ar')));
const categoryFor = (title) => {
  const text = title || '';
  if (/(?:تحكيم|وساطة|محام|محامي|محاماة)/iu.test(text)) return 'المحاماة والتحكيم';
  if (/(?:قضاء|قضائي|قاضي|محكمة|محاكم|دعوى|مرافعات|إثبات|اثبات|إقرار|شهادة)/iu.test(text)) return 'المحاكم والمرافعات';
  if (/(?:جريمة|جرائم|جنائي|جزائي|عقوبة|عقوبات|إعدام|قتل|إبادة|ادعاء عام)/iu.test(text)) return 'القانون الجنائي';
  if (/(?:دستور|دستوري|حريات|حقوق الإنسان|حقوق الانسان|جنسية)/iu.test(text)) return 'القانون الدستوري';
  if (/(?:إداري|اداري|إدارة عامة|قرار إداري|قرار اداري|ضبط إداري|ضبط اداري)/iu.test(text)) return 'القانون الإداري';
  if (/(?:تجاري|شركة|شركات|أسهم|افلاس|إفلاس|مصرف|بنك|تأمين|مزايدات)/iu.test(text)) return 'القانون التجاري';
  if (/(?:دولي|الأمم المتحدة|الامم المتحدة|نزاع مسلح|منظمة التجارة)/iu.test(text)) return 'القانون الدولي';
  if (/(?:أحوال شخصية|احوال شخصية|زواج|طلاق|نسب|وصاية|وصي|أسرة|اسرة)/iu.test(text)) return 'الأحوال الشخصية';
  if (/(?:عقد|عقود|التزام|التزامات|مسؤولية|تعويض|أجنبي|اجنبي|ملكية|أراضي|اراضي)/iu.test(text)) return 'القانون المدني';
  return 'الأبحاث القانونية والقضائية';
};
const mainBucket = (category) => {
  if (/محاماة|تحكيم/.test(category)) return 'mohama';
  if (/محاكم|قضاء|جنائي|جنايات|إثبات/.test(category)) return 'qadaa';
  if (/قانون|أنظمة|تشريع/.test(category)) return 'nizam';
  return 'other';
};

const candidateData = JSON.parse(fs.readFileSync(path.join(root, 'qanoon_network_channels_analysis.json'), 'utf8'));
const itemData = unwrap(JSON.parse(fs.readFileSync(path.join(root, 'items.json'), 'utf8')));
const existingTitles = new Set(itemData.items.map((item) => normalize(item.title)).filter(Boolean));
const existingIds = new Set(itemData.items.map((item) => item.id).filter(Boolean));
const candidateSeen = new Set();
const additions = [];
const exclusions = [];

for (const candidate of candidateData.candidates) {
  const key = normalize(candidate.title);
  if (!key || existingTitles.has(key) || candidateSeen.has(key)) {
    exclusions.push({ title: candidate.title, reason: 'ظهر مكرراً في فحص الإدخال النهائي' });
    continue;
  }
  candidateSeen.add(key);
  const baseId = candidate.input_source === 'theses' ? 'qanoon_theses' : 'qanoon_network';
  let index = additions.filter((item) => item.id.startsWith(baseId + '_')).length + 1;
  let id = `${baseId}_${String(index).padStart(3, '0')}`;
  while (existingIds.has(id)) { index += 1; id = `${baseId}_${String(index).padStart(3, '0')}`; }
  existingIds.add(id);
  existingTitles.add(key);
  const category = categoryFor(candidate.title);
  additions.push({
    id,
    title: candidate.title,
    author: candidate.author || '',
    investigator: '',
    link_telegram: '',
    link_drive: '',
    link_direct: '',
    source: candidate.channel,
    publisher: candidate.channel,
    category,
    material_type: candidate.input_source === 'theses' ? 'رسالة علمية' : 'عنوان مرجعي',
    file_type: 'عنوان',
    file_size: '',
    pages_count: '',
    is_featured: false,
    download_links_count: 0,
    note: 'إحالة بعنوان المادة واسم القناة فقط؛ لا يتضمن التصدير رابط فتح مباشر أو الملف نفسه.',
  });
}

if (additions.length === 0) throw new Error('لم يبق أي سجل جديد صالح للإضافة بعد فحص الإدخال النهائي.');
const before = itemData.items.length;
itemData.items.push(...additions);
fs.writeFileSync(path.join(root, 'items.json'), JSON.stringify(rewrap(itemData), null, 2) + '\n');
fs.writeFileSync(path.join(root, 'client/public/items.json'), JSON.stringify(rewrap(itemData), null, 2) + '\n');

const statsPath = path.join(root, 'stats.json');
const stats = JSON.parse(fs.readFileSync(statsPath, 'utf8'));
const delta = { qadaa: 0, nizam: 0, mohama: 0, other: 0 };
for (const item of additions) delta[mainBucket(item.category)] += 1;
stats.total_items = itemData.items.length;
stats.books_count = itemData.items.length;
stats.qadaa_count = (stats.qadaa_count || 0) + delta.qadaa;
stats.nizam_count = (stats.nizam_count || 0) + delta.nizam;
stats.mohama_count = (stats.mohama_count || 0) + delta.mohama;
stats.other_count = itemData.items.length - stats.qadaa_count - stats.nizam_count - stats.mohama_count;
stats.categories = countBy(itemData.items, (item) => item.category);
stats.sources = countBy(itemData.items, (item) => item.source);
stats.file_types = countBy(itemData.items, (item) => item.file_type);
stats.with_download_links = itemData.items.filter((item) => Number(item.download_links_count || 0) > 0).length;
stats.featured_count = itemData.items.filter((item) => item.is_featured).length;
fs.writeFileSync(statsPath, JSON.stringify(stats, null, 2) + '\n');
fs.writeFileSync(path.join(root, 'client/public/stats.json'), JSON.stringify(stats, null, 2) + '\n');

const hookPath = path.join(root, 'client/src/hooks/useItems.ts');
const hook = fs.readFileSync(hookPath, 'utf8').replace(/cacheBust=[^"'`\s&]+/g, 'cacheBust=qanoon-network-title-additions-' + additions.length + '-2026-09-06');
fs.writeFileSync(hookPath, hook);

const execution = {
  executed_at: new Date().toISOString(),
  before_total: before,
  added: additions.length,
  after_total: itemData.items.length,
  source_counts: countBy(additions, (item) => item.source),
  category_counts: countBy(additions, (item) => item.category),
  bucket_delta: delta,
  final_input_exclusions: exclusions,
  added_ids: additions.map((item) => item.id),
};
fs.writeFileSync(path.join(root, 'qanoon_network_title_additions_execution.json'), JSON.stringify(execution, null, 2));
fs.writeFileSync(path.join(root, 'qanoon_network_title_additions_manifest.txt'), additions.map((item) => `${item.id}\t${item.material_type}\t${item.source}\t${item.title}`).join('\n') + '\n');
console.log(JSON.stringify({ before, added: additions.length, after: itemData.items.length, source_counts: execution.source_counts, exclusions: exclusions.length }, null, 2));
