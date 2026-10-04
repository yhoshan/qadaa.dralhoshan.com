import fs from 'node:fs/promises';

const root = process.cwd();
const itemPaths = [`${root}/items.json`, `${root}/client/public/items.json`];
const statsPaths = [`${root}/stats.json`, `${root}/client/public/stats.json`];

// يبقى التقسيم حصريًا: المحاماة المهنية أولاً، ثم القضاء، ثم الأنظمة.
// لا تُعدّل هذه القاعدة الحقول الأصلية للمواد؛ إنما تعيد توزيع بطاقات Hero فقط.
const PRACTICE_CATEGORY = /(القانون المدني|العقاري|القانون التجاري|المالي|الأحوال الشخصية|الأسرة|المعاملات|التزامات|العقود|الشركات|الحوكمة|الإفلاس|العمالي|قانون العمل|أنظمة العمل|الملكية الفكرية|التأمين|المنافسات|القانون الإداري|قانون إداري|القانون الدستوري|قانون دستوري|الضرائب|الزكاة|الجمارك|الأوراق التجارية)/u;
const PRACTICE_TITLE = /(صحيفة\s*(دعوى|استئناف|اعتراض)|لائحة\s*(دعوى|اعتراض)|مذكرة\s*(جواب|دفاع|قانونية|اعتراض)|صياغة\s*(العقود|عقد|قانونية)|نموذج\s*(عقد|دعوى|مذكرة|لائحة|وكالة)|أتعاب\s*المحام|مسؤولية\s*المحام|مهنة\s*المحام|وكالة\s*(شرعية|قانونية)|عقد\s*(تجاري|عمل|ايجار|إيجار|مقاولة|وكالة)|تصفية\s*الشركات|حوكمة\s*الشركات|إفلاس|تنفيذ\s*(الأحكام|السندات|العقود)|الملكية\s*الفكرية|علامة\s*تجارية|براءة\s*اختراع|منافسات\s*(ومشتريات|حكومية)|تأمين\s*(ضد|تعاوني|مسؤولية)|ضريبة|جمرك|زكاة)/u;
const PRACTICE_EXPLICIT_TITLE = /(محام|تحكيم|وساط)/u;

function baseHeroGroup(category = '') {
  if (/(محام|تحكيم|وساط)/u.test(category)) return 'mohama';
  if (/(قضاء|قضائي|محكم|مرافع|إثبات|جنا|جزائي|حسبة|مظالم|أحكام|إجراء.*قضائي|قرار.*قضائي)/u.test(category)) return 'qadaa';
  return 'nizam';
}

function heroClassification(item) {
  const category = String(item.category || '');
  const title = String(item.title || '');
  const baseGroup = baseHeroGroup(category);

  // لا ننقل مواد القضاء أو المحاماة القائمة؛ النقل من الأنظمة فقط.
  if (baseGroup !== 'nizam') return { group: baseGroup, migrated: false, reason: null };
  if (PRACTICE_CATEGORY.test(category)) return { group: 'mohama', migrated: true, reason: 'تصنيف موضوعي للممارسة القانونية' };
  if (PRACTICE_TITLE.test(title)) return { group: 'mohama', migrated: true, reason: 'عنوان عملي مباشر للممارسة القانونية' };
  if (PRACTICE_EXPLICIT_TITLE.test(title)) return { group: 'mohama', migrated: true, reason: 'عنوان صريح في المحاماة أو التحكيم أو الوساطة' };
  return { group: 'nizam', migrated: false, reason: null };
}

const mainContainer = JSON.parse(await fs.readFile(itemPaths[0], 'utf8'));
const items = Array.isArray(mainContainer) ? mainContainer : mainContainer.items;
if (!Array.isArray(items)) throw new Error('بنية items.json غير متوقعة');

const auditReasons = {};
const counts = items.reduce((acc, item) => {
  const classification = heroClassification(item);
  acc[classification.group] += 1;
  if (classification.migrated) auditReasons[classification.reason] = (auditReasons[classification.reason] || 0) + 1;
  return acc;
}, { qadaa: 0, nizam: 0, mohama: 0 });

if (counts.qadaa + counts.nizam + counts.mohama !== items.length) throw new Error('لا تطابق أرقام بطاقات الإحصاء إجمالي المواد');
for (const path of statsPaths) {
  const stats = JSON.parse(await fs.readFile(path, 'utf8'));
  stats.qadaa_count = counts.qadaa;
  stats.nizam_count = counts.nizam;
  stats.mohama_count = counts.mohama;
  await fs.writeFile(path, JSON.stringify(stats, null, 2) + '\n');
}

const audit = {
  generated_at: new Date().toISOString(),
  total_items: items.length,
  qadaa_count: counts.qadaa,
  nizam_count: counts.nizam,
  mohama_count: counts.mohama,
  migrated_from_base_nizam: Object.values(auditReasons).reduce((sum, value) => sum + value, 0),
  migrated_by_reason: auditReasons,
  rule: 'مواد المحاماة والتحكيم والوساطة أولاً، ثم مواد الممارسة القانونية المدنية والتجارية والعقارية والأسرية والعمالية والإدارية وما شابهها، ثم القضاء، وما بقي للأنظمة؛ التقسيم حصري ويطابق الإجمالي ولا يغير بيانات المواد.',
};
await fs.writeFile(`${root}/hero_stats_audit.json`, JSON.stringify(audit, null, 2));
console.log(JSON.stringify(audit));
