import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
const root=process.cwd();
const raw=JSON.parse(readFileSync(path.join(root,'items.json'),'utf8'));const items=Array.isArray(raw)?raw:raw.items;
const linkFields=['link_telegram','link_drive','link_direct'];
const telegramUrl=/^(?:https?:\/\/)?(?:t\.me|telegram\.me)\/([^?#/]+)(?:\/([^?#]+))?/i;
const normalize=(value)=>String(value??'').trim().toLowerCase();
function getTelegramLinks(item){return linkFields.flatMap(field=>String(item[field]??'').split(/[\s,]+/).filter(value=>/(?:t\.me|telegram\.me)\//i.test(value)).map(value=>({field,url:value})));}
function channelFrom(url){const match=url.match(telegramUrl);if(!match)return 'غير قابل للاستخراج';return normalize(match[1])==='c'&&match[2]?`c/${match[2].split('/')[0]}`:match[1];}
function statusFor(source,channels){const s=normalize(source),c=channels.map(normalize);const one=(terms)=>terms.some(term=>s.includes(term)||c.some(channel=>channel.includes(term)));
 if(one(['bahith_pdf','bahith_word','arsail2020','waqfeya_pdf','shamela_epub','ilmiya_pdf']))return 'موثوق ومعتمد — مستثنى';
 if(one(['arabialawer','great_law','iirmll','ibrazx40','مكتبة الاسكندرية','المكتبة القانونية الكبرى','قناة الرسائل العلمية الخاصة','c/1453973283','قناة المجلات والصحف القانونية']))return 'مفحوص ومنتهٍ — مستثنى';
 return 'غير محسوم — ضمن الفحص النهائي';}
const sourceMap=new Map();let telegramItemCount=0;
for(const item of items){const links=getTelegramLinks(item);if(!links.length)continue;telegramItemCount++;const source=String(item.source??'غير محدد').trim()||'غير محدد';const channels=[...new Set(links.map(link=>channelFrom(link.url)))].sort();const key=source;const entry=sourceMap.get(key)??{source,channels:new Map(),items:[]};entry.items.push({id:item.id,title:item.title,author:item.author,category:item.category,source,links,channels});for(const channel of channels)entry.channels.set(channel,(entry.channels.get(channel)??0)+1);sourceMap.set(key,entry);}
const groups=[...sourceMap.values()].map(entry=>{const channels=[...entry.channels.entries()].map(([channel,count])=>({channel,count}));const status=statusFor(entry.source,channels.map(row=>row.channel));return {source:entry.source,channels,item_count:entry.items.length,status,items:entry.items};}).sort((a,b)=>a.source.localeCompare(b.source,'ar'));
const remaining=groups.filter(group=>group.status.startsWith('غير محسوم'));
const out={generated_at:new Date().toISOString(),total_items:items.length,telegram_item_count:telegramItemCount,total_source_groups:groups.length,source_groups:groups,remaining_source_groups:remaining.map(group=>({source:group.source,channels:group.channels,item_count:group.item_count,status:group.status,items:group.items})),closed_or_trusted_groups:groups.filter(group=>!group.status.startsWith('غير محسوم')).map(group=>({source:group.source,channels:group.channels,item_count:group.item_count,status:group.status}))};
writeFileSync(path.join(root,'telegram_sources_full_inventory.json'),`${JSON.stringify(out,null,2)}\n`);console.log(JSON.stringify({telegram_item_count:telegramItemCount,total_source_groups:groups.length,remaining_source_groups:remaining.map(group=>({source:group.source,item_count:group.item_count,channels:group.channels}))},null,2));
