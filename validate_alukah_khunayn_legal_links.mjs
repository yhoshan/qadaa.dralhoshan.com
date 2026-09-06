import fs from 'node:fs/promises';

const root = process.cwd();
const queue = JSON.parse(await fs.readFile(`${root}/alukah_khunayn_legal_candidates.json`, 'utf8'));
const candidates = queue.candidates ?? [];
const concurrency = 12;

async function inspect(item) {
  const started = Date.now();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(item.link_direct, {
      redirect: 'follow',
      signal: controller.signal,
      headers: { 'user-agent': 'Mozilla/5.0' },
    });
    const text = await response.text();
    const titlePresent = text.includes(item.title.replace(/\s*\([^)]*\)\s*/g, '').trim().slice(0, 12));
    const unavailable = /not found|صفحة غير موجودة|لم يتم العثور/i.test(text);
    return {
      ...item,
      status: response.status,
      final_url: response.url,
      duration_ms: Date.now() - started,
      title_present: titlePresent,
      accessible: response.status >= 200 && response.status < 400 && !unavailable,
      reason: response.status >= 200 && response.status < 400 && !unavailable ? 'ACCESSIBLE' : 'UNAVAILABLE_CONTENT',
    };
  } catch (error) {
    return { ...item, status: null, final_url: null, duration_ms: Date.now() - started, title_present: false, accessible: false, reason: error.name === 'AbortError' ? 'TIMEOUT' : `ERROR: ${error.message}` };
  } finally {
    clearTimeout(timer);
  }
}

const results = new Array(candidates.length);
let cursor = 0;
await Promise.all(Array.from({ length: Math.min(concurrency, candidates.length) }, async () => {
  while (true) {
    const index = cursor++;
    if (index >= candidates.length) return;
    results[index] = await inspect(candidates[index]);
  }
}));

const accessible = results.filter(item => item.accessible);
const unavailable = results.filter(item => !item.accessible);
const output = {
  generated_at: new Date().toISOString(),
  totals: { checked: results.length, accessible: accessible.length, unavailable: unavailable.length },
  accessible,
  unavailable,
};
await fs.writeFile(`${root}/alukah_khunayn_legal_link_validation.json`, JSON.stringify(output, null, 2));
await fs.writeFile(`${root}/alukah_khunayn_legal_link_validation.txt`, [
  `فحص روابط الألوكة القضائية: ${output.generated_at}`,
  `المفحوص: ${results.length}`,
  `متاح: ${accessible.length}`,
  `غير متاح/مؤجل: ${unavailable.length}`,
  '',
  'المتاح:',
  ...accessible.map((item, index) => `${index + 1}. ${item.title} | ${item.status} | ${item.final_url}`),
  '',
  'المؤجل أو غير المتاح:',
  ...unavailable.map((item, index) => `${index + 1}. ${item.title} | ${item.reason}`),
].join('\n'));
console.log(JSON.stringify(output.totals));
