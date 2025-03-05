import requests
import os

# Replace with your Asana access token
ASANA_ACCESS_TOKEN = "2/1204220771478700/1209557208654124:14e1caffe986d2899907f8fabb501f14"

# Replace with your Asana resource ID (Task, Project, or Workspace ID)
RESOURCE_ID = "1209353707682767"

# Your deployed webhook URL on Railway
WEBHOOK_URL = "asana-webhook-api-production.up.railway.app"

headers = {
    "Authorization": f"Bearer {ASANA_ACCESS_TOKEN}",
    "Content-Type": "application/x-www-form-urlencoded"
}

data = {
    "resource": RESOURCE_ID,
    "target": WEBHOOK_URL
}

response = requests.post("https://app.asana.com/api/1.0/webhooks", headers=headers, data=data)

print("Response Status Code:", response.status_code)
print("Response JSON:", response.json())
