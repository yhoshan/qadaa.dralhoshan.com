import fs from 'node:fs/promises';

const root = process.cwd();
const candidatesData = JSON.parse(await fs.readFile(`${root}/promahmoud_arabic_legal_candidates.json`, 'utf8'));
const candidates = candidatesData.candidates ?? [];
const concurrency = 16;

async function check(candidate) {
  const started = Date.now();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(candidate.link_direct, {
      redirect: 'follow',
      signal: controller.signal,
      headers: { 'user-agent': 'Mozilla/5.0' },
    });
    const body = await response.text();
    const unavailable = /not found|page not found|file not found|خطأ 404|لم يتم العثور|الملف غير موجود/i.test(body);
    const login = /sign in|login|تسجيل الدخول/i.test(body) && response.url.includes('4shared');
    return {
      ...candidate,
      status: response.status,
      final_url: response.url,
      duration_ms: Date.now() - started,
      accessible: response.status >= 200 && response.status < 400 && !unavailable && !login,
      reason: response.status >= 200 && response.status < 400 && !unavailable && !login ? 'ACCESSIBLE' : (login ? 'LOGIN_REQUIRED' : 'UNAVAILABLE_CONTENT'),
    };
  } catch (error) {
    return {
      ...candidate,
      status: null,
      final_url: null,
      duration_ms: Date.now() - started,
      accessible: false,
      reason: error.name === 'AbortError' ? 'TIMEOUT' : `ERROR: ${error.message}`,
    };
  } finally {
    clearTimeout(timeout);
  }
}

const results = new Array(candidates.length);
let cursor = 0;
await Promise.all(Array.from({ length: Math.min(concurrency, candidates.length) }, async () => {
  while (true) {
    const index = cursor++;
    if (index >= candidates.length) return;
    results[index] = await check(candidates[index]);
  }
}));

const accessible = results.filter(row => row.accessible);
const unavailable = results.filter(row => !row.accessible);
const byHost = collection => Object.fromEntries([...collection.reduce((map, item) => {
  const host = item.final_url ? new URL(item.final_url).hostname : new URL(item.link_direct).hostname;
  map.set(host, (map.get(host) ?? 0) + 1);
  return map;
}, new Map()).entries()].sort((a, b) => b[1] - a[1]));
const output = {
  generated_at: new Date().toISOString(),
  totals: { checked: results.length, accessible: accessible.length, unavailable: unavailable.length },
  accessible_by_host: byHost(accessible),
  unavailable_by_host: byHost(unavailable),
  accessible,
  unavailable,
};
await fs.writeFile(`${root}/promahmoud_arabic_legal_link_validation.json`, JSON.stringify(output, null, 2));
await fs.writeFile(`${root}/promahmoud_arabic_legal_link_validation.txt`, [
  `فحص روابط المواد العربية القانونية لموقع الأستاذ محمود: ${output.generated_at}`,
  `المفحوص: ${results.length}`,
  `متاح: ${accessible.length}`,
  `مؤجل أو غير متاح: ${unavailable.length}`,
  `المتاح بحسب النطاق: ${JSON.stringify(output.accessible_by_host)}`,
  '',
  'المتاح:',
  ...accessible.map((item, index) => `${index + 1}. ${item.title} | ${item.status} | ${item.final_url}`),
  '',
  'المؤجل أو غير المتاح:',
  ...unavailable.map((item, index) => `${index + 1}. ${item.title} | ${item.reason}`),
].join('\n'));
console.log(JSON.stringify(output.totals));
