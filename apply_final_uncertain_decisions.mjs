import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const read = (file) => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'))
const write = (file, value) => fs.writeFileSync(path.join(root, file), JSON.stringify(value, null, 2))
const keepId = 'legal_mag_340'
const uncertain = read('sample_uncertain_records.json')
const removeIds = new Set(uncertain.filter((item) => item.id !== keepId).map((item) => String(item.id)))
if (uncertain.length !== 7 || removeIds.size !== 6 || !uncertain.some((item) => item.id === keepId)) throw new Error('قائمة القرارات النهائية غير مطابقة للسبعة المعروضة')
const items = read('items.json')
const statsBefore = read('client/public/stats.json')
const byId = new Map(items.map((item) => [String(item.id), item]))
const missing = [...removeIds].filter((id) => !byId.has(id))
if (missing.length) throw new Error(`عناوين الحذف غير موجودة: ${missing.join(', ')}`)
if (!byId.has(keepId)) throw new Error('سجل التعرفة الكمركية غير موجود للإبقاء')
const removed = items.filter((item) => removeIds.has(String(item.id)))
const retained = items.filter((item) => !removeIds.has(String(item.id)))
const bucket = (item) => {
  const category = String(item.category || '')
  if (/محاماة|محامي/.test(category)) return 'mohama_count'
  if (/أنظمة|تشريع|لائحة/.test(category)) return 'nizam_count'
  return 'qadaa_count'
}
const decrements = { qadaa_count: 0, nizam_count: 0, mohama_count: 0, research_count: 0 }
for (const item of removed) {
  decrements[bucket(item)] += 1
  if (String(item.material_type || '') === 'بحث') decrements.research_count += 1
}
const stats = {
  ...statsBefore,
  total_items: retained.length,
  total: retained.length,
  qadaa_count: Math.max(0, Number(statsBefore.qadaa_count || 0) - decrements.qadaa_count),
  nizam_count: Math.max(0, Number(statsBefore.nizam_count || 0) - decrements.nizam_count),
  mohama_count: Math.max(0, Number(statsBefore.mohama_count ?? statsBefore.mohamah_count ?? 0) - decrements.mohama_count),
  research_count: Math.max(0, Number(statsBefore.research_count || 0) - decrements.research_count),
  last_updated: '2026-08-19',
}
stats.mohamah_count = stats.mohama_count
const stamp = new Date().toISOString().replace(/[:.]/g, '-').replace('T', '_').replace('Z', '')
const backup = path.join(root, 'backups', `final-uncertain-decisions-${stamp}`)
fs.mkdirSync(backup, { recursive: true })
for (const file of ['items.json', 'client/public/items.json', 'client/public/stats.json']) fs.copyFileSync(path.join(root, file), path.join(backup, path.basename(file)))
write('items.json', retained)
write('client/public/items.json', retained)
write('client/public/stats.json', stats)
const hookPath = path.join(root, 'client/src/hooks/useItems.ts')
const hook = fs.readFileSync(hookPath, 'utf8')
fs.writeFileSync(hookPath, hook.replace(/items\.json\?v=[^'"`\s)]+/, 'items.json?v=final-uncertain-decisions-2026-08-19'))
const report = { total_before: items.length, total_after: retained.length, kept_id: keepId, removed_ids: [...removeIds], removed_count: removed.length, decrements, stats }
write('final_uncertain_decisions_report.json', report)
write('final_uncertain_decisions_removed.json', removed)
console.log(JSON.stringify(report, null, 2))
