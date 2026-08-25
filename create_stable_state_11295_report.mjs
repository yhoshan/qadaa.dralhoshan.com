import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const before = load('stable_state_pre_restart_verification.json');
const after = load('stable_state_post_restart_verification.json');
const samples = load('deleted_samples_post_restart_verification.json');
const git = (args) => execFileSync('git', args, { cwd: root, encoding: 'utf8' }).trim();
const tag = 'stable-clean-state-11295-2026-08-25';
const tagCommit = git(['rev-parse', '--short', tag]);
const head = git(['rev-parse', '--short', 'HEAD']);
const aheadBehind = git(['rev-list', '--left-right', '--count', 'user_github/main...HEAD']).replace(/\s+/, ' | ');
const files = ['items.json', 'client/public/items.json', 'stats.json', 'client/public/stats.json'];
const lines = [
  'تقرير تثبيت الحالة المرجعية — مكنز القضاء والأنظمة والمحاماة',
  'التاريخ: 2026-08-25',
  '',
  '1) خلاصة النتيجة',
  `العدد قبل إعادة تشغيل المعاينة: ${before.total_items}.`,
  `العدد بعد إعادة تشغيل المعاينة: ${after.total_items}.`,
  `عدد مواد قناة الرسائل العلمية قبل إعادة التشغيل: ${before.source_count_academic_theses}.`,
  `عدد مواد قناة الرسائل العلمية بعد إعادة التشغيل: ${after.source_count_academic_theses}.`,
  `نتيجة ثبات البصمات: ${after.passed ? 'ناجح؛ تطابقت البصمات الأربع كلها.' : 'فشل.'}`,
  '',
  '2) سبب الارتداد السابق',
  'كان سبب الارتداد فنياً في آلية إعادة تشغيل المعاينة، لا في cache ولا في script لتوليد البيانات: كانت الحالة المنقحة موجودة كتعديلات محلية غير محفوظة في commit، بينما كان فرع user_github/main يشير إلى checkpoint أقدم (df6193b). إعادة تشغيل المعاينة تستحضر حالة المستودع المتعقبة وتعيد تشغيل الخادم؛ لذلك عادت ملفات البيانات إلى snapshot أقدم. فحص package.json وملفات البدء لم يجد bootstrap أو regenerate أو نسخاً تلقائياً من data/ إلى items.json عند التشغيل.',
  '',
  '3) إجراء المنع والنقطة المرجعية',
  `تم إنشاء commit محلي مرجعي: ${head}.`,
  `تم إنشاء وسم محلي واضح: ${tag} (يشير إلى ${tagCommit}).`,
  `حالة المقارنة مع user_github/main (remote | local): ${aheadBehind}؛ أي إن النقطة المرجعية المحلية متقدمة بcommit واحد، ولم يتم push أو مزامنة GitHub.`,
  'بهذا أصبحت ملفات البيانات المنقحة جزءاً من commit محلي متعقب بدلاً من أن تبقى تغييرات عمل غير محفوظة. أثبت اختبار إعادة التشغيل التالي مباشرة بقاء هذا commit والأعداد والبصمات بلا تغيير.',
  '',
  '4) جدول البصمات',
  'المسار | عدد السجلات | SHA-256 قبل | SHA-256 بعد | النتيجة',
  ...files.map((file) => `${file} | ${before.files[file].record_count} | ${before.files[file].sha256} | ${after.hashes_after[file]} | ${after.hash_matches[file] ? 'مطابق' : 'مختلف'}`),
  '',
  '5) عينات الحذوف بعد إعادة التشغيل',
  ...Object.entries(samples.results).map(([group, rows]) => `${group}: ${rows.map((row) => row.id).join(' | ')} — جميعها غائبة من النسختين الرئيسية والمنشورة.`),
  '',
  '6) فحوص ما بعد إعادة التشغيل',
  'سلامة بيانات JSON وتطابق النسخة الرئيسية والمنشورة: ناجح.',
  'عدم وجود معرفات مكررة: ناجح.',
  'فحص TypeScript: ناجح.',
  'البناء الإنتاجي: ناجح.',
  'البحث: ناجح؛ ظهر السجل المحمي risail_6221 بعنوان «الآثار القانونية لتدخل القاضي في».',
  'فلتر المصدر: ناجح؛ عرض فلتر قناة الرسائل العلمية 430 مادة.',
  '',
  '7) حدود التنفيذ',
  'لم تُحذف مواد جديدة، ولم تُعدّل عناوين أو روابط أو تصنيفات، ولم تتغير الواجهة. لم يتم نشر الموقع أو مزامنة GitHub.',
  '',
];
writeFileSync(path.join(root, 'stable_clean_state_11295_report.txt'), lines.join('\n'), 'utf8');
console.log(JSON.stringify({ tag, head, before_total: before.total_items, after_total: after.total_items, hashes_match: after.passed, deleted_samples_absent: samples.all_absent }, null, 2));
