import fs from 'node:fs';
import path from 'node:path';

const root = '/home/ubuntu/makanez-qadaa';
const sources = [
  { key: 'theses', file: '/home/ubuntu/upload/pasted_file_f7Mdgb_result.json' },
  { key: 'network', file: '/home/ubuntu/upload/pasted_file_0NQfkI_result.json' },
];

const unwrap = (data) => Array.isArray(data) ? data : (Array.isArray(data.items) ? data.items : []);
const normalize = (value = '') => String(value)
  .normalize('NFKD')
  .replace(/[\u064B-\u065F\u0670\u0640]/g, '')
  .replace(/[أإآٱ]/g, 'ا')
  .replace(/ى/g, 'ي')
  .replace(/ة/g, 'ه')
  .replace(/[\p{P}\p{S}\s_]/gu, '')
  .toLowerCase();
const flatten = (value) => Array.isArray(value)
  ? value.map((v) => typeof v === 'string' ? v : (v?.text || '')).join('')
  : (typeof value === 'string' ? value : '');
const tidy = (value = '') => String(value)
  .replace(/[_]+/g, ' ')
  .replace(/\.(pdf|docx?|pptx?|xlsx?|zip|rar|mp3|mp4)$/iu, '')
  .replace(/\s+/g, ' ')
  .trim();
const extractTitle = (message) => {
  const text = flatten(message.text);
  const named = text.match(/(?:عنوان الرسالة|اسم الرسالة|أسم الرسالة|اسم الكتاب|أسم الكتاب|عنوان البحث|عنوان الدراسة|اسم البحث)\s*[:：-]+\s*([^\n]+)/iu)?.[1];
  return tidy(named || message.file_name || text.split('\n')[0] || '');
};
const extractAuthor = (message) => {
  const text = flatten(message.text);
  return tidy(text.match(/(?:المؤلف|اسم الباحث|أسم الباحث|الباحث)\s*[:：-]+\s*([^\n]+)/iu)?.[1] || '');
};

const legalSignals = /(?:القانون|قانوني|القضاء|قضائي|قاضي|محكمه|المحاكم|دعوي|الدعوى|مرافع|تحكيم|إثبات|الاثبات|جزائي|جنائي|جريمه|الجرائم|عقوبه|عقوبات|عقابي|ادعاء|دستور|دستوري|إداري|الاداري|تجاري|شركه|شركات|عقد|عقود|التزام|التزامات|مسؤوليه|المسؤولية|حقوق الانسان|الحريات|جنسية|تشريع|تشريعي|ضبط|الضبط|دولي|الدوليه|دولي|ملكية|الملكيه|إفلاس|الافلاس|ضريبي|الضريبة|ضريبه|ضريبة|مالي|المالية|عمل|عمال|تأمين|بنك|مصرف|قانون العمل|اجراءات|إجراءات|تنفيذ|تنفيذي|وقف|وصايه|وصاية|احوال شخصيه|الأحوال الشخصية|نظام قانوني|المركز القانوني|انظمه|أنظمة)/iu;
const clearNonLegal = /(?:ملزمه|ملزمة|محاضرات|منهج|مرحله|مرحلة|امتحان|اختبار|طلب|سؤال|اسئلة|أسئلة|وظائف|اعلان|إعلان|دوره|دورة|headway|اللغه العربية|الحاسوب|انكليزي|لغة إنجليزية|نحو|تجويد|عقيدة|تفسير|حديث نبوي|علوم القرآن|السيرة|أدب عربي|بلاغة)/iu;

const current = unwrap(JSON.parse(fs.readFileSync(path.join(root, 'items.json'), 'utf8')));
const existingTitles = new Set(current.map((item) => normalize(item.title)).filter(Boolean));
const existingLinks = new Set(current.map((item) => String(item.link_direct || item.link_telegram || '')).filter(Boolean));
const allCandidates = [];
const analysis = { generated_at: new Date().toISOString(), current_items: current.length, source_summaries: [], candidates: [], exclusions: [] };

for (const source of sources) {
  const data = JSON.parse(fs.readFileSync(source.file, 'utf8'));
  const messages = Array.isArray(data.messages) ? data.messages : [];
  const seen = new Set();
  const stats = { key: source.key, channel: data.name || '', channel_id: data.id || null, message_count: messages.length, file_messages: 0, candidate_count: 0, excluded_existing: 0, excluded_internal_duplicate: 0, excluded_nonlegal: 0, excluded_empty: 0 };
  for (const message of messages) {
    if (!message.file_name) continue;
    stats.file_messages += 1;
    const title = extractTitle(message);
    const author = extractAuthor(message);
    const key = normalize(title);
    if (!key || key.length < 5) { stats.excluded_empty += 1; continue; }
    if (existingTitles.has(key)) { stats.excluded_existing += 1; continue; }
    if (seen.has(key)) { stats.excluded_internal_duplicate += 1; continue; }
    if (clearNonLegal.test(title)) { stats.excluded_nonlegal += 1; continue; }
    if (!legalSignals.test(title)) { stats.excluded_nonlegal += 1; continue; }
    seen.add(key);
    const candidate = {
      input_source: source.key,
      channel: data.name || '',
      title,
      author,
      file_name: message.file_name,
      file_size: message.file_size || null,
      mime_type: message.mime_type || null,
      message_id: message.id,
      date: message.date || null,
      verification: 'title_reference_only',
      reason: 'ملف التصدير لا يتضمن رابطاً مباشراً أو مرفقاً قابلاً للفتح؛ يصلح كعنوان إحالي باسم القناة فقط.'
    };
    allCandidates.push(candidate);
    analysis.candidates.push(candidate);
    stats.candidate_count += 1;
  }
  analysis.source_summaries.push(stats);
}

const crossSeen = new Set();
analysis.candidates = analysis.candidates.filter((candidate) => {
  const key = normalize(candidate.title);
  if (crossSeen.has(key)) {
    analysis.exclusions.push({ title: candidate.title, input_source: candidate.input_source, reason: 'تكرار بين الملفين' });
    return false;
  }
  crossSeen.add(key);
  return true;
});
analysis.summary = {
  candidate_count_before_cross_dedupe: allCandidates.length,
  accepted_title_references: analysis.candidates.length,
  cross_file_duplicates: analysis.exclusions.length,
  total_file_messages: analysis.source_summaries.reduce((n, s) => n + s.file_messages, 0),
};

fs.writeFileSync(path.join(root, 'qanoon_network_channels_analysis.json'), JSON.stringify(analysis, null, 2));
const lines = [
  'تحليل قناتي شبكة قانونيون',
  `إجمالي ملفات التصدير: ${analysis.summary.total_file_messages}`,
  `عناوين قانونية جديدة مرشحة كسجلات إحالية: ${analysis.summary.accepted_title_references}`,
  `تكرارات بين الملفين: ${analysis.summary.cross_file_duplicates}`,
  '',
  ...analysis.source_summaries.map((s) => `${s.channel}: ملفات ${s.file_messages} | مرشحات ${s.candidate_count} | موجود سابقاً ${s.excluded_existing} | مكرر داخلياً ${s.excluded_internal_duplicate} | مستبعد غير قانوني ${s.excluded_nonlegal} | عنوان ناقص ${s.excluded_empty}`),
  '',
  'تنبيه: المرشحات لا تحوي روابط فتح مباشرة في التصدير، وهي معدة للمراجعة أو الإدخال كسجل عنوان فقط بناءً على توجيه المستخدم.',
];
fs.writeFileSync(path.join(root, 'qanoon_network_channels_analysis.txt'), lines.join('\n') + '\n');
