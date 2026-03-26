import requests                                       
      2 import json                                           
      3                                                             4 url = "http://127.0.0.1:8000/api/samachar/proce
        ss"                                                   
      5 data = {"text": "Breaking news: Tech stocks ral       
        ly as AI companies report strong earnings."}
      6
      7 resp = requests.post(url, json=data)
      8 print(resp.status_code)
      9 print(json.dumps(resp.json(), indent=2))