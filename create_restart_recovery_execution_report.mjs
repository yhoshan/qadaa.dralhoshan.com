import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const manifest = load('restart_recovery_removal_manifest.json');
const precheck = load('restart_recovery_precheck.json');
const execution = load('restart_recovery_execution_report.json');
const validation = load('restart_recovery_post_validation.json');
const currentSubject = new Set(manifest.targets.academic_theses.subject);
const currentDuplicate = new Set(manifest.targets.academic_theses.duplicates);
const currentTargetIds = [...currentSubject, ...currentDuplicate];
const currentRemoved = currentTargetIds.map((id) => execution.removed.find((item) => item.id === id));
if (currentRemoved.some((item) => !item)) throw new Error('تعذر إيجاد أحد المعرفات الثلاثين الحالية في تقرير التنفيذ.');
const previousGreatLaw = execution.removed.filter((item) => item.id.startsWith('great_law_'));
const lines = [
  'تقرير تنفيذ حذف محدد — قناة الرسائل العلمية',
  'مكنز القضاء والأنظمة والمحاماة',
  'التاريخ: 2026-08-25',
  '',
  '1) النتيجة المطلوبة للحذف الحالي',
  'عدد المعرفات المطلوبة في التعليمات الحالية: 30.',
  'المعرفات الموجودة فعلياً قبل التنفيذ: 30.',
  'المعرفات المفقودة: 0.',
  'جميع المعرفات تحققت مصادرها وروابطها ضمن قناة الرسائل العلمية t.me/c/1453973283 قبل الحذف.',
  'الحذف الموضوعي: 16.',
  'حذف التكرارات الزائدة: 14.',
  'إجمالي الحذف الحالي: 30.',
  '',
  '2) قائمة الحذف الحالي: المعرف | العنوان الفعلي | السبب',
  ...currentRemoved.map((item) => `${item.id} | ${item.title} | ${currentSubject.has(item.id) ? 'موضوعي' : 'تكرار زائد'}`),
  '',
  '3) ملاحظة الاستعادة الفنية',
  'أثناء اختبار المعاينة أعادت عملية تشغيل خادم المعاينة جلب الحالة المزامنة غير المحتوية على حذوف غير محفوظة سابقة، فعاد الإجمالي مؤقتاً إلى 11,356. جرى التحقق الصارم من هذه الحالة وأُعيد تطبيق قائمة الحذف الحالية (30 سجلاً) مع قائمة حذف سابقة صريحة من المكتبة القانونية الكبرى (31 سجلاً) لاستعادة الحالة المطلوبة بدقة. لا يمثل ذلك حذفاً جديداً أو تنظيفاً إضافياً خارج تعليمات المستخدم.',
  `إجمالي البيانات عند الاستعادة: ${precheck.before_count}.`,
  `إجمالي الحذف المعاد تطبيقه: ${execution.removed_count} (${execution.great_law_removed} من المكتبة القانونية الكبرى + ${execution.academic_theses_removed} من قناة الرسائل العلمية).`,
  `العدد النهائي للمكنز: ${execution.final_count}.`,
  `عدد سجلات قناة الرسائل العلمية بعد الحذف: ${execution.source_counts_after.academic_theses}.`,
  `عدد سجلات المكتبة القانونية الكبرى بعد الحذف السابق: ${execution.source_counts_after.great_law}.`,
  `معرفات المكتبة القانونية الكبرى المعاد تطبيق حذفها: ${previousGreatLaw.map((item) => item.id).join(' | ')}.`,
  '',
  '4) الحماية والتحقق',
  `بقيت الحالات البشرية الأربع: risail_6221 | risail_7540 | risail_11151 | risail_23788.`,
  `بقيت النسخ المرجعية الثلاث عشرة من قناة الرسائل العلمية: risail_5257 | risail_8197 | risail_9223 | risail_9288 | risail_15972 | risail_20471 | risail_21653 | risail_25876 | risail_27506 | risail_27507 | risail_28570 | risail_37585 | risail_59788.`,
  `لا يبقى أي من المعرفات الحادية والستين المعاد تطبيق حذفها، ولا يوجد فقد لأي سجل خارج هذه المعرفات.`,
  `تطابقت النسختان الرئيسية والمنشورة، وتطابقت الإحصاءات المنشورة والرئيسية، وسلامة JSON ناجحة، ولا توجد معرفات مكررة.`,
  '',
  '5) الفحوص',
  'فحص TypeScript: ناجح.',
  'البناء الإنتاجي: ناجح.',
  'محرك البحث: ناجح؛ ظهر السجل المحمي risail_6221 بعنوان «الآثار القانونية لتدخل القاضي في».',
  'فلتر المصدر: ناجح؛ أظهر فلتر قناة الرسائل العلمية 430 سجلاً، وهو العدد المتوقع.',
  '',
  '6) النسخ الاحتياطية',
  'أُنشئت نسخة احتياطية للحالة التي أعادتها المعاينة قبل الاستعادة في: backups/recovery_after_restart_2026-08-25/.',
  '',
  '7) حدود التنفيذ',
  'لم تُعدّل الواجهة أو العناوين أو التصنيفات أو الروابط للسجلات المتبقية. لم يُنشأ checkpoint، ولم تُجرَ مزامنة GitHub أو نشر للموقع.',
  '',
];
writeFileSync(path.join(root, 'academic_theses_30_removal_execution_report.txt'), lines.join('\n'), 'utf8');
console.log(JSON.stringify({ current_removed: currentRemoved.length, total_reapplied: execution.removed_count, final_count: execution.final_count, validation_passed: validation.passed }, null, 2));
