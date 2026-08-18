import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const read = (relative) => JSON.parse(fs.readFileSync(path.join(root, relative), 'utf8'))
const write = (relative, data) => fs.writeFileSync(path.join(root, relative), JSON.stringify(data, null, 2))

const items = read('items.cleaned.json')
const stats = read('client/public/stats.json')
const category = (item) => String(item.category || '')

const nextStats = {
  ...stats,
  total_items: items.length,
  total: items.length,
  qadaa_count: items.filter((item) => /قضاء|قضائي/.test(category(item))).length,
  nizam_count: items.filter((item) => /نظام|لائحة|تشريع/.test(category(item))).length,
  mohama_count: items.filter((item) => /محاماة|محامي/.test(category(item))).length,
  research_count: items.filter((item) => String(item.material_type || '') === 'بحث').length,
  last_updated: '2026-08-18',
}
nextStats.mohamah_count = nextStats.mohama_count

write('items.json', items)
write('client/public/items.json', items)
write('client/public/stats.json', nextStats)

console.log(JSON.stringify({
  total_items: nextStats.total_items,
  qadaa_count: nextStats.qadaa_count,
  nizam_count: nextStats.nizam_count,
  mohama_count: nextStats.mohama_count,
  research_count: nextStats.research_count,
}, null, 2))
