import fs from 'node:fs';
import path from 'node:path';

const root = '/home/ubuntu/makanez-qadaa';
const unwrap = (data) => Array.isArray(data) ? { items: data, array: true } : { items: data.items || [], array: false, original: data };
const rewrap = (state) => state.array ? state.items : { ...state.original, items: state.items };
const normalize = (value = '') => String(value).normalize('NFKD').replace(/[\u064B-\u065F\u0670\u0640]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه').replace(/[\p{P}\p{S}\s_]/gu, '').toLowerCase();
const countBy = (items, selector) => Object.fromEntries([...items.reduce((map, item) => { const key = selector(item) || 'غير مصنف'; map.set(key, (map.get(key) || 0) + 1); return map; }, new Map()).entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], 'ar')));
const categoryFor = (title) => {
  if (/(?:تحكيم|وساطة|محام|محامي|محاماة)/iu.test(title)) return 'المحاماة والتحكيم';
  if (/(?:قضاء|قضائي|قاضي|محكمة|محاكم|دعوى|مرافعات|إثبات|اثبات|إقرار|شهادة|حكم قضائي)/iu.test(title)) return 'المحاكم والمرافعات';
  if (/(?:جريمة|جرائم|جنائي|جزائي|عقوبة|عقوبات|ادعاء عام|غسل الأموال)/iu.test(title)) return 'القانون الجنائي';
  if (/(?:دستور|دستوري|حريات|حقوق الإنسان|حقوق الانسان|جنسية)/iu.test(title)) return 'القانون الدستوري';
  if (/(?:إداري|اداري|إدارة عامة|قرار إداري|قرار اداري|ضبط إداري|ضبط اداري)/iu.test(title)) return 'القانون الإداري';
  if (/(?:تجاري|شركة|شركات|أسهم|افلاس|إفلاس|مصرف|بنك|تأمين|مزايدات)/iu.test(title)) return 'القانون التجاري';
  if (/(?:دولي|الأمم المتحدة|الامم المتحدة|نزاع مسلح|منظمة التجارة)/iu.test(title)) return 'القانون الدولي';
  if (/(?:أحوال شخصية|احوال شخصية|زواج|طلاق|نسب|وصاية|وصي|أسرة|اسرة)/iu.test(title)) return 'الأحوال الشخصية';
  if (/(?:عقد|عقود|التزام|التزامات|مسؤولية|تعويض|أجنبي|اجنبي|ملكية|أراضي|اراضي|رهن)/iu.test(title)) return 'القانون المدني';
  if (/(?:عمل|عمال|عامل|موظف|وظيفة)/iu.test(title)) return 'القانون العمالي';
  return 'الأبحاث القانونية والقضائية';
};
const bucket = (category) => /محاماة|تحكيم/.test(category) ? 'mohama' : /محاكم|قضاء|جنائي|إثبات/.test(category) ? 'qadaa' : /قانون|أنظمة|تشريع/.test(category) ? 'nizam' : 'other';

const analysis = JSON.parse(fs.readFileSync(path.join(root, 'nomass_suwaid_channels_analysis.json'), 'utf8'));
const state = unwrap(JSON.parse(fs.readFileSync(path.join(root, 'items.json'), 'utf8')));
const titles = new Set(state.items.map((item) => normalize(item.title)).filter(Boolean));
const ids = new Set(state.items.map((item) => item.id).filter(Boolean));
const next = { nomass: 1, suwaid: 1 };
for (const id of ids) {
  const match = String(id).match(/^(nomass_title|suwaid_title)_(\d+)$/);
  if (match) next[match[1].startsWith('nomass') ? 'nomass' : 'suwaid'] = Math.max(next[match[1].startsWith('nomass') ? 'nomass' : 'suwaid'], Number(match[2]) + 1);
}
const additions = [];
const exclusions = [];
for (const candidate of analysis.candidates) {
  const key = normalize(candidate.title);
  if (!key || titles.has(key)) { exclusions.push({ title: candidate.title, reason: 'تكرار في فحص الإدخال النهائي' }); continue; }
  const sourceKey = candidate.input_source === 'nomass' ? 'nomass' : 'suwaid';
  let id = `${sourceKey}_title_${String(next[sourceKey]++).padStart(3, '0')}`;
  while (ids.has(id)) id = `${sourceKey}_title_${String(next[sourceKey]++).padStart(3, '0')}`;
  ids.add(id); titles.add(key);
  const category = categoryFor(candidate.title);
  additions.push({ id, title: candidate.title, author: '', investigator: '', link_telegram: '', link_drive: '', link_direct: '', source: candidate.channel, publisher: candidate.channel, category, material_type: 'عنوان مرجعي', file_type: 'عنوان', file_size: '', pages_count: '', is_featured: false, download_links_count: 0, note: 'إحالة بعنوان المادة واسم القناة فقط؛ لا يتضمن التصدير رابط فتح مباشر أو الملف نفسه.' });
}
if (!additions.length) throw new Error('لا توجد عناوين جديدة للإدخال بعد منع التكرار النهائي.');
const before = state.items.length;
state.items.push(...additions);
const output = JSON.stringify(rewrap(state), null, 2) + '\n';
fs.writeFileSync(path.join(root, 'items.json'), output);
fs.writeFileSync(path.join(root, 'client/public/items.json'), output);
const stats = JSON.parse(fs.readFileSync(path.join(root, 'stats.json'), 'utf8'));
const changes = { qadaa: 0, nizam: 0, mohama: 0, other: 0 };
for (const item of additions) changes[bucket(item.category)] += 1;
stats.total_items = state.items.length;
stats.books_count = state.items.length;
stats.qadaa_count = (stats.qadaa_count || 0) + changes.qadaa;
stats.nizam_count = (stats.nizam_count || 0) + changes.nizam;
stats.mohama_count = (stats.mohama_count || 0) + changes.mohama;
stats.other_count = state.items.length - stats.qadaa_count - stats.nizam_count - stats.mohama_count;
stats.categories = countBy(state.items, (item) => item.category);
stats.sources = countBy(state.items, (item) => item.source);
stats.file_types = countBy(state.items, (item) => item.file_type);
stats.with_download_links = state.items.filter((item) => Number(item.download_links_count || 0) > 0).length;
stats.featured_count = state.items.filter((item) => item.is_featured).length;
const statOutput = JSON.stringify(stats, null, 2) + '\n';
fs.writeFileSync(path.join(root, 'stats.json'), statOutput);
fs.writeFileSync(path.join(root, 'client/public/stats.json'), statOutput);
const hookPath = path.join(root, 'client/src/hooks/useItems.ts');
fs.writeFileSync(hookPath, fs.readFileSync(hookPath, 'utf8').replace(/cacheBust=[^"'`\s&]+/g, `cacheBust=nomass-suwaid-title-additions-${additions.length}-2026-09-06`));
const result = { executed_at: new Date().toISOString(), before_total: before, added: additions.length, after_total: state.items.length, source_counts: countBy(additions, (item) => item.source), category_counts: countBy(additions, (item) => item.category), bucket_changes: changes, final_exclusions: exclusions, added_ids: additions.map((item) => item.id) };
fs.writeFileSync(path.join(root, 'nomass_suwaid_title_additions_execution.json'), JSON.stringify(result, null, 2));
fs.writeFileSync(path.join(root, 'nomass_suwaid_title_additions_manifest.txt'), additions.map((item) => `${item.id}\t${item.source}\t${item.category}\t${item.title}`).join('\n') + '\n');
console.log(JSON.stringify({ before, added: additions.length, after: state.items.length, source_counts: result.source_counts, exclusions: exclusions.length }, null, 2));
