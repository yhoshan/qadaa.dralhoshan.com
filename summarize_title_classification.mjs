import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const items = JSON.parse(fs.readFileSync(path.join(root, 'items.json'), 'utf8'))
const progress = JSON.parse(fs.readFileSync(path.join(root, 'title_classifications.progress.json'), 'utf8'))
const byId = new Map(items.map((item) => [String(item.id), item]))
const decisions = progress.classifications.reduce((acc, row) => {
  acc[row.decision] = acc[row.decision] || []
  acc[row.decision].push(row)
  return acc
}, {})

const output = {
  classified_items: progress.classified_items,
  counts: Object.fromEntries(Object.entries(decisions).map(([key, rows]) => [key, rows.length])),
  samples: Object.fromEntries(['KEEP', 'REMOVE', 'REVIEW'].map((decision) => [
    decision,
    (decisions[decision] || []).slice(0, 25).map((row) => ({
      id: row.id,
      title: byId.get(String(row.id))?.title || '',
      source: byId.get(String(row.id))?.source || '',
      category: byId.get(String(row.id))?.category || '',
      reason: row.reason,
      confidence: row.confidence,
    })),
  ])),
}

fs.writeFileSync(path.join(root, 'title_classification_snapshot.json'), JSON.stringify(output, null, 2))
console.log(JSON.stringify(output, null, 2))
