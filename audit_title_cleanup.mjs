import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const items = JSON.parse(fs.readFileSync(path.join(root, 'items.json'), 'utf8'))
const stats = JSON.parse(fs.readFileSync(path.join(root, 'client/public/stats.json'), 'utf8'))

const by = (key) => Object.entries(items.reduce((acc, item) => {
  const value = String(item[key] || 'غير محدد').trim() || 'غير محدد'
  acc[value] = (acc[value] || 0) + 1
  return acc
}, {})).sort((a, b) => b[1] - a[1])

const ids = new Set()
const duplicateIds = []
const noLink = []
for (const item of items) {
  if (ids.has(item.id)) duplicateIds.push(item.id)
  ids.add(item.id)
  if (!item.link_telegram && !item.link_direct && !item.link_drive) noLink.push(item.id)
}

const report = {
  total_items: items.length,
  stats,
  duplicate_id_count: duplicateIds.length,
  items_without_open_link_count: noLink.length,
  top_sources: by('source').slice(0, 40),
  top_categories: by('category').slice(0, 40),
  top_material_types: by('material_type').slice(0, 20),
  top_file_types: by('file_type').slice(0, 20),
}

fs.writeFileSync(path.join(root, 'title_cleanup_audit.json'), JSON.stringify(report, null, 2))
console.log(JSON.stringify(report, null, 2))
