import json
import time
import os
from urllib.parse import urljoin
import requests

# Configure
BASE_URL = os.getenv('FASTAPI_BASE_URL', 'http://localhost:8000')

def post_item(item):
    url = urljoin(BASE_URL, '/api/news')
    resp = requests.post(url, json=item, timeout=30)
    resp.raise_for_status()
    return resp.json()

def get_item(news_id):
    url = urljoin(BASE_URL, f'/api/news/{news_id}')
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def main():
    with open('sample_data.json', 'r', encoding='utf-8') as f:
        samples = json.load(f)

    created = []
    for s in samples:
        print('Posting:', s['title'])
        r = post_item(s)
        print('  ->', r)
        created.append(r['newsId'])

    print('\nWaiting 5 seconds for background processing...')
    time.sleep(5)

    for nid in created:
        try:
            res = get_item(nid)
            print('\nResult for', nid)
            print(json.dumps(res, indent=2, ensure_ascii=False))
        except Exception as e:
            print('Error fetching', nid, e)

if __name__ == '__main__':
    main()
