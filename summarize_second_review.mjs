import fs from 'node:fs'

const input = fs.existsSync('title_review_second_pass.json')
  ? 'title_review_second_pass.json'
  : 'title_review_second_pass.progress.json'
const data = JSON.parse(fs.readFileSync(input, 'utf8'))
const decisions = data.decisions || []
const counts = decisions.reduce((acc, row) => {
  acc[row.decision] = (acc[row.decision] || 0) + 1
  return acc
}, { KEEP: 0, REMOVE: 0, REVIEW: 0 })
const display = (row) => ({
  id: row.id,
  title: row.context?.title || '',
  source: row.context?.source || '',
  category: row.context?.category || '',
  material_type: row.context?.material_type || '',
  reason: row.reason,
  confidence: row.confidence,
})
const report = {
  input,
  total_decisions: decisions.length,
  counts,
  remove_confidence_buckets: decisions.filter((row) => row.decision === 'REMOVE').reduce((acc, row) => {
    const bucket = row.confidence >= 0.95 ? '0.95_1.00' : row.confidence >= 0.85 ? '0.85_0.94' : row.confidence >= 0.75 ? '0.75_0.84' : 'below_0.75'
    acc[bucket] = (acc[bucket] || 0) + 1
    return acc
  }, {}),
  remove_examples: decisions.filter((row) => row.decision === 'REMOVE').slice(0, 30).map(display),
  review_examples: decisions.filter((row) => row.decision === 'REVIEW').slice(0, 30).map(display),
}
fs.writeFileSync('title_review_second_pass_summary.json', JSON.stringify(report, null, 2))
console.log(JSON.stringify(report, null, 2))
