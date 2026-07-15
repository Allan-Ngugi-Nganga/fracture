"""Create fracture repo on GitHub."""
import json, urllib.request, os

TOKEN = "ghp_rr…Bze"
url = "https://api.github.com/user/repos"
payload = json.dumps({
    "name": "fracture",
    "description": "Measure your brain's fragmentation tax — context switch tracking for knowledge workers",
    "private": False,
}).encode()

req = urllib.request.Request(url, data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    })
try:
    resp = urllib.request.urlopen(req)
    data = json.load(resp)
    print(f"Created: {data['html_url']}")
except urllib.error.HTTPError as e:
    print(f"Error: {e.code} {e.read().decode()}")
