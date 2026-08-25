import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const root = process.cwd();
const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const precheck = load('iirmll_9_duplicate_removal_precheck.json');
const execution = load('iirmll_9_duplicate_removal_execution.json');
const validation = load('iirmll_9_duplicate_removal_post_validation.json');
const commit = execFileSync('git', ['rev-parse', '--short', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim();
const tag = execFileSync('git', ['rev-parse', '--short', 'stable-clean-state-11286-2026-08-25'], { cwd: root, encoding: 'utf8' }).trim();
const lines = [
  'تقرير تنفيذ حذف التكرارات المحددة — مصدر iirmll / المكتبة القانونية ⚖️',
  'التاريخ: 2026-08-25',
  '',
  'النطاق والتنفيذ',
  'اقتصر الحذف على المعرفات التسعة المعتمدة صراحةً. لم يستخدم حذف بالكلمات المفتاحية أو العناوين أو التطبيع العام، ولم يُحذف أي سجل موضوعي من مصدر iirmll أو من أي مصدر آخر.',
  '',
  'التحقق القبلي',
  'البند | النتيجة',
  `إجمالي المكنز قبل الحذف | ${precheck.total_items}`,
  `مواد iirmll قبل الحذف | ${precheck.iirmll_count}`,
  `المعرفات المطلوبة | ${precheck.removals.length}`,
  `المعرفات الموجودة فعلياً | ${precheck.removals.filter((row) => row.exists).length}`,
  `المعرفات المفقودة | ${precheck.missing_removal_ids.length}`,
  `المعرفات ذات مصدر غير مطابق | ${precheck.wrong_source_removal_ids.length}`,
  '',
  'المعرفات المحذوفة والعناوين الفعلية',
  ...execution.removed.map((row) => `${row.id} | ${row.title} | ${row.source} | ${row.category}`),
  '',
  'النتيجة بعد التنفيذ',
  'البند | النتيجة',
  `عدد المحذوف فعلياً | ${execution.removed_count}`,
  `إجمالي المكنز بعد الحذف | ${execution.total_after}`,
  `مواد iirmll بعد الحذف | ${execution.iirmll_after}`,
  `المعرفات التسعة المتبقية | ${validation.removed_ids_remaining_main.length}`,
  `سلامة JSON | ${validation.passed ? 'ناجحة' : 'غير ناجحة'}`,
  `تطابق items.json والنسخة المنشورة | ${validation.primary_published_same_ids ? 'نعم' : 'لا'}`,
  `وجود IDs مكررة بعد العملية | ${validation.no_duplicate_ids_main && validation.no_duplicate_ids_published ? 'لا' : 'نعم'}`,
  '',
  'السجلات المحمية',
  `بقاء النسخ المرجعية السبع: ${validation.protected_ids_missing_main.length === 0 ? 'مؤكد' : 'غير مكتمل'}.`,
  `بقاء legal_lib_12629: ${validation.protected_12629_present_main && validation.protected_12629_present_published ? 'مؤكد' : 'غير مؤكد'}.`,
  '',
  'الفحوص التقنية',
  'نجح فحص TypeScript والبناء الإنتاجي. تحققت المعاينة عبر تحميل items.json وstats.json مع معلمة كسر الكاش الجديدة؛ أعاد كلاهما HTTP 200، وإجمالي 11,286، و501 مادة للمصدر، وعدم وجود المعرفات التسعة، وبقاء جميع المعرفات المحمية.',
  '',
  'التثبيت المحلي وإعادة التشغيل',
  `النسخة الاحتياطية: backups/iirmll_9_duplicate_removal_2026-08-25/`,
  `الـcommit المحلي: ${commit}.`,
  `الوسم المحلي: stable-clean-state-11286-2026-08-25 (${tag}).`,
  `بصمة items.json بعد إعادة التشغيل: ${validation.hashes.items_main}.`,
  `بصمة stats.json بعد إعادة التشغيل: ${validation.hashes.stats_main}.`,
  'أعيد تشغيل المعاينة مرة واحدة بعد التثبيت، وبقيت الأعداد والبصمات والحذوف كما هي.',
  '',
  'حدود التنفيذ',
  'لم يُنشأ checkpoint مُدار، ولم تُنفذ مزامنة GitHub أو Push أو نشر للموقع.',
  '',
];
writeFileSync(path.join(root, 'iirmll_9_duplicate_removal_execution_report.txt'), lines.join('\n'), 'utf8');
console.log(JSON.stringify({ report: 'iirmll_9_duplicate_removal_execution_report.txt', total_after: execution.total_after, iirmll_after: execution.iirmll_after, commit, tag }, null, 2));
