import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const readJson = (file) => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'))
const writeJson = (file, data) => fs.writeFileSync(path.join(root, file), JSON.stringify(data, null, 2))

const items = readJson('items.json')
const firstPass = readJson('title_classifications.json').classifications
const secondPass = readJson('title_removal_review.json').reviews
const firstById = new Map(firstPass.map((row) => [String(row.id), row]))
const secondById = new Map(secondPass.map((row) => [String(row.id), row]))

const removed = []
const reviews = []
const kept = []

for (const item of items) {
  const id = String(item.id)
  const first = firstById.get(id)
  if (!first) throw new Error(`لا يوجد قرار أولي للمعرف ${id}`)

  if (first.decision === 'REMOVE') {
    const confirmation = secondById.get(id)
    if (!confirmation) throw new Error(`لا توجد مراجعة حذف للمعرف ${id}`)
    if (confirmation.final_decision === 'REMOVE' && confirmation.confidence >= 0.92) {
      removed.push({
        id,
        title: item.title,
        source: item.source,
        category: item.category,
        reason: confirmation.reason,
        first_pass_reason: first.reason,
        confirmation_confidence: confirmation.confidence,
      })
    } else if (confirmation.final_decision === 'KEEP') {
      kept.push(item)
    } else {
      reviews.push({
        id,
        title: item.title,
        source: item.source,
        category: item.category,
        reason: confirmation.reason || first.reason,
      })
      kept.push(item)
    }
    continue
  }

  if (first.decision === 'REVIEW') {
    reviews.push({
      id,
      title: item.title,
      source: item.source,
      category: item.category,
      reason: first.reason,
    })
  }
  kept.push(item)
}

const countBy = (rows, key) => Object.fromEntries(Object.entries(rows.reduce((acc, row) => {
  const value = String(row[key] || 'غير محدد')
  acc[value] = (acc[value] || 0) + 1
  return acc
}, {})).sort((a, b) => b[1] - a[1]))

const report = {
  total_before: items.length,
  kept_count: kept.length - reviews.length,
  removed_count: removed.length,
  review_count: reviews.length,
  total_after: kept.length,
  removed_by_source: countBy(removed, 'source'),
  removed_by_category: countBy(removed, 'category'),
  removed_items: removed,
  decision_policy: 'يُحذف العنوان فقط إذا صنفته المرحلتان REMOVE وكانت ثقة المراجعة المستقلة 0.92 أو أعلى. تبقى كل الحالات الملتبسة في REVIEW ضمن البيانات المنشورة.',
}

if (report.total_after !== report.total_before - report.removed_count) {
  throw new Error('فشل تحقق معادلة العدد بعد الحذف')
}

writeJson('items.cleaned.json', kept)
writeJson('title_review_needed.json', reviews)
writeJson('title_cleanup_report.json', report)
writeJson('title_cleanup_plan_summary.json', {
  total_before: report.total_before,
  kept_count: report.kept_count,
  review_count: report.review_count,
  removed_count: report.removed_count,
  total_after: report.total_after,
  sample_removed: removed.slice(0, 20),
  sample_review: reviews.slice(0, 20),
})

console.log(JSON.stringify({
  total_before: report.total_before,
  kept_count: report.kept_count,
  review_count: report.review_count,
  removed_count: report.removed_count,
  total_after: report.total_after,
}, null, 2))
