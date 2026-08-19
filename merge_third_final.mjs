import fs from 'node:fs'

const third = JSON.parse(fs.readFileSync('title_review_third_pass.json', 'utf8'))
const tiebreak = JSON.parse(fs.readFileSync('title_review_third_pass_final.json', 'utf8'))
const reviewIds = new Set(third.decisions.filter((row) => row.decision === 'REVIEW').map((row) => String(row.id)))
const tiebreakMap = new Map(tiebreak.decisions.map((row) => [String(row.id), row]))
const merged = third.decisions.map((row) => {
  const final = tiebreakMap.get(String(row.id))
  return final ? { ...final, stage: 'final_tiebreak' } : { ...row, stage: 'third_pass' }
})
const counts = merged.reduce((acc, row) => {
  acc[row.decision] = (acc[row.decision] || 0) + 1
  return acc
}, { KEEP: 0, REMOVE: 0, REVIEW: 0 })
const mergedIds = new Set(merged.map((row) => String(row.id)))
const validation = {
  input_cases: third.decisions.length,
  final_cases: merged.length,
  expected_tiebreak_cases: reviewIds.size,
  actual_tiebreak_cases: tiebreak.decisions.length,
  ids_match: mergedIds.size === third.decisions.length && [...mergedIds].every((id) => third.decisions.some((row) => String(row.id) === id)),
  tiebreak_ids_match: reviewIds.size === tiebreakMap.size && [...reviewIds].every((id) => tiebreakMap.has(id)),
  counts,
  count_matches: counts.KEEP + counts.REMOVE + counts.REVIEW === third.decisions.length,
  no_site_data_modified: true,
  no_publish_performed: true,
}
const line = (row, index, details = true) => {
  const c = row.context || {}
  const headline = `${index}. ${c.title || ''}`
  return details ? `${headline}\n   المصدر: ${c.source || ''} | التصنيف: ${c.category || ''}\n   السبب: ${row.reason}\n` : headline
}
const report = [
  'نتيجة الجولة الثالثة والنهائية للحالات المتبقية',
  '=================================================',
  `KEEP: ${counts.KEEP}`,
  `REMOVE: ${counts.REMOVE}`,
  `REVIEW النهائي: ${counts.REVIEW}`,
  '',
  'جميع عناوين REVIEW النهائي',
  ...merged.filter((row) => row.decision === 'REVIEW').map((row, index) => line(row, index + 1)),
  '',
  '30 مثالاً من REMOVE',
  ...merged.filter((row) => row.decision === 'REMOVE').slice(0, 30).map((row, index) => line(row, index + 1)),
].join('\n')
fs.writeFileSync('title_review_third_pass_merged.json', JSON.stringify({ counts, decisions: merged }, null, 2))
fs.writeFileSync('title_review_third_pass_final_validation.json', JSON.stringify(validation, null, 2))
fs.writeFileSync('title_review_third_pass_final_results.txt', report)
console.log(JSON.stringify(validation, null, 2))
