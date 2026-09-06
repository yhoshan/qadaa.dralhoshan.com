import { readFile, writeFile } from 'node:fs/promises';

const root = process.cwd();
const sources = [
  { path: '/home/ubuntu/upload/pasted_file_FRXVXW_result.json', source: 'مكتبة فلسفة القانون', channel: 'https://t.me/philosophyoflaw2024', family: 'philosophy' },
  { path: '/home/ubuntu/upload/pasted_file_IEMmm9_result.json', source: 'المكتبة القانونية ⚖️', channel: 'https://t.me/iirmll', family: 'library' },
];
const stripExt = (value = '') => String(value).replace(/\.(pdf|docx?|xlsx?|pptx?|zip|rar|jpg|png)$/iu, '');
const clean = (value = '') => stripExt(value).replace(/[_@]+/g, ' ').replace(/\s+/g, ' ').replace(/^[\-–—\s.]+|[\-–—\s.]+$/g, '').trim();
const norm = (value = '') => clean(value).normalize('NFKD').replace(/[\u064B-\u065F\u0670]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي').toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');
const legal = /قانون|قانوني|قضائي|قضاء|محكم|محاكم|قاضي|مراف|دعوى|دعوي|تنفيذ|اثبات|بينه|شهاد|تحكيم|وساط|تشريع|تشريعي|لائح|نظام|انظمه|دستور|دستوري|جناي|جريم|عقوب|نياب|تحقيق|سجن|محام|محامي|محاماه|عقد|عقود|التزام|مدني|تجاري|شرك|افلاس|شيك|اوراق تجاري|ضريب|جمارك|عقار|ايجار|تملك|عمال|عمل|توظيف|عداله|حقوق|موظف عام|اداري|اداره عامه|دوله|سلطه|انتخاب|منافس|مشتري|تاديب|تأديب|توقيف|اجراءات|تدابير|حمايه|خصوصيه|اعلام قانوني/i;
const exclude = /^(?:\d+|ملف|كتاب جديد|قوانين|law|test)$|ملخص محاضر|محاضره نهائيه|اسئل|سوال|اجاب|اجابة|اختبار|واجب|اعلان|وظيف|سيره ذاتيه|طلبات|دعايه|دورة|دورات|شهاده حضور|جدول|تكليف|واجبات|محاضرات|سكشن|مقرر|lecture|course/iu;
const currentRaw = JSON.parse(await readFile(`${root}/items.json`, 'utf8'));
const current = Array.isArray(currentRaw) ? currentRaw : currentRaw.items;
const currentByTitle = new Map();
const currentByUrl = new Map();
for (const item of current) {
  const title = norm(item.title);
  if (title && !currentByTitle.has(title)) currentByTitle.set(title, { id: item.id, source: item.source, title: item.title });
  for (const url of [item.link_direct, item.link_telegram, item.link_drive]) if (url && !currentByUrl.has(String(url).trim())) currentByUrl.set(String(url).trim(), { id: item.id, source: item.source, title: item.title });
}
const all = { total_files: 0, likely_legal: 0, existing: 0, internal_duplicate: 0, excluded: 0, candidates: [], existing_matches: [], excluded_rows: [], sources: [] };
const candidateKeys = new Set();
for (const cfg of sources) {
  const exportData = JSON.parse(await readFile(cfg.path, 'utf8'));
  const messages = (exportData.messages || []).filter(m => m.type === 'message' && m.file_name);
  const sourceResult = { source: cfg.source, channel: cfg.channel, total_messages: (exportData.messages || []).length, file_messages: messages.length, likely_legal: 0, existing: 0, internal_duplicate: 0, excluded: 0, candidates: 0 };
  const seen = new Set();
  for (const message of messages) {
    const title = clean(message.file_name);
    const key = norm(title);
    if (!key || exclude.test(title)) { sourceResult.excluded++; all.excluded++; all.excluded_rows.push({ source: cfg.source, message_id: message.id, title, reason: !key ? 'عنوان فارغ أو رمزي' : 'تدريب أو إعلان أو مادة دراسية عامة' }); continue; }
    if (!legal.test(title)) { sourceResult.excluded++; all.excluded++; all.excluded_rows.push({ source: cfg.source, message_id: message.id, title, reason: 'لا تظهر دلالة قانونية أو قضائية كافية في العنوان' }); continue; }
    sourceResult.likely_legal++; all.likely_legal++;
    if (currentByTitle.has(key)) { sourceResult.existing++; all.existing++; all.existing_matches.push({ source: cfg.source, message_id: message.id, title, existing: currentByTitle.get(key), reason: 'عنوان مطابق في المكنز' }); continue; }
    if (seen.has(key) || candidateKeys.has(key)) { sourceResult.internal_duplicate++; all.internal_duplicate++; all.existing_matches.push({ source: cfg.source, message_id: message.id, title, reason: 'تكرار داخل الملفين' }); continue; }
    seen.add(key); candidateKeys.add(key);
    const candidate = { source: cfg.source, channel: cfg.channel, message_id: message.id, date: message.date, title, file_name: message.file_name, file_size: message.file_size || 0, mime_type: message.mime_type || '', material_type: cfg.family === 'philosophy' ? 'كتاب' : 'رابط مرجعي', category: cfg.family === 'philosophy' ? 'فلسفة القانون ونظرية الدولة' : 'القضاء والأنظمة والمحاماة' };
    all.candidates.push(candidate); sourceResult.candidates++;
  }
  all.total_files += messages.length;
  all.sources.push(sourceResult);
}
await writeFile(`${root}/new_legal_channels_analysis.json`, `${JSON.stringify(all, null, 2)}\n`);
await writeFile(`${root}/new_legal_channels_analysis.txt`, [
  'تحليل ملفي مكتبة فلسفة القانون والمكتبة القانونية',
  `إجمالي رسائل الملفات: ${all.total_files}`,
  `عناوين قانونية أو قضائية محتملة: ${all.likely_legal}`,
  `مطابقات قائمة في المكنز: ${all.existing}`,
  `تكرارات داخل الملفين: ${all.internal_duplicate}`,
  `مستبعدات أولية: ${all.excluded}`,
  `مرشحات جديدة بعد منع التكرار: ${all.candidates.length}`,
  '',
  ...all.sources.map(s => `${s.source}: ملفات ${s.file_messages} | قانونية محتملة ${s.likely_legal} | موجودة ${s.existing} | مكررة ${s.internal_duplicate} | مستبعدة ${s.excluded} | جديدة ${s.candidates}`),
  '', 'أول 60 مرشحاً جديداً:', ...all.candidates.slice(0, 60).map((c, index) => `${index + 1}. [${c.source}] ${c.title}`),
  '', 'الضابط: هذا تقرير فحص فقط. لا تدخل العناوين قبل اعتماد طريقة التعامل مع روابط القناتين أو الاكتفاء بالإحالة باسم القناة.'
].join('\n'));
console.log(JSON.stringify({ total_files: all.total_files, likely_legal: all.likely_legal, existing: all.existing, internal_duplicate: all.internal_duplicate, excluded: all.excluded, candidates: all.candidates.length, sources: all.sources }, null, 2));
