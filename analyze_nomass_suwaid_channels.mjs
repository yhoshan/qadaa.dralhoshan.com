import fs from 'node:fs';
import path from 'node:path';

const root = '/home/ubuntu/makanez-qadaa';
const inputs = [
  { key: 'nomass', file: '/home/ubuntu/upload/pasted_file_6YHVDs_result.json' },
  { key: 'suwaid', file: '/home/ubuntu/upload/pasted_file_liyIgE_result.json' },
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
  ? value.map((part) => typeof part === 'string' ? part : (part?.text || '')).join('')
  : (typeof value === 'string' ? value : '');
const tidy = (value = '') => String(value)
  .replace(/[\u200f\u200e\u2060]/g, '')
  .replace(/[_]+/g, ' ')
  .replace(/\.(pdf|docx?|pptx?|xlsx?|zip|rar|mp3|mp4|jpg|jpeg|png)$/iu, '')
  .replace(/[\u0640]/g, '')
  .replace(/\s+/g, ' ')
  .trim();
const legalSignals = /(?:قانون|قانوني|قضاء|قضائي|قاضي|محكمة|محاكم|دعوى|الدعوى|مرافعات|إثبات|اثبات|إقرار|شهادة|جنائي|جزائي|جريمة|جرائم|عقوبة|عقوبات|ادعاء|دستور|دستوري|إداري|اداري|تجاري|شركة|شركات|عقد|عقود|التزام|التزامات|مسؤولية|تعويض|ملكية|عقار|الرهن|إفلاس|افلاس|عمالي|عمل|عامل|موظف|تأمين|مصرف|ضريبة|ضريبي|تحكيم|وساطة|تنفيذ|مظالم|حقوق|حجز|وقف|وصاية|نظام|لائحة|لوائح|تشريع|الجنسية|أحوال شخصية|احوال شخصية)/iu;
const nonLegal = /(?:ملخص .*نظام|محاضرات|محاضرة|منهج|اختبار|امتحان|إعلان|اعلان|دورة|دورات|استشارة|استشارات|وظائف|توظيف|قروب|مجموعة واتساب|تفسير|عقيدة|حديث|فقه عبادة|تجويد|نحو|لغة إنجليزية|انجليزي|سيرة ذاتية|تهنئة|تغطية|فيديو|صور|IMG|^[0-9]+$)/iu;
const isGenericFileName = (value) => /^(?:[0-9]+|img[ _-]?[0-9]+|scan[ _-]?[0-9]+|document[ _-]?[0-9]+)$/iu.test(tidy(value));
const extractUrls = (message) => {
  const urls = [];
  for (const entity of message.text_entities || []) if (entity?.type === 'link' && /^https?:\/\//i.test(entity.text || '')) urls.push(entity.text);
  return [...new Set(urls)];
};
const deriveTitle = (message) => {
  const fileTitle = tidy(message.file_name || '');
  if (fileTitle && !isGenericFileName(fileTitle)) return { title: fileTitle, origin: 'file_name' };
  const text = tidy(flatten(message.text));
  if (!text || /^#/.test(text) || text.length > 180) return null;
  const clean = tidy(text.replace(/#[^\s]+/g, '').replace(/(?:👇🏻|👆🏻|✅|📌|🖊️|📚|💻|•)/g, ''));
  if (!clean || clean.length < 8 || clean.length > 160) return null;
  return { title: clean, origin: 'short_text' };
};

const current = unwrap(JSON.parse(fs.readFileSync(path.join(root, 'items.json'), 'utf8')));
const existingTitles = new Set(current.map((item) => normalize(item.title)).filter(Boolean));
const existingLinks = new Set(current.map((item) => item.link_direct || item.link_telegram || item.link_drive).filter(Boolean));
const candidateSeen = new Set();
const candidates = [];
const summary = [];

for (const input of inputs) {
  const data = JSON.parse(fs.readFileSync(input.file, 'utf8'));
  const stats = { key: input.key, channel: data.name || '', messages: (data.messages || []).length, candidates: 0, existing: 0, internal_duplicates: 0, excluded_nonlegal: 0, excluded_incomplete: 0, with_urls: 0 };
  for (const message of data.messages || []) {
    if (message.type !== 'message') continue;
    const result = deriveTitle(message);
    if (!result || !result.title) { stats.excluded_incomplete += 1; continue; }
    const { title, origin } = result;
    const key = normalize(title);
    if (!key || key.length < 5 || nonLegal.test(title) || !legalSignals.test(title)) { stats.excluded_nonlegal += 1; continue; }
    if (existingTitles.has(key)) { stats.existing += 1; continue; }
    if (candidateSeen.has(key)) { stats.internal_duplicates += 1; continue; }
    candidateSeen.add(key);
    const urls = extractUrls(message).filter((url) => !existingLinks.has(url));
    const candidate = { input_source: input.key, channel: data.name || '', title, origin, message_id: message.id, date: message.date || '', urls, text: tidy(flatten(message.text)) };
    candidates.push(candidate);
    stats.candidates += 1;
    if (urls.length) stats.with_urls += 1;
  }
  summary.push(stats);
}

const out = { generated_at: new Date().toISOString(), current_items: current.length, summaries: summary, candidates, total_candidates: candidates.length, candidates_with_urls: candidates.filter((item) => item.urls.length).length };
fs.writeFileSync(path.join(root, 'nomass_suwaid_channels_analysis.json'), JSON.stringify(out, null, 2));
const lines = [
  'تحليل قناتي شركة نوماس وشركة السويد',
  `إجمالي العناوين القانونية الجديدة المرشحة: ${out.total_candidates}`,
  `عناوين مرشحة مع روابط مضمّنة تحتاج تحققاً مستقلاً: ${out.candidates_with_urls}`,
  '',
  ...summary.map((s) => `${s.channel}: رسائل ${s.messages} | مرشحات ${s.candidates} | موجود سابقاً ${s.existing} | مكرر داخلياً ${s.internal_duplicates} | مستبعد غير قانوني ${s.excluded_nonlegal} | ناقص/غير صالح عنواناً ${s.excluded_incomplete} | بها روابط ${s.with_urls}`),
  '',
  'المرشحات بلا روابط تعامل كسجلات إحالية باسم القناة فقط. الروابط المضمنة لا تُعتمد إلا بعد فحص فتحها العام وصلة موردها.',
];
fs.writeFileSync(path.join(root, 'nomass_suwaid_channels_analysis.txt'), lines.join('\n') + '\n');
console.log(lines.join('\n'));
