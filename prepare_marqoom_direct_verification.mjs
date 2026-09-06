import fs from 'node:fs/promises';

const root = process.cwd();
const result = JSON.parse(await fs.readFile('/home/ubuntu/verify_marqoom_legal_pages.json', 'utf8'));
const rows = result.results
  .filter((row) => !row.error && row.output?.is_publicly_open && row.output?.legal_relevance && row.output?.public_file_link)
  .map((row) => ({
    title: String(row.output.title ?? row.input.split(' | ')[0]).replace(/\s*\(\s*\d+\s*(?:حقق|نظم)\s*\)\s*$/u, '').trim(),
    page_url: row.output.final_url || row.output.url,
    file_url: row.output.public_file_link,
    page_status: row.output.page_status,
  }));
const seen = new Set();
const unique = rows.filter((row) => {
  const key = `${row.title}\u0000${row.file_url}`;
  if (seen.has(key)) return false;
  seen.add(key);
  return true;
});
await fs.writeFile(`${root}/marqoom_direct_links_to_verify.json`, JSON.stringify({ generated_at: new Date().toISOString(), totals: { verified_pages: unique.length, subtask_failures: result.results.filter((row) => row.error).length }, rows: unique }, null, 2));
await fs.writeFile(`${root}/marqoom_direct_links_to_verify.txt`, unique.map((row, index) => `${index + 1}. ${row.title}\n   ${row.file_url}\n   الصفحة: ${row.page_url}`).join('\n'));
console.log(JSON.stringify({ verified_pages: unique.length, subtask_failures: result.results.filter((row) => row.error).length }));
