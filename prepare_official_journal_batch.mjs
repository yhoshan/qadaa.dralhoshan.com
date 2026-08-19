import fs from 'node:fs'
import path from 'node:path'
import crypto from 'node:crypto'

const root = process.cwd()
const rawFiles = [
  { country: 'العراق', source: '/home/ubuntu/upload/pasted_file_X0mc5W_deepseek_json_20260819_9acc5c.json', key: 'المجلات_الحقوقية_العراقية', code: 'iq' },
  { country: 'سوريا', source: '/home/ubuntu/upload/pasted_file_83Cmay_deepseek_json_20260819_030d4b.json', key: 'المجلات_الحقوقية_السورية', code: 'sy' },
  { country: 'لبنان', source: '/home/ubuntu/upload/pasted_file_GbyIJN_deepseek_json_20260819_f87c37.json', key: 'المجلات_الحقوقية_اللبنانية', code: 'lb' },
  { country: 'الأردن', source: '/home/ubuntu/upload/pasted_file_udqrVe_deepseek_json_20260819_8a0050.json', key: 'المجلات_الحقوقية_الأردنية', code: 'jo' },
]
const stripRefs = (value) => String(value ?? '').replace(/\[reference:\d+\]/g, '').replace(/\s+/g, ' ').trim()
const norm = (value) => stripRefs(value).normalize('NFKC').replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي').replace(/[^\p{L}\p{N}]+/gu, ' ').trim().toLowerCase()
const isUrl = (value) => /^https?:\/\//i.test(stripRefs(value))
const items = JSON.parse(fs.readFileSync(path.join(root, 'items.json'), 'utf8'))
const existing = new Set(items.map((item) => norm(item.title)))
const journals = []
const skipped = []
for (const file of rawFiles) {
  const data = JSON.parse(fs.readFileSync(file.source, 'utf8'))
  const rows = data[file.key]
  if (!Array.isArray(rows)) throw new Error(`لم تُعثر قائمة ${file.key}`)
  for (const row of rows) {
    const name = stripRefs(row['الاسم'])
    const url = stripRefs(row['الرابط'])
    const fingerprint = norm(`${file.country} ${name}`)
    if (!isUrl(url)) {
      skipped.push({ country: file.country, name, reason: 'لا يوجد رابط رسمي صالح' })
      continue
    }
    if (existing.has(norm(name))) {
      skipped.push({ country: file.country, name, reason: 'عنوان مجلة موجود مسبقاً في بيانات المكنز' })
      continue
    }
    const id = `journal_link_${file.code}_${crypto.createHash('sha1').update(fingerprint).digest('hex').slice(0, 10)}`
    journals.push({
      id,
      title: name,
      author: stripRefs(row['الناشر']) || 'غير محدد',
      publisher: stripRefs(row['الناشر']) || 'غير محدد',
      year: stripRefs(row['سنة_التأسيس']) || 'غير محدد',
      source: `فهرس المجلات المتخصصة — ${file.country}`,
      category: 'المجلات القانونية',
      material_type: 'مجلة',
      file_type: 'رابط',
      file_size: '',
      pages_count: '',
      link_telegram: '',
      link_drive: '',
      link_direct: url,
      is_featured: false,
      download_links_count: 1,
      country: file.country,
      issn: stripRefs(row['ISSN']) || 'غير محدد',
      frequency: stripRefs(row['التردد']) || 'غير محدد',
      notes: stripRefs(row['ملاحظات']) || '',
    })
  }
}
const duplicateInBatch = journals.filter((journal, index) => journals.findIndex((other) => norm(`${other.country} ${other.title}`) === norm(`${journal.country} ${journal.title}`)) !== index)
if (duplicateInBatch.length) throw new Error(`تكرار داخل الدفعة: ${duplicateInBatch.map((item) => item.title).join('، ')}`)
fs.writeFileSync(path.join(root, 'official_journals_four_countries_preview.json'), JSON.stringify({ journals, skipped, input_count: journals.length + skipped.length }, null, 2))
console.log(JSON.stringify({ input_count: journals.length + skipped.length, add_count: journals.length, skipped_count: skipped.length, by_country: Object.fromEntries(rawFiles.map((file) => [file.country, journals.filter((journal) => journal.country === file.country).length])) }, null, 2))
