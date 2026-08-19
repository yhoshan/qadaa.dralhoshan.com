import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const read = (file) => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'))
const write = (file, value) => fs.writeFileSync(path.join(root, file), JSON.stringify(value, null, 2))
const stripRefs = (value) => String(value ?? '').replace(/\[reference:\d+\]/g, '').replace(/\s+/g, ' ').trim()
const journals = read('official_journals_four_countries_preview.json').journals
const items = read('items.json')
const statsBefore = read('client/public/stats.json')
const existingIds = new Set(items.map((item) => String(item.id)))
const duplicateIds = journals.filter((journal) => existingIds.has(journal.id))
if (duplicateIds.length) throw new Error(`معرّفات مكررة: ${duplicateIds.map((item) => item.id).join(', ')}`)
const stamp = new Date().toISOString().replace(/[:.]/g, '-').replace('T', '_').replace('Z', '')
const backup = path.join(root, 'backups', `official-journals-four-countries-${stamp}`)
fs.mkdirSync(backup, { recursive: true })
for (const file of ['items.json', 'client/public/items.json', 'client/public/stats.json']) fs.copyFileSync(path.join(root, file), path.join(backup, file.replaceAll('/', '_')))
const nextItems = [...items, ...journals]
const stats = {
  ...statsBefore,
  total_items: nextItems.length,
  total: nextItems.length,
  last_updated: '2026-08-19',
}
write('items.json', nextItems)
write('client/public/items.json', nextItems)
write('client/public/stats.json', stats)
const palette = { العراق: 'oklch(0.55 0.12 155)', سوريا: 'oklch(0.58 0.12 250)', لبنان: 'oklch(0.67 0.13 35)', الأردن: 'oklch(0.55 0.12 75)' }
const uiEntries = journals.map((journal) => ({
  name: journal.title,
  description: `${journal.country} · ${journal.publisher}`,
  countLabel: 'رابط رسمي',
  color: palette[journal.country] || 'oklch(0.48 0.12 68)',
  officialLink: journal.link_direct,
}))
const ts = `/* بيانات روابط المجلات الرسمية المستوردة حسب البلد. */\nexport type OfficialJournal = { name: string; description: string; countLabel: string; color: string; officialLink: string }\n\nexport const OFFICIAL_JOURNALS: OfficialJournal[] = ${JSON.stringify(uiEntries, null, 2)}\n`
fs.mkdirSync(path.join(root, 'client/src/data'), { recursive: true })
fs.writeFileSync(path.join(root, 'client/src/data/officialJournals.ts'), ts)
const hookPath = path.join(root, 'client/src/hooks/useItems.ts')
const hook = fs.readFileSync(hookPath, 'utf8')
fs.writeFileSync(hookPath, hook.replace(/items\.json\?v=[^'"`\s)]+/, 'items.json?v=official-journals-four-countries-2026-08-19'))
const report = { added_count: journals.length, total_before: items.length, total_after: nextItems.length, by_country: Object.fromEntries([...new Set(journals.map((journal) => journal.country))].map((country) => [country, journals.filter((journal) => journal.country === country).length])), skipped: read('official_journals_four_countries_preview.json').skipped }
write('official_journals_four_countries_report.json', report)
console.log(JSON.stringify(report, null, 2))
