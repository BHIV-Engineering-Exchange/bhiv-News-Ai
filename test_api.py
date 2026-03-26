import requests
import json

url = "http://127.0.0.1:8000/api/samachar/process"
data = {"text": "Breaking news: Tech stocks rally as AI companies report strong earnings."}

resp = requests.post(url, json=data)
print(resp.status_code)
print(json.dumps(resp.json(), indent=2))
