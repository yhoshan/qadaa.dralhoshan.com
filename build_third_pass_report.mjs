import fs from 'node:fs'

const data = JSON.parse(fs.readFileSync('title_review_third_pass.json', 'utf8'))
const decisions = data.decisions || []
const counts = decisions.reduce((acc, row) => {
  acc[row.decision] = (acc[row.decision] || 0) + 1
  return acc
}, { KEEP: 0, REMOVE: 0, REVIEW: 0 })
const source = JSON.parse(fs.readFileSync('title_review_second_pass_final.json', 'utf8'))
const expected = new Set(source.decisions.filter((row) => row.decision === 'REVIEW').map((row) => String(row.id)))
const received = new Set(decisions.map((row) => String(row.id)))
const valid = decisions.length === expected.size && [...expected].every((id) => received.has(id))
const line = (row, number, detail = true) => {
  const context = row.context || {}
  const core = `${number}. ${context.title || ''}`
  return detail
    ? `${core}\n   المصدر: ${context.source || ''} | التصنيف: ${context.category || ''}\n   السبب: ${row.reason}\n`
    : core
}
const report = [
  'نتيجة الجولة الثالثة النهائية للحالات الملتبسة',
  '================================================',
  `KEEP: ${counts.KEEP}`,
  `REMOVE: ${counts.REMOVE}`,
  `REVIEW النهائي: ${counts.REVIEW}`,
  `سلامة التغطية: ${valid ? 'مكتملة' : 'غير مكتملة'}`,
  '',
  'جميع عناوين REVIEW النهائي',
  ...decisions.filter((row) => row.decision === 'REVIEW').map((row, index) => line(row, index + 1)),
  '',
  '30 مثالاً من REMOVE',
  ...decisions.filter((row) => row.decision === 'REMOVE').slice(0, 30).map((row, index) => line(row, index + 1)),
].join('\n')
fs.writeFileSync('title_review_third_pass_results.txt', report)
fs.writeFileSync('title_review_third_pass_validation.json', JSON.stringify({
  expected_cases: expected.size,
  decided_cases: decisions.length,
  counts,
  ids_match: valid,
  no_site_data_modified: true,
  no_publish_performed: true,
}, null, 2))
console.log(JSON.stringify({ expected_cases: expected.size, decided_cases: decisions.length, counts, ids_match: valid }, null, 2))
