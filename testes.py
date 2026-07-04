import requests

headers = {"Authorization": "Bearer"}

requests.get("http://127.0.0.1:8000/auth/refresh", headers=headers)
