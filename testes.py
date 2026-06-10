import requests

headers = {
    'Authorization':'Bearer'
}

requests.get('http://http://127.0.0.1:8000/auth/refrash', headres=headers)