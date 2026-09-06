import fs from 'node:fs/promises';

const root = process.cwd();
const input = JSON.parse(await fs.readFile(`${root}/staralgeria_legal_candidates.json`, 'utf8'));
const genericBundles = /^(?:رسائل\s+ماجي(?:س|س)تر\s*\d+|بحوث\s*\d*|مذكرات\s*\d*)$/u;
const badText = /(file (?:is )?not found|file (?:has been )?deleted|404 not found|page not found|login required|sign in|access denied|forbidden|captcha|cloudflare)/iu;

function normalizeUrl(url) { return String(url).trim().replace(/^http:\/\//iu, 'https://'); }
async function sampleBody(response) {
  if (!response.body) return '';
  const reader = response.body.getReader();
  const chunks = [];
  let total = 0;
  try {
    while (total < 65536) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
      total += value.length;
    }
  } finally {
    await reader.cancel().catch(() => {});
  }
  return new TextDecoder('utf-8', { fatal: false }).decode(Buffer.concat(chunks));
}
async function verify(row) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(normalizeUrl(row.url), { redirect: 'follow', signal: controller.signal, headers: { 'user-agent': 'Mozilla/5.0 (compatible; MakanezResearch/1.0)', accept: '*/*' } });
    const type = response.headers.get('content-type') || '';
    const finalUrl = response.url || normalizeUrl(row.url);
    let body = '';
    if (/text|html|json|xml|javascript/iu.test(type) || !type) body = await sampleBody(response);
    const isErrorPage = badText.test(body);
    const accessible = response.status >= 200 && response.status < 400 && !isErrorPage;
    return { title: row.title, source_url: row.url, final_url: finalUrl, http_status: response.status, content_type: type, is_publicly_open: accessible, reason: accessible ? 'الرابط يفتح للعامة دون خطأ ظاهر' : isErrorPage ? 'صفحة خطأ أو حاجز وصول ظاهر' : `حالة HTTP ${response.status}` };
  } catch (error) {
    return { title: row.title, source_url: row.url, final_url: '', http_status: 0, content_type: '', is_publicly_open: false, reason: error.name === 'AbortError' ? 'انتهت مهلة الاتصال' : `تعذر الاتصال: ${error.message}` };
  } finally {
    clearTimeout(timeout);
  }
}
async function concurrentMap(rows, limit, worker) {
  const result = [];
  let cursor = 0;
  await Promise.all(Array.from({ length: Math.min(limit, rows.length) }, async () => {
    while (cursor < rows.length) {
      const index = cursor++;
      result[index] = await worker(rows[index]);
    }
  }));
  return result;
}

const skipped = [];
const seenUrl = new Map();
const toVerify = [];
for (const row of input.candidates) {
  if (genericBundles.test(row.title)) {
    skipped.push({ title: row.title, source_url: row.url, reason: 'عنوان حزمة عامة لا يحدد مادة قانونية مستقلة' });
    continue;
  }
  const key = normalizeUrl(row.url);
  if (seenUrl.has(key)) {
    skipped.push({ title: row.title, source_url: row.url, reason: `رابط مكرر مع: ${seenUrl.get(key)}` });
    continue;
  }
  seenUrl.set(key, row.title);
  toVerify.push(row);
}
const verified = await concurrentMap(toVerify, 8, verify);
const open = verified.filter((row) => row.is_publicly_open);
const closed = verified.filter((row) => !row.is_publicly_open);
const output = { generated_at: new Date().toISOString(), source_page: input.source_page, totals: { initial_candidates: input.candidates.length, direct_urls_to_verify: toVerify.length, publicly_open: open.length, unavailable: closed.length, skipped: skipped.length }, open, closed, skipped };
await fs.writeFile(`${root}/staralgeria_link_verification.json`, JSON.stringify(output, null, 2));
await fs.writeFile(`${root}/staralgeria_link_verification.txt`, [
  `المصدر: ${input.source_page}`,
  `مرشحات مبدئية: ${output.totals.initial_candidates}`,
  `روابط فريدة تم اختبارها: ${output.totals.direct_urls_to_verify}`,
  `روابط مفتوحة للعامة: ${output.totals.publicly_open}`,
  `روابط متعذرة أو محجوبة: ${output.totals.unavailable}`,
  `عناوين مستبعدة لكونها حزم عامة أو بروابط مكررة: ${output.totals.skipped}`,
  '',
  'الروابط المفتوحة:',
  ...open.map((row, index) => `${index + 1}. ${row.title}\n   ${row.final_url}\n   ${row.reason}`),
  '',
  'الروابط المتعذرة:',
  ...closed.map((row, index) => `${index + 1}. ${row.title} | ${row.reason}`),
  '',
  'المستبعدة:',
  ...skipped.map((row, index) => `${index + 1}. ${row.title} | ${row.reason}`),
].join('\n'));
console.log(JSON.stringify(output.totals));
