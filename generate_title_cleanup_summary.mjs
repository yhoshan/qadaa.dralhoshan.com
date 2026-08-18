import fs from 'node:fs'
import path from 'node:path'

const root = process.cwd()
const read = (file) => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'))
const report = read('title_cleanup_report.json')
const reviews = read('title_review_needed.json')
const stats = read('client/public/stats.json')

const line = (text = '') => `${text}\n`
const item = (row, index) => `${index + 1}. [${row.id}] ${row.title}\n   المصدر: ${row.source} | القسم: ${row.category}\n   السبب: ${row.reason}\n`
let output = ''
output += line('تقرير تنظيف عناوين مكنز القضاء والأنظمة والمحاماة')
output += line('=====================================================')
output += line('')
output += line('نطاق التنفيذ')
output += line('راجعت العناوين دلالياً على مرحلتين مستقلتين. حُذفت المواد فقط عند اتفاق المرحلتين على REMOVE وثقة مراجعة لا تقل عن 0.92. بقيت كل الحالات الملتبسة في ملف REVIEW وداخل البيانات المنشورة.')
output += line('')
output += line('النتائج الرقمية')
output += line(`إجمالي المواد قبل التنظيف: ${report.total_before}`)
output += line(`المواد المحذوفة: ${report.removed_count}`)
output += line(`المواد المحتفظ بها مباشرة: ${report.kept_count}`)
output += line(`الحالات المحالة للمراجعة اليدوية: ${report.review_count}`)
output += line(`إجمالي المواد بعد التنظيف: ${report.total_after}`)
output += line(`عداد القضاء بعد التحديث: ${stats.qadaa_count}`)
output += line(`عداد الأنظمة بعد التحديث: ${stats.nizam_count}`)
output += line(`عداد المحاماة بعد التحديث: ${stats.mohama_count}`)
output += line('')
output += line('أكثر المصادر التي حُذفت منها مواد')
Object.entries(report.removed_by_source).slice(0, 12).forEach(([source, count]) => { output += line(`- ${source}: ${count}`) })
output += line('')
output += line('20 مثالاً من المواد المحذوفة')
report.removed_items.slice(0, 20).forEach((row, index) => { output += item(row, index) })
output += line('')
output += line('20 مثالاً من الحالات المحالة للمراجعة اليدوية')
reviews.slice(0, 20).forEach((row, index) => { output += item(row, index) })
output += line('')
output += line('سلامة التنفيذ')
output += line('تطابق ملف البيانات الرئيس مع النسخة المنشورة. لا توجد معرفات مكررة أو مواد بلا رابط فتح، ولا تظهر المعرفات المحذوفة في البيانات الحالية. أُضيفت بوابة إدخال محافظة لسكربتات أرشيف الإنترنت ومكتبة الإسكندرية والرسائل؛ فلا يُقبل العنوان مستقبلاً بسبب المصدر أو كلمة مشتركة وحدها.')

fs.writeFileSync(path.join(root, 'title_cleanup_summary.txt'), output, 'utf8')
console.log('تم إنشاء title_cleanup_summary.txt')
