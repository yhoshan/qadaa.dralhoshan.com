import fs from 'node:fs/promises';

const root = process.cwd();
const itemPaths = [`${root}/items.json`, `${root}/client/public/items.json`];
const statsPaths = [`${root}/stats.json`, `${root}/client/public/stats.json`];

function heroGroup(category = '') {
  // تقسيم حصري لجميع المواد: المحاماة والتحكيم أولاً، ثم القضاء، وما بقي للأنظمة والقانون.
  if (/(محام|تحكيم|وساط)/u.test(category)) return 'mohama';
  if (/(قضاء|قضائي|محكم|مرافع|إثبات|جنا|جزائي|حسبة|مظالم|أحكام|إجراء.*قضائي|قرار.*قضائي)/u.test(category)) return 'qadaa';
  return 'nizam';
}
const mainContainer = JSON.parse(await fs.readFile(itemPaths[0], 'utf8'));
const items = Array.isArray(mainContainer) ? mainContainer : mainContainer.items;
if (!Array.isArray(items)) throw new Error('بنية items.json غير متوقعة');
const counts = items.reduce((acc, item) => {
  acc[heroGroup(item.category)] += 1;
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
  rule: 'المحاماة والتحكيم أولاً، ثم القضاء، وما بقي للأنظمة والقانون؛ التقسيم حصري ويطابق الإجمالي.',
};
await fs.writeFile(`${root}/hero_stats_audit.json`, JSON.stringify(audit, null, 2));
console.log(JSON.stringify(audit));
