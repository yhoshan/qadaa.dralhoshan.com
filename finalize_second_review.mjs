import fs from 'node:fs'

const source = JSON.parse(fs.readFileSync('title_review_second_pass.json', 'utf8'))
const threshold = 0.85
const decisions = source.decisions.map((row) => {
  if (row.decision === 'REMOVE' && row.confidence < threshold) {
    return {
      ...row,
      decision: 'REVIEW',
      reason: `ثقة الحذف ${row.confidence} أقل من عتبة التحفظ ${threshold}: ${row.reason}`,
    }
  }
  return row
})
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
const final = {
  model: source.model,
  total_cases: decisions.length,
  removal_confidence_threshold: threshold,
  counts,
  decisions,
  remove_examples: decisions.filter((row) => row.decision === 'REMOVE').slice(0, 30).map(display),
  review_examples: decisions.filter((row) => row.decision === 'REVIEW').slice(0, 30).map(display),
}
fs.writeFileSync('title_review_second_pass_final.json', JSON.stringify(final, null, 2))
console.log(JSON.stringify({ total_cases: final.total_cases, threshold, counts }, null, 2))
