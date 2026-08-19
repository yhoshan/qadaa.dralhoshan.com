import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const read = (file) => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'))
const write = (file, value) => fs.writeFileSync(path.join(root, file), JSON.stringify(value, null, 2))
const now = new Date().toISOString().replace(/[:.]/g, '-').replace('T', '_').replace('Z', '')

const explicitKeeps = new Set([
  'qadaa_10466',
  'qadaa_12297',
  'archive_alfirdwsiy2018_gmail_2551_201810',
])

const current = read('items.json')
const statsBefore = read('client/public/stats.json')
const second = read('title_review_second_pass_final.json')
const third = read('title_review_third_pass_merged.json')
const secondRemoves = second.decisions.filter((row) => row.decision === 'REMOVE').map((row) => String(row.id))
const thirdRemoves = third.decisions.filter((row) => row.decision === 'REMOVE').map((row) => String(row.id))
const finalReviewRemoves = third.decisions
  .filter((row) => row.decision === 'REVIEW' && !explicitKeeps.has(String(row.id)))
  .map((row) => String(row.id))
const removeIds = new Set([...secondRemoves, ...thirdRemoves, ...finalReviewRemoves])
const byId = new Map(current.map((item) => [String(item.id), item]))
const missingKeeps = [...explicitKeeps].filter((id) => !byId.has(id))
const missingRemoveIds = [...removeIds].filter((id) => !byId.has(id))
if (missingKeeps.length) throw new Error(`سجل KEEP مفقود: ${missingKeeps.join(', ')}`)

const removed = current.filter((item) => removeIds.has(String(item.id)))
const retained = current.filter((item) => !removeIds.has(String(item.id)))
const duplicateIds = retained.map((item) => String(item.id)).filter((id, index, arr) => arr.indexOf(id) !== index)
if (duplicateIds.length) throw new Error(`معرفات مكررة بعد الإغلاق: ${duplicateIds.slice(0, 10).join(', ')}`)

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

fs.mkdirSync(path.join(root, 'backups', `final-closure-${now}`), { recursive: true })
fs.copyFileSync(path.join(root, 'items.json'), path.join(root, 'backups', `final-closure-${now}`, 'items.before.json'))
fs.copyFileSync(path.join(root, 'client/public/items.json'), path.join(root, 'backups', `final-closure-${now}`, 'client-public-items.before.json'))
fs.copyFileSync(path.join(root, 'client/public/stats.json'), path.join(root, 'backups', `final-closure-${now}`, 'stats.before.json'))

write('items.json', retained)
write('client/public/items.json', retained)
write('client/public/stats.json', stats)
const useItemsPath = path.join(root, 'client/src/hooks/useItems.ts')
const useItems = fs.readFileSync(useItemsPath, 'utf8')
fs.writeFileSync(useItemsPath, useItems.replace(/items\.json\?v=[^'"`\s)]+/, 'items.json?v=final-closure-2026-08-19'))

const report = {
  applied_at: new Date().toISOString(),
  total_before: current.length,
  total_after: retained.length,
  removed_this_closure: removed.length,
  removed_from_second_pass: secondRemoves.length,
  removed_from_third_pass: thirdRemoves.length,
  removed_from_final_review: finalReviewRemoves.length,
  explicit_kept_ids: [...explicitKeeps],
  final_review_count: 0,
  missing_remove_ids_not_in_current_data: missingRemoveIds,
  decrements,
  stats,
}
write('final_closure_report.json', report)
write('final_closure_removed.json', removed)
write('final_closure_kept.json', [...explicitKeeps].map((id) => byId.get(id)))
console.log(JSON.stringify(report, null, 2))
