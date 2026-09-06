import { readFile, writeFile } from 'node:fs/promises';
const root = process.cwd();
const candidates = JSON.parse(await readFile(`${root}/lawlibrary_early_site_recovery_candidates.json`, 'utf8'));
const timeoutMs = 15000; let cursor = 0; const results = new Array(candidates.length);
async function check(item) {
  const controller = new AbortController(); const timer = setTimeout(() => controller.abort(), timeoutMs); const started = Date.now();
  try {
    const response = await fetch(item.link_direct, { redirect: 'follow', signal: controller.signal, headers: { 'user-agent': 'Mozilla/5.0 (compatible; MakanezLinkVerifier/1.0)', range: 'bytes=0-4095' } });
    const finalUrl = response.url || item.link_direct; let body = ''; try { body = await response.text(); } catch {}
    const closed = /login|signin|sign-in|accessdenied|not[ -]?found|404/i.test(`${finalUrl} ${body.slice(0, 600)}`);
    return { ...item, http_status: response.status, final_url: finalUrl, status: response.status >= 200 && response.status < 400 && !closed ? 'ACCESSIBLE' : (response.status === 401 || response.status === 403 || response.status === 429 || response.status === 405 ? 'NEEDS_REVIEW' : 'UNAVAILABLE'), duration_ms: Date.now() - started };
  } catch (error) { return { ...item, http_status: null, final_url: '', status: error.name === 'AbortError' ? 'TIMEOUT' : 'ERROR', error: String(error.message || error), duration_ms: Date.now() - started }; } finally { clearTimeout(timer); }
}
async function worker() { while (true) { const index = cursor++; if (index >= candidates.length) return; results[index] = await check(candidates[index]); } }
await Promise.all(Array.from({ length: 8 }, worker));
const summary = results.reduce((map, item) => { map[item.status] = (map[item.status] || 0) + 1; return map; }, {});
await writeFile(`${root}/lawlibrary_early_site_link_validation.json`, `${JSON.stringify({ verified_at: new Date().toISOString(), summary, results }, null, 2)}\n`);
await writeFile(`${root}/lawlibrary_early_site_link_validation.txt`, ['تحقق روابط الدفعة الأسبق من موقع مكتبة القانون', ...Object.entries(summary).map(([status, count]) => `- ${status}: ${count}`), '', ...results.map((item) => `- ${item.status} | ${item.http_status ?? '-'} | ${item.title} | ${item.link_direct}`)].join('\n'));
console.log(JSON.stringify({ count: candidates.length, summary }, null, 2));
