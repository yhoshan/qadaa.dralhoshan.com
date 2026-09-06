import { readFile, writeFile } from 'node:fs/promises';

const root = process.cwd();
const exportPath = '/home/ubuntu/upload/pasted_file_k9XHUn_result.json';
const unwrap = (raw) => Array.isArray(raw) ? raw : raw.items;
const normalize = (value = '') => String(value)
  .replace(/\.[A-Za-z0-9]{2,5}$/u, '')
  .replace(/[\u200e\u200f\u202a-\u202e\u2066-\u2069]/g, '')
  .normalize('NFKD')
  .replace(/[\u064B-\u065F\u0670]/g, '')
  .replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي')
  .toLowerCase().replace(/[\s_\-–—.,،:؛()\[\]{}]+/g, '');
const legalPattern = /قضائ|قضاء|محكم|محام|مرافع|تنفيذ|نظام|لائح|قانون|ادار|تحكيم|اثبات|شهاد|دعوى|عقد|شرك|تجار|افلاس|جنائ|عقوب|نياب|حقوق|عقار|تملك|تمويل|عمل|وظيف|اداري|طلاق|فسخ|حضانه|نفقه|ديوان|مظالم|صلح|موثق|وثيق|حراس/;
const exported = JSON.parse(await readFile(exportPath, 'utf8'));
const messages = exported.messages || [];
const items = unwrap(JSON.parse(await readFile(`${root}/items.json`, 'utf8')));
const currentTitles = new Map();
for (const item of items) {
  const key = normalize(item.title);
  if (!currentTitles.has(key)) currentTitles.set(key, []);
  currentTitles.get(key).push({ id: item.id, title: item.title, source: item.source });
}
const records = messages.filter((message) => message.type === 'message');
const files = records.filter((message) => message.file_name);
const links = records.filter((message) => (message.text_entities || []).some((entity) => entity.type === 'link' || entity.href || entity.url));
const likelyLegalFiles = files.filter((message) => legalPattern.test(`${message.file_name || ''} ${typeof message.text === 'string' ? message.text : ''}`));
const matchRows = likelyLegalFiles.map((message) => ({
  message_id: message.id,
  date: message.date,
  file_name: message.file_name,
  has_embedded_file: Boolean(message.file && message.file !== '(File not included. Change data exporting settings to download.)'),
  direct_urls: (message.text_entities || []).filter((entity) => entity.type === 'link' || entity.href || entity.url).map((entity) => entity.href || entity.url || entity.text).filter(Boolean),
  existing_matches: currentTitles.get(normalize(message.file_name)) || [],
}));
const exactMatches = matchRows.filter((row) => row.existing_matches.length);
const exactUnmatched = matchRows.filter((row) => !row.existing_matches.length);
const summary = {
  audited_at: new Date().toISOString(),
  channel_name: exported.name, channel_type: exported.type, channel_id: exported.id,
  total_messages: messages.length, ordinary_messages: records.length, file_messages: files.length,
  messages_with_url_entities: links.length, likely_legal_file_messages: likelyLegalFiles.length,
  likely_legal_exact_title_matches_in_current_items: exactMatches.length,
  likely_legal_titles_not_exactly_matched: exactUnmatched.length,
  file_payloads_included: matchRows.filter((row) => row.has_embedded_file).length,
  legal_rows: matchRows,
};
await writeFile(`${root}/lawlibrary_channel_export_audit.json`, `${JSON.stringify(summary, null, 2)}\n`);
await writeFile(`${root}/lawlibrary_channel_export_audit.txt`, [
  'تقييم ملف تصدير قناة مكتبة القانون',
  `اسم القناة في التصدير: ${exported.name}`,
  `نوع القناة: ${exported.type}`,
  `عدد الرسائل الكلي: ${messages.length}`,
  `عدد الرسائل العادية: ${records.length}`,
  `عدد الرسائل ذات الملفات: ${files.length}`,
  `عدد الرسائل ذات روابط ظاهرة: ${links.length}`,
  `عدد الملفات ذات الدلالة القانونية أو القضائية: ${likelyLegalFiles.length}`,
  `الملفات القانونية التي تطابق عنواناً قائماً حرفياً بعد التطبيع: ${exactMatches.length}`,
  `الملفات القانونية التي لا تطابق عنواناً قائماً حرفياً: ${exactUnmatched.length}`,
  `الملفات المضمنة فعلياً داخل التصدير: ${summary.file_payloads_included}`,
  '',
  'الحكم:',
  '- الملف مفيد بوصفه فهرساً وصفياً واسعاً لقناة مكتبة القانون، ويمكن أن يستخرج منه مرشحون قانونيون كثيرون.',
  '- لا يصلح للإضافة المباشرة في حالته الحالية، لأن معظم الرسائل تشير صراحة إلى أن الملف غير مضمن في التصدير، ولأن التصدير لا يقدم رابط فتح عام لكل ملف.',
  '- لا يُعد كل ملف غير مطابق عنواناً مادة جديدة؛ يلزم أولاً إثبات رابط فتح عام وتحقق موضوعي ومنع تكرار دلالي.',
  '',
  'عينة من العناوين القانونية غير المطابقة حرفياً:',
  ...exactUnmatched.slice(0, 30).map((row) => `- [${row.message_id}] ${row.file_name}`),
].join('\n'));
console.log(JSON.stringify({ total_messages: summary.total_messages, file_messages: summary.file_messages, url_entities: summary.messages_with_url_entities, likely_legal_files: summary.likely_legal_file_messages, exact_matches: summary.likely_legal_exact_title_matches_in_current_items, exact_unmatched: summary.likely_legal_titles_not_exactly_matched, included_payloads: summary.file_payloads_included }, null, 2));
