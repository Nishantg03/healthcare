import requests, json

r = requests.post('http://localhost:8000/api/analyze', json={'case_id': 'PA-001'})
try:
    d = r.json()
except Exception:
    print('Error parsing response:', r.text)
    raise

cr = d.get('criteria_results', [])
met = sum(1 for c in cr if c.get('status') == 'MET')
partial = sum(1 for c in cr if c.get('status') == 'PARTIAL')
notmet = sum(1 for c in cr if c.get('status') == 'NOT_MET')
gaps = [c.get('gap') for c in cr if c.get('gap')]

print(f"MET: {met}  PARTIAL: {partial}  NOT_MET: {notmet}  Gaps count: {len(gaps)}\n")
for i, c in enumerate(cr, 1):
    print(f"{i}. {c.get('criterion')}: {c.get('status')}; gap={c.get('gap')}")

print('\nMissing information list:')
for g in d.get('missing_information', []):
    print('-', g)
