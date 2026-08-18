import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const read = (file) => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'))
const items = read('items.json')
const publicItems = read('client/public/items.json')
const report = read('title_cleanup_report.json')
const review = read('title_review_needed.json')
const stats = read('client/public/stats.json')

const ids = new Set(items.map((item) => String(item.id)))
const publicIds = new Set(publicItems.map((item) => String(item.id)))
const duplicateIds = items.length - ids.size
const noLinks = items.filter((item) => !item.link_telegram && !item.link_direct && !item.link_drive)
const removedStillPresent = report.removed_items.filter((row) => ids.has(String(row.id)))
const reviewMissing = review.filter((row) => !ids.has(String(row.id)))
const publicMismatch = items.length !== publicItems.length || ids.size !== publicIds.size || [...ids].some((id) => !publicIds.has(id))

const result = {
  total_current: items.length,
  total_reported_after: report.total_after,
  total_public: publicItems.length,
  stats_total: stats.total_items,
  duplicate_id_count: duplicateIds,
  items_without_open_link_count: noLinks.length,
  removed_ids_still_present: removedStillPresent.length,
  review_ids_missing_from_current_data: reviewMissing.length,
  public_copy_mismatch: publicMismatch,
  passed: items.length === report.total_after
    && publicItems.length === items.length
    && stats.total_items === items.length
    && duplicateIds === 0
    && noLinks.length === 0
    && removedStillPresent.length === 0
    && reviewMissing.length === 0
    && !publicMismatch,
}

fs.writeFileSync(path.join(root, 'title_cleanup_validation.json'), JSON.stringify(result, null, 2))
console.log(JSON.stringify(result, null, 2))
if (!result.passed) process.exitCode = 1
