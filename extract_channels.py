#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
استخراج أسماء القنوات والمصادر من ملف تصدير تيليجرام
"""

import json
import re
from collections import Counter, defaultdict

with open("/home/ubuntu/upload/result.json", encoding="utf-8") as f:
    data = json.load(f)

print(f"اسم القناة الرئيسية: {data.get('name', '')}")
print(f"النوع: {data.get('type', '')}")
print(f"عدد الرسائل: {len(data.get('messages', []))}")
print("="*60)

messages = data.get("messages", [])

# استخراج جميع المُعاد توجيههم (forwarded_from)
forwarded_sources = Counter()
channel_links = defaultdict(list)
all_links = []
file_names = []
text_samples = []

for msg in messages:
    if msg.get("type") != "message":
        continue
    
    # المصادر المُعاد توجيهها
    fwd = msg.get("forwarded_from", "")
    if fwd:
        forwarded_sources[fwd] += 1
    
    # استخراج الروابط
    text = msg.get("text", "")
    if isinstance(text, list):
        for part in text:
            if isinstance(part, dict) and part.get("type") == "link":
                link = part.get("text", "")
                all_links.append(link)
                if fwd:
                    channel_links[fwd].append(link)
    elif isinstance(text, str):
        links = re.findall(r'https?://\S+', text)
        all_links.extend(links)
    
    # أسماء الملفات
    fname = msg.get("file_name", "")
    if fname:
        file_names.append(fname)
    
    # عينات من النصوص
    if isinstance(text, str) and len(text) > 20:
        text_samples.append(text[:200])
    elif isinstance(text, list):
        full_text = " ".join([p if isinstance(p, str) else p.get("text", "") for p in text])
        if len(full_text) > 20:
            text_samples.append(full_text[:200])

print(f"\n📡 المصادر المُعاد توجيهها (أسماء القنوات):")
for src, count in forwarded_sources.most_common():
    print(f"  [{count}] {src}")

print(f"\n📎 عدد الروابط الكلي: {len(all_links)}")
print(f"📄 عدد الملفات: {len(file_names)}")

print(f"\n📄 أسماء الملفات (أول 50):")
for fn in file_names[:50]:
    print(f"  - {fn}")

print(f"\n🔗 عينة من الروابط:")
for link in all_links[:20]:
    print(f"  {link}")

# استخراج أسماء القنوات من الروابط
tg_channels = set()
for link in all_links:
    m = re.match(r'https://t\.me/([^/\s]+)', link)
    if m:
        ch = m.group(1)
        if not ch.isdigit() and len(ch) > 2:
            tg_channels.add(ch)

print(f"\n📡 قنوات تيليجرام المذكورة في الروابط:")
for ch in sorted(tg_channels):
    print(f"  https://t.me/{ch}")

# حفظ النتائج
results = {
    "channel_name": data.get("name", ""),
    "forwarded_sources": dict(forwarded_sources.most_common()),
    "telegram_channels": sorted(list(tg_channels)),
    "total_files": len(file_names),
    "file_names": file_names,
    "total_links": len(all_links),
    "sample_links": all_links[:50],
}

with open("/home/ubuntu/makanez-qadaa/data/telegram_channels.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n✅ تم حفظ النتائج في telegram_channels.json")
