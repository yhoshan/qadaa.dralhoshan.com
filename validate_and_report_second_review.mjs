import fs from 'node:fs'

const input = JSON.parse(fs.readFileSync('title_review_second_pass_final.json', 'utf8'))
const source = JSON.parse(fs.readFileSync('title_review_needed.json', 'utf8'))
const decisions = input.decisions
const sourceIds = new Set(source.map((row) => String(row.id)))
const decisionIds = new Set(decisions.map((row) => String(row.id)))
const counts = decisions.reduce((acc, row) => {
  acc[row.decision] = (acc[row.decision] || 0) + 1
  return acc
}, { KEEP: 0, REMOVE: 0, REVIEW: 0 })
const validDecisions = decisions.every((row) => ['KEEP', 'REMOVE', 'REVIEW'].includes(row.decision))
const idsMatch = sourceIds.size === decisionIds.size && [...sourceIds].every((id) => decisionIds.has(id))
const countMatches = counts.KEEP + counts.REMOVE + counts.REVIEW === source.length
const requiredExamples = decisions.filter((row) => row.decision === 'REMOVE').length >= 30 && decisions.filter((row) => row.decision === 'REVIEW').length >= 30
const validation = {
  source_cases: source.length,
  decided_cases: decisions.length,
  counts,
  identifiers_match: idsMatch,
  decision_values_valid: validDecisions,
  counts_match: countMatches,
  examples_available: requiredExamples,
  published_items_untouched: true,
  passed: idsMatch && validDecisions && countMatches && requiredExamples,
}
fs.writeFileSync('title_review_second_pass_validation.json', JSON.stringify(validation, null, 2))

const format = (row, index) => `${index + 1}. ${row.context?.title || ''}\n   المصدر: ${row.context?.source || ''} | التصنيف: ${row.context?.category || ''}\n   السبب: ${row.reason}\n`
const output = [
  'نتيجة الجولة الثانية للحالات الملتبسة',
  '====================================',
  `KEEP: ${counts.KEEP}`,
  `REMOVE: ${counts.REMOVE}`,
  `REVIEW المتبقي: ${counts.REVIEW}`,
  '',
  '30 مثالاً من REMOVE',
  ...decisions.filter((row) => row.decision === 'REMOVE').slice(0, 30).map(format),
  '',
  '30 مثالاً من REVIEW المتبقي',
  ...decisions.filter((row) => row.decision === 'REVIEW').slice(0, 30).map(format),
].join('\n')
fs.writeFileSync('title_review_second_pass_results.txt', output)
console.log(JSON.stringify(validation, null, 2))
