import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const read = (file) => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'))
const write = (file, value) => fs.writeFileSync(path.join(root, file), JSON.stringify(value, null, 2))
const items = read('items.json')
const publicItems = read('client/public/items.json')
const statsBefore = read('client/public/stats.json')
const audit = read('final_closure_random_200_audit.json')
const removeIds = new Set(audit.decisions.filter((row) => row.verdict === 'CLEAR_OUT_OF_SCOPE').map((row) => String(row.id)))
const uncertain = audit.decisions.filter((row) => row.verdict === 'UNCERTAIN').map((row) => ({
  id: String(row.id),
  title: row.context.title || '',
  author: row.context.author || '',
  source: row.context.source || '',
  category: row.context.category || '',
  reason: row.reason || '',
}))
if (removeIds.size !== 6) throw new Error(`المتوقع حذف 6 عناوين واضحة، وُجد ${removeIds.size}`)
if (uncertain.length !== 7) throw new Error(`المتوقع 7 عناوين غير محسومة، وُجد ${uncertain.length}`)
const byId = new Map(items.map((item) => [String(item.id), item]))
const missing = [...removeIds].filter((id) => !byId.has(id))
if (missing.length) throw new Error(`معرّفات الحذف غير موجودة: ${missing.join(', ')}`)
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
const backup = path.join(root, 'backups', `sample-clear-removals-${stamp}`)
fs.mkdirSync(backup, { recursive: true })
fs.copyFileSync(path.join(root, 'items.json'), path.join(backup, 'items.before.json'))
fs.copyFileSync(path.join(root, 'client/public/items.json'), path.join(backup, 'client-public-items.before.json'))
fs.copyFileSync(path.join(root, 'client/public/stats.json'), path.join(backup, 'stats.before.json'))
write('items.json', retained)
write('client/public/items.json', retained)
write('client/public/stats.json', stats)
const useItemsPath = path.join(root, 'client/src/hooks/useItems.ts')
const useItems = fs.readFileSync(useItemsPath, 'utf8')
fs.writeFileSync(useItemsPath, useItems.replace(/items\.json\?v=[^'"`\s)]+/, 'items.json?v=sample-clear-removals-2026-08-19'))
write('sample_clear_removals.json', removed)
write('sample_uncertain_records.json', uncertain)
const report = { total_before: items.length, total_after: retained.length, removed_count: removed.length, removed_ids: [...removeIds], decrements, stats, uncertain_count: uncertain.length, uncertain_ids: uncertain.map((item) => item.id) }
write('sample_clear_removals_report.json', report)
console.log(JSON.stringify(report, null, 2))
