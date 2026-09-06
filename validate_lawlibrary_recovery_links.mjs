import { readFile, writeFile } from 'node:fs/promises';

const root = process.cwd();
const source = JSON.parse(await readFile(`${root}/lawlibrary_recovery_candidates.json`, 'utf8'));
const candidates = source.candidates;
const timeoutMs = 15000;
const concurrency = 12;
const isLoginOrMissing = (finalUrl, body = '') => /login|signin|sign-in|accessdenied|not[ -]?found|404/i.test(`${finalUrl} ${body.slice(0, 600)}`);

async function inspect(candidate) {
  const url = candidate.link_direct || candidate.link_drive || candidate.link_telegram;
  const started = Date.now();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    let response = await fetch(url, { redirect: 'follow', signal: controller.signal, headers: { 'user-agent': 'Mozilla/5.0 (compatible; MakanezLinkVerifier/1.0)', range: 'bytes=0-4095' } });
    let body = '';
    try { body = await response.text(); } catch { /* Binary responses are not read as text. */ }
    const finalUrl = response.url || url;
    let status = 'UNAVAILABLE';
    if (response.status >= 200 && response.status < 400 && !isLoginOrMissing(finalUrl, body)) status = 'ACCESSIBLE';
    else if (response.status === 401 || response.status === 403 || response.status === 429 || response.status === 405 || response.status === 0) status = 'NEEDS_REVIEW';
    return { id: candidate.id, title: candidate.title, recovery_group: candidate.recovery_group, origin_source: candidate.source, url, final_url: finalUrl, http_status: response.status, content_type: response.headers.get('content-type') || '', status, duration_ms: Date.now() - started };
  } catch (error) {
    return { id: candidate.id, title: candidate.title, recovery_group: candidate.recovery_group, origin_source: candidate.source, url, final_url: '', http_status: null, content_type: '', status: error.name === 'AbortError' ? 'TIMEOUT' : 'ERROR', error: String(error.message || error), duration_ms: Date.now() - started };
  } finally { clearTimeout(timer); }
}

const results = new Array(candidates.length);
let cursor = 0;
async function worker() { while (true) { const index = cursor++; if (index >= candidates.length) return; results[index] = await inspect(candidates[index]); } }
await Promise.all(Array.from({ length: concurrency }, worker));
const summary = results.reduce((acc, row) => { acc[row.status] = (acc[row.status] || 0) + 1; return acc; }, {});
const byGroup = Object.fromEntries([...results.reduce((map, row) => { const item = map.get(row.recovery_group) || {}; item[row.status] = (item[row.status] || 0) + 1; map.set(row.recovery_group, item); return map; }, new Map()).entries()]);
const report = { verified_at: new Date().toISOString(), candidate_count: candidates.length, timeout_ms: timeoutMs, concurrency, summary, by_group: byGroup, results };
await writeFile(`${root}/lawlibrary_recovery_link_validation.json`, `${JSON.stringify(report, null, 2)}\n`);
await writeFile(`${root}/lawlibrary_recovery_link_validation_summary.txt`, [
  'تحقق فتح روابط استعادة مكتبة القانون',
  `إجمالي المرشحات: ${candidates.length}`,
  ...Object.entries(summary).map(([status, count]) => `- ${status}: ${count}`),
  '',
  'التوزيع بحسب المجموعة:',
  ...Object.entries(byGroup).map(([group, counts]) => `- ${group}: ${Object.entries(counts).map(([status, count]) => `${status} ${count}`).join(' | ')}`),
].join('\n'));
console.log(JSON.stringify({ candidate_count: candidates.length, summary, by_group: byGroup }, null, 2));
