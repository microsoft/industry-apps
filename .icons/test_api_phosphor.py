import requests
import json

# Test Phosphor icon search
response = requests.post(
    'http://localhost:8000/api/icon-selector/icons/search',
    json={'query': 'airplane', 'sources': ['phosphor']}
)

results = response.json()
print(f"Phosphor 'airplane' search: Found {len(results)} icons")
for icon in results[:5]:
    print(f"  - {icon['name']} ({icon['source']})")

# Test user search
response = requests.post(
    'http://localhost:8000/api/icon-selector/icons/search',
    json={'query': 'user', 'sources': ['phosphor']}
)

results = response.json()
print(f"\nPhosphor 'user' search: Found {len(results)} icons")
for icon in results[:5]:
    print(f"  - {icon['name']} ({icon['source']})")

# Test all sources
response = requests.post(
    'http://localhost:8000/api/icon-selector/icons/search',
    json={'query': 'airplane', 'sources': ['tabler', 'material-design', 'lucide', 'phosphor']}
)

results = response.json()
phosphor_count = sum(1 for i in results if i['source'] == 'phosphor')
print(f"\nAll sources 'airplane' search: {len(results)} total, {phosphor_count} from Phosphor")
