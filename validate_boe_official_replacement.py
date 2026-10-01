#!/usr/bin/env python3
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/home/ubuntu/makanez-qadaa')
BACKUP = ROOT / 'backups/boe_official_replacement_2026-09-29'
ADD_CSV = Path('/home/ubuntu/upload/pasted_file_rCwoBj_qadaa_add_boe_official_538.csv')
DELETE_CSV = Path('/home/ubuntu/upload/pasted_file_ClHru3_qadaa_remove_intermediary_226.csv')
MANIFEST = Path('/home/ubuntu/upload/pasted_file_pN8Ytn_qadaa_boe_execution_manifest.json')
REPORT = ROOT / 'boe_official_replacement_2026-09-29_validation.json'
PREFIX = 'https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/'

def read_items(path):
    data = json.loads(path.read_text(encoding='utf-8'))
    return data if isinstance(data, list) else data['items']

def norm(value=''):
    return str(value).translate(str.maketrans({'أ':'ا','إ':'ا','آ':'ا','ٱ':'ا','ى':'ي','ة':'ه'})).lower().strip()

def sha256_text(text):
    return hashlib.sha256(text.encode()).hexdigest()

before_text = (BACKUP / 'items.before.json').read_text(encoding='utf-8')
final_text = (ROOT / 'items.json').read_text(encoding='utf-8')
public_text = (ROOT / 'client/public/items.json').read_text(encoding='utf-8')
stats_text = (ROOT / 'stats.json').read_text(encoding='utf-8')
public_stats_text = (ROOT / 'client/public/stats.json').read_text(encoding='utf-8')
cache_text = (ROOT / 'client/src/hooks/useItems.ts').read_text(encoding='utf-8')
before = read_items(BACKUP / 'items.before.json')
final = read_items(ROOT / 'items.json')
public = read_items(ROOT / 'client/public/items.json')
stats = json.loads(stats_text)
adds = list(csv.DictReader(ADD_CSV.open(encoding='utf-8-sig', newline='')))
deletes = list(csv.DictReader(DELETE_CSV.open(encoding='utf-8-sig', newline='')))
manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))

before_by_id = {x['id']: x for x in before}
final_by_id = {x['id']: x for x in final}
add_boe_ids = {row['boe_id'] for row in adds}
remove_ids = {row['current_id'] for row in deletes}
protected_moj_ids = {row['id'] for row in manifest['protected_moj']}
official_items = [x for x in final if x['id'].startswith('boe_')]
official_boe_ids = [x.get('boe_id') for x in official_items]
actual_removed = set(before_by_id) - set(final_by_id)
actual_added = set(final_by_id) - set(before_by_id)
duplicate_item_ids = len(final) - len(final_by_id)
duplicate_boe_ids = len(official_boe_ids) - len(set(official_boe_ids))
non_target_changed = [
    item_id for item_id, before_item in before_by_id.items()
    if item_id not in remove_ids and final_by_id.get(item_id) != before_item
]
search_matches = [
    x for x in final
    if norm('نظام التنفيذ') in norm(' '.join(str(x.get(k, '')) for k in ['title','author','investigator','category','source']))
]
type_filter = [x for x in final if x.get('material_type') == 'نظام']
failures = []
def require(condition, message):
    if not condition:
        failures.append(message)

require(len(before) == 17178, 'unexpected pre-change count')
require(len(final) == 17490 and len(public) == 17490, 'final count mismatch')
require(final_text == public_text, 'main/public items bytes mismatch')
require(stats_text == public_stats_text, 'main/public stats bytes mismatch')
require(len(adds) == 538 and len(add_boe_ids) == 538, 'addition input mismatch')
require(len(deletes) == 226 and len(remove_ids) == 226, 'deletion input mismatch')
require(actual_removed == remove_ids and len(actual_removed) == 226, 'unexpected removal set')
require(actual_added == {f'boe_{x}' for x in add_boe_ids} and len(actual_added) == 538, 'unexpected addition set')
require(not (remove_ids & set(final_by_id)), 'a listed removal id remains')
require(all(f'boe_{x}' in final_by_id for x in add_boe_ids), 'an official BOE addition is missing')
require(len(official_items) == 538, 'official BOE record count mismatch')
require(len(set(official_boe_ids)) == 538 and not any(x is None for x in official_boe_ids), 'BOE ID duplication or missing value')
require(all(x.get('link_direct','').startswith(PREFIX) for x in official_items), 'invalid official URL')
require(all(item_id in final_by_id for item_id in protected_moj_ids), 'protected MOJ record missing')
require(not non_target_changed, 'non-target record changed')
require(duplicate_item_ids == 0, 'duplicate item id')
require(duplicate_boe_ids == 0, 'duplicate BOE id')
require(stats.get('total_items') == 17490, 'stats total mismatch')
require(stats.get('qadaa_count',0) + stats.get('nizam_count',0) + stats.get('mohama_count',0) == 17490, 'hero counters mismatch')
require('boe-official-canonical-538-2026-09-29' in cache_text, 'cache buster not updated')
require('moj-official-documents-2026-09-28' not in cache_text, 'previous cache buster remains')
require('boe_67dd54bc-c33a-48c8-8356-b44700a9ab55' in {x['id'] for x in search_matches}, 'normalized search test failed')
require(len(type_filter) >= 538 and all(x.get('material_type') == 'نظام' for x in official_items), 'material-type filter test failed')

report = {
    'validated_at_utc': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'),
    'passed': not failures,
    'failures': failures,
    'before_total': len(before),
    'official_added': len(official_items),
    'intermediaries_removed': len(actual_removed),
    'after_total': len(final),
    'no_listed_removal_id_remains': not bool(remove_ids & set(final_by_id)),
    'boe_id_duplicates': duplicate_boe_ids,
    'item_id_duplicates': duplicate_item_ids,
    'official_urls_valid': sum(x.get('link_direct','').startswith(PREFIX) for x in official_items),
    'protected_moj_preserved': sorted(protected_moj_ids & set(final_by_id)),
    'non_target_records_changed': len(non_target_changed),
    'main_public_items_match': final_text == public_text,
    'main_public_stats_match': stats_text == public_stats_text,
    'hero_counts': {'qadaa':stats['qadaa_count'], 'nizam':stats['nizam_count'], 'mohama':stats['mohama_count']},
    'search_test': {'query':'نظام التنفيذ','match_count':len(search_matches),'official_execution_found':'boe_67dd54bc-c33a-48c8-8356-b44700a9ab55' in {x['id'] for x in search_matches}},
    'material_type_filter_test': {'value':'نظام','result_count':len(type_filter),'all_official_records_match':all(x.get('material_type')=='نظام' for x in official_items)},
    'file_hashes': {'items_json':sha256_text(final_text),'stats_json':sha256_text(stats_text)},
}
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
if failures:
    raise SystemExit('VALIDATION FAILED')
