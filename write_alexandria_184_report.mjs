import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const execution = JSON.parse(readFileSync(path.join(root, 'alexandria_184_removal_execution_report.json'), 'utf8'));
const validation = JSON.parse(readFileSync(path.join(root, 'alexandria_184_removal_validation.json'), 'utf8'));
const lines = [
  'تقرير تنفيذ الحذف المحدد — مكتبة الإسكندرية',
  `التاريخ: ${execution.generated_at}`,
  '',
  'نطاق التنفيذ',
  'اقتصر التنفيذ على المعرفات الـ184 الواردة صراحة في طلب المستخدم. تم التحقق من وجود كل معرف ومن أن مصدره مكتبة الاسكندرية قبل الحذف، ولم يُستخدم حذف بالكلمات المفتاحية أو عناوين مشابهة.',
  '',
  'النسخ الاحتياطية قبل الحذف',
  `${execution.backup_dir}/items.before.json`,
  `${execution.backup_dir}/client-public-items.before.json`,
  `${execution.backup_dir}/stats.before.json`,
  `${execution.backup_dir}/client-public-stats.before.json`,
  '',
  'النتائج الرقمية',
  `العدد الإجمالي قبل الحذف: ${execution.before_count}`,
  `عدد المعرفات المطلوبة: ${execution.requested_count}`,
  `عدد المعرفات الموجودة فعلياً: ${execution.found_count}`,
  `عدد المعرفات غير الموجودة: ${execution.missing_count}`,
  `عدد السجلات المحذوفة فعلياً: ${execution.removed_count}`,
  `العدد الإجمالي بعد الحذف: ${execution.final_count}`,
  `عدد المعرفات المستهدفة المتبقية: ${execution.remaining_target_ids.length}`,
  '',
  'المعرفات والعناوين الفعلية المحذوفة',
  ...execution.removed.map((item, index) => `${index + 1}. ${item.id} — ${item.title}`),
  '',
  'فحوص السلامة',
  `تطابق البيانات الرئيسية والمنشورة: ${validation.main_and_published_match ? 'ناجح' : 'فشل'}`,
  `عدم وجود المعرفات المستهدفة: ${validation.remaining_target_ids_main.length === 0 && validation.remaining_target_ids_published.length === 0 ? 'ناجح' : 'فشل'}`,
  `عدم وجود معرفات مكررة: ${validation.duplicate_ids_main.length === 0 && validation.duplicate_ids_published.length === 0 ? 'ناجح' : 'فشل'}`,
  `سلامة الحقول الأساسية: ${validation.records_missing_basic_fields.length === 0 ? 'ناجح' : 'فشل'}`,
  `صحة معادلة العدد: ${validation.count_equation_valid ? 'ناجح' : 'فشل'}`,
  `حفظ السجلات خارج القائمة بالعدد: ${validation.non_target_records_preserved_by_count ? 'ناجح' : 'فشل'}`,
  'تم تحديث stats.json وclient/public/stats.json وبيانات الواجهة وكسر الكاش.',
  'نجح فحص TypeScript وبناء الإنتاج، ونجح اختبار البحث بعنوان «أدب القاضي» وفلتر بلد إصدار المجلات عند اختيار السعودية.',
  '',
  'لم يُنشر الموقع ولم تُنشأ نقطة تفتيش في هذه العملية.',
];
writeFileSync(path.join(root, 'alexandria_184_removal_execution_report.txt'), `${lines.join('\n')}\n`);
console.log(`Written report with ${execution.removed.length} removed records.`);
