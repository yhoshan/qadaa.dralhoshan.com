import fs from 'node:fs'
import crypto from 'node:crypto'

const read = (file) => JSON.parse(fs.readFileSync(file, 'utf8'))
const items = read('items.json')
const publicItems = read('client/public/items.json')
const stats = read('client/public/stats.json')
const report = read('final_closure_report.json')
const finalKeeps = read('final_closure_kept.json')
const ids = items.map((item) => String(item.id))
const duplicateIds = ids.filter((id, index) => ids.indexOf(id) !== index)
const missingLinks = items.filter((item) => !String(item.link_telegram || item.link_direct || item.link_drive || '').trim()).map((item) => item.id)
const equivalent = crypto.createHash('sha256').update(JSON.stringify(items)).digest('hex') === crypto.createHash('sha256').update(JSON.stringify(publicItems)).digest('hex')
const keepPresent = finalKeeps.every((item) => ids.includes(String(item.id)))
const useItems = fs.readFileSync('client/src/hooks/useItems.ts', 'utf8')
const validation = {
  total_items: items.length,
  public_copy_matches: equivalent,
  stats_total_matches: Number(stats.total_items) === items.length && Number(stats.total) === items.length,
  unique_ids: duplicateIds.length === 0,
  missing_links_count: missingLinks.length,
  explicit_keeps_present: keepPresent,
  final_review_count: report.final_review_count,
  cache_version_updated: useItems.includes('items.json?v=final-closure-2026-08-19'),
}
validation.passed = Object.values(validation).every((value) => value === true || value === 0 || typeof value === 'number')
fs.writeFileSync('final_closure_validation.json', JSON.stringify(validation, null, 2))
console.log(JSON.stringify(validation, null, 2))
