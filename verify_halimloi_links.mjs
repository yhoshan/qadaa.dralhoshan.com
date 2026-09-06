import fs from 'node:fs/promises';

const root = process.cwd();
const input = JSON.parse(await fs.readFile(`${root}/halimloi_legal_candidates.json`, 'utf8'));
const badText = /(404|not found|page not found|file (?:is )?not found|login required|sign in|access denied|forbidden|captcha|cloudflare|لم يتم العثور|غير موجود)/iu;

function normalizedUrl(url) { return String(url).trim().replace(/^http:\/\//iu, 'https://'); }
async function bodySample(response) {
  if (!response.body) return '';
  const reader = response.body.getReader();
  const chunks = [];
  let bytes = 0;
  try {
    while (bytes < 65536) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
      bytes += value.length;
    }
  } finally {
    await reader.cancel().catch(() => {});
  }
  return new TextDecoder('utf-8', { fatal: false }).decode(Buffer.concat(chunks));
}
async function verify(item) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(normalizedUrl(item.link_direct), {
      signal: controller.signal,
      redirect: 'follow',
      headers: { 'user-agent': 'Mozilla/5.0 (compatible; MakanezResearch/1.0)', accept: 'text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8' },
    });
    const contentType = response.headers.get('content-type') || '';
    const body = /text|html|json|xml|javascript/iu.test(contentType) || !contentType ? await bodySample(response) : '';
    const isError = badText.test(body);
    const isOpen = response.status >= 200 && response.status < 400 && !isError;
    return { title: item.title, source_url: item.link_direct, final_url: response.url || normalizedUrl(item.link_direct), http_status: response.status, content_type: contentType, is_publicly_open: isOpen, reason: isOpen ? 'تفتح صفحة المادة للعامة دون خطأ ظاهر' : isError ? 'صفحة خطأ أو حاجز وصول ظاهر' : `حالة HTTP ${response.status}` };
  } catch (error) {
    return { title: item.title, source_url: item.link_direct, final_url: '', http_status: 0, content_type: '', is_publicly_open: false, reason: error.name === 'AbortError' ? 'انتهت مهلة الاتصال' : `تعذر الاتصال: ${error.message}` };
  } finally {
    clearTimeout(timeout);
  }
}
async function concurrentMap(rows, limit) {
  const result = [];
  let cursor = 0;
  await Promise.all(Array.from({ length: Math.min(limit, rows.length) }, async () => {
    while (cursor < rows.length) {
      const index = cursor++;
      result[index] = await verify(rows[index]);
    }
  }));
  return result;
}
const results = await concurrentMap(input.candidates, 8);
const open = results.filter((item) => item.is_publicly_open);
const unavailable = results.filter((item) => !item.is_publicly_open);
const output = { generated_at: new Date().toISOString(), source: input.source, source_page: input.source_page, totals: { candidates: input.candidates.length, publicly_open: open.length, unavailable: unavailable.length }, open, unavailable };
await fs.writeFile(`${root}/halimloi_link_verification.json`, JSON.stringify(output, null, 2));
await fs.writeFile(`${root}/halimloi_link_verification.txt`, [
  `المصدر: ${input.source}`,
  `صفحة الإحالة: ${input.source_page}`,
  `روابط تم فحصها: ${output.totals.candidates}`,
  `روابط عامة مثبتة: ${output.totals.publicly_open}`,
  `روابط متعذرة أو محجوبة: ${output.totals.unavailable}`,
  '',
  'المتاحة:',
  ...open.map((item, index) => `${index + 1}. ${item.title}\n   ${item.final_url}`),
  '',
  'المتعذرة:',
  ...unavailable.map((item, index) => `${index + 1}. ${item.title} | ${item.reason}`),
].join('\n'));
console.log(JSON.stringify(output.totals));
