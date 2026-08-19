import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const read = (file) => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'))
const items = read('items.json')
const publicItems = read('client/public/items.json')
const report = read('official_journals_four_countries_report.json')
const journalLinks = items.filter((item) => String(item.id).startsWith('journal_link_'))
const ids = new Set(items.map((item) => String(item.id)))
const valid = {
  items_match_public: items.length === publicItems.length,
  expected_total: items.length === 15559,
  expected_journal_links: journalLinks.length === 25,
  unique_ids: ids.size === items.length,
  all_journal_links_valid: journalLinks.every((item) => /^https?:\/\//.test(String(item.link_direct || ''))),
  country_counts: report.by_country,
}
valid.passed = Object.entries(valid).filter(([key]) => key !== 'country_counts' && key !== 'passed').every(([, value]) => value === true)
console.log(JSON.stringify(valid, null, 2))
if (!valid.passed) process.exit(1)
