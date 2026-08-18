import fs from 'node:fs'

const items = JSON.parse(fs.readFileSync('items.json', 'utf8'))
const normalizeArabic = (text) => String(text || '')
  .replace(/[أإآا]/g, 'ا')
  .replace(/[\u064B-\u065F]/g, '')
  .replace(/ة/g, 'ه')
  .replace(/ى/g, 'ي')
  .toLowerCase()
  .trim()

const search = (query) => items.filter((item) => normalizeArabic([
  item.title, item.author, item.investigator, item.category, item.source,
].join(' ')).includes(normalizeArabic(query))).length

const results = {
  total_items: items.length,
  search_hamza_plain: { with_hamza: search('إثبات'), without_hamza: search('اثبات') },
  filter_category_count: items.filter((item) => item.category === 'الأنظمة والتشريعات').length,
  filter_source_count: items.filter((item) => String(item.source).includes('مكتبة الاسكندرية')).length,
  all_items_have_required_title_and_id: items.every((item) => String(item.id || '').trim() && String(item.title || '').trim()),
}
results.search_hamza_normalization_passed = results.search_hamza_plain.with_hamza === results.search_hamza_plain.without_hamza
results.passed = results.total_items > 0
  && results.all_items_have_required_title_and_id
  && results.search_hamza_normalization_passed
  && results.filter_category_count > 0
  && results.filter_source_count > 0

fs.writeFileSync('title_cleanup_search_filter_validation.json', JSON.stringify(results, null, 2))
console.log(JSON.stringify(results, null, 2))
if (!results.passed) process.exitCode = 1
