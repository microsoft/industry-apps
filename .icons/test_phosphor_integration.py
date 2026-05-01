import json

# Test Phosphor integration
with open('.icons/merged_icons_cache_clean.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

total = len(data['icons'])
phosphor = [i for i in data['icons'] if i['source'] == 'phosphor']

print(f"Total icons: {total}")
print(f"Phosphor icons: {len(phosphor)}")
print(f"\nSample Phosphor icons:")
for icon in phosphor[:5]:
    print(f"  - {icon['name']} (category: {icon['category']}, tags: {len(icon['tags'])})")

# Check source distribution
from collections import Counter
sources = Counter(i['source'] for i in data['icons'])
print(f"\nIcon sources:")
for source, count in sources.most_common():
    print(f"  {source}: {count}")
