import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const read = (relative) => JSON.parse(fs.readFileSync(path.join(root, relative), 'utf8'))
const write = (relative, value) => fs.writeFileSync(path.join(root, relative), JSON.stringify(value, null, 2))

const beforeItems = read('backups/title-cleanup-2026-08-18/items.before.json')
const beforeStats = read('backups/title-cleanup-2026-08-18/stats.before.json')
const currentItems = read('items.json')
const report = read('title_cleanup_report.json')
const beforeById = new Map(beforeItems.map((item) => [String(item.id), item]))

const bucket = (item) => {
  const category = String(item.category || '')
  if (/محاماة|محامي/.test(category)) return 'mohama_count'
  if (/أنظمة|تشريع|لائحة/.test(category)) return 'nizam_count'
  return 'qadaa_count'
}

const decrements = { qadaa_count: 0, nizam_count: 0, mohama_count: 0, research_count: 0 }
for (const row of report.removed_items) {
  const item = beforeById.get(String(row.id))
  if (!item) throw new Error(`معرف محذوف غير موجود في النسخة الاحتياطية: ${row.id}`)
  decrements[bucket(item)] += 1
  if (String(item.material_type || '') === 'بحث') decrements.research_count += 1
}

const stats = {
  ...beforeStats,
  total_items: currentItems.length,
  total: currentItems.length,
  qadaa_count: Math.max(0, Number(beforeStats.qadaa_count || 0) - decrements.qadaa_count),
  nizam_count: Math.max(0, Number(beforeStats.nizam_count || 0) - decrements.nizam_count),
  mohama_count: Math.max(0, Number(beforeStats.mohama_count ?? beforeStats.mohamah_count ?? 0) - decrements.mohama_count),
  research_count: Math.max(0, Number(beforeStats.research_count || 0) - decrements.research_count),
  last_updated: '2026-08-18',
}
stats.mohamah_count = stats.mohama_count
write('client/public/stats.json', stats)
write('title_cleanup_stats_delta.json', { before: beforeStats, decrements, after: stats })
console.log(JSON.stringify({ decrements, after: stats }, null, 2))
