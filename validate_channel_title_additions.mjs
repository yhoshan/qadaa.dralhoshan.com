import { readFile, writeFile } from 'node:fs/promises';
const root = process.cwd();
const [itemsText, publicText, statsText, statsPublicText, sanhouriBeforeText, channelsBeforeText] = await Promise.all([
  readFile(`${root}/items.json`, 'utf8'), readFile(`${root}/client/public/items.json`, 'utf8'),
  readFile(`${root}/stats.json`, 'utf8'), readFile(`${root}/client/public/stats.json`, 'utf8'),
  readFile(`${root}/backups/sanhouri_channel_titles_2026-09-06/items.before.json`, 'utf8'),
  readFile(`${root}/backups/philosophy_and_legal_libraries_titles_2026-09-06/items.before.json`, 'utf8'),
]);
const items = JSON.parse(itemsText), stats = JSON.parse(statsText), sanhouriBefore = JSON.parse(sanhouriBeforeText), channelsBefore = JSON.parse(channelsBeforeText);
const norm = (v = '') => String(v).normalize('NFKD').replace(/[\u064B-\u065F\u0670]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي').toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');
const ids = new Set(), duplicateIds = [];
for (const item of items) { if (ids.has(item.id)) duplicateIds.push(item.id); ids.add(item.id); }
const titleOnly = items.filter(i => /^sanhouri_\d+$|^philosophy_law_\d+$|^iirmll_title_\d+$/.test(i.id || ''));
const sanhouriBeforeTitleSet = new Set(sanhouriBefore.map(i => norm(i.title)));
const channelsBeforeTitleSet = new Set(channelsBefore.map(i => norm(i.title)));
const sanhouriRows = titleOnly.filter(i => i.source === 'ملخصات القانون (مكتبة السنهوري)');
const channelRows = titleOnly.filter(i => i.source === 'مكتبة فلسفة القانون' || i.source === 'المكتبة القانونية ⚖️');
const candidatesDuplicatePrior = [
  ...sanhouriRows.filter(i => sanhouriBeforeTitleSet.has(norm(i.title))),
  ...channelRows.filter(i => channelsBeforeTitleSet.has(norm(i.title))),
];
const bySource = Object.fromEntries([...titleOnly.reduce((m, i) => m.set(i.source, (m.get(i.source) || 0) + 1), new Map()).entries()]);
const result = { total: items.length, data_match: itemsText === publicText, stats_match: statsText === statsPublicText, stats_total: stats.total_items, duplicate_ids: duplicateIds.length, title_reference_counts: bySource, total_title_references: titleOnly.length, title_reference_duplicate_prior: candidatesDuplicatePrior.length, title_reference_shape_valid: titleOnly.every(i => i.material_type === 'عنوان مرجعي' && i.file_type === 'عنوان' && Number(i.download_links_count || 0) === 0 && !i.link_direct), expected_sanhouri: 104, expected_philosophy: 179, expected_legal_library: 540 };
result.passed = result.data_match && result.stats_match && result.stats_total === result.total && result.duplicate_ids === 0 && result.title_reference_duplicate_prior === 0 && result.title_reference_shape_valid && bySource['ملخصات القانون (مكتبة السنهوري)'] === 104 && bySource['مكتبة فلسفة القانون'] === 179 && bySource['المكتبة القانونية ⚖️'] === 540;
await writeFile(`${root}/channel_title_additions_post_validation.json`, `${JSON.stringify(result, null, 2)}\n`);
console.log(JSON.stringify(result, null, 2));
if (!result.passed) process.exit(1);
