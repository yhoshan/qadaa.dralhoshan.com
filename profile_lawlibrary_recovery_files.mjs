import { readFile, writeFile } from 'node:fs/promises';

const root = process.cwd();
const uploadRoot = '/home/ubuntu/upload';
const files = [
  'pasted_file_Ccz0Dd_moj_official_journals_new_titles_2026-08-28.json',
  'pasted_file_DsF63l_lawlibrarysa_MASTER_v6_merge_ready_310.json',
  'pasted_file_SvnUyP_lawlibrarysa_merge_ready_140.json',
  'pasted_file_iRj0dd_kku_uqu_legal_new_titles_2026-08-28.json',
  'pasted_file_VzsweO_ksu_law_political_science_new_titles_2026-08-28.json',
  'pasted_file_RMtfOF_kau_qassim_legal_new_titles_2026-08-28.json',
  'pasted_file_OsPkHo_ajsrp_saudi_legal_new_titles_24_2026-08-28.json',
  'pasted_file_7JojVM_majmaah_imam_legal_new_titles_2026-08-28.json',
];
const profiles = [];
for (const filename of files) {
  const raw = JSON.parse(await readFile(`${uploadRoot}/${filename}`, 'utf8'));
  const entries = Array.isArray(raw) ? raw : (raw.items || raw.messages || []);
  const keyCounts = new Map();
  let stringTitle = 0; let nonemptyTitle = 0; let directLink = 0;
  for (const entry of entries) {
    for (const key of Object.keys(entry || {})) keyCounts.set(key, (keyCounts.get(key) || 0) + 1);
    if (typeof entry?.title === 'string') { stringTitle += 1; if (entry.title.trim()) nonemptyTitle += 1; }
    if (typeof entry?.link_direct === 'string' && entry.link_direct.trim()) directLink += 1;
  }
  profiles.push({ filename, top_level_type: Array.isArray(raw) ? 'array' : typeof raw, entry_count: entries.length, title_field_count: stringTitle, nonempty_title_count: nonemptyTitle, direct_link_count: directLink, keys: Object.fromEntries([...keyCounts.entries()].sort((a,b) => b[1] - a[1])) });
}
await writeFile(`${root}/lawlibrary_recovery_file_profiles.json`, `${JSON.stringify(profiles, null, 2)}\n`);
await writeFile(`${root}/lawlibrary_recovery_file_profiles.txt`, profiles.map((profile) => [
  profile.filename,
  `- السجلات: ${profile.entry_count}`,
  `- حقل العنوان: ${profile.title_field_count}؛ عناوين غير فارغة: ${profile.nonempty_title_count}`,
  `- روابط مباشرة: ${profile.direct_link_count}`,
  `- الحقول: ${Object.keys(profile.keys).join('، ')}`,
].join('\n')).join('\n\n'));
console.log(JSON.stringify(profiles.map(({ filename, entry_count, title_field_count, nonempty_title_count, direct_link_count }) => ({ filename, entry_count, title_field_count, nonempty_title_count, direct_link_count })), null, 2));
