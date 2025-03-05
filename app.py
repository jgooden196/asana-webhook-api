from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Load Asana API token and workspace ID from environment variables
ASANA_TOKEN = os.getenv("2/1204220771478700/1209557208654124:14e1caffe986d2899907f8fabb501f14")
HEADERS = {
    "Authorization": f"Bearer {ASANA_TOKEN}",
    "Content-Type": "application/json"
}

@app.route("/")
def home():
    return "Webhook is running."

@app.route("/webhook", methods=["POST", "GET"])
def asana_webhook():
    if request.method == "GET":
        challenge = request.args.get("challenge")
        if challenge:
            return jsonify({"challenge": challenge})

    if request.method == "POST":
        data = request.json
        print("🔹 Webhook Event Received:", data)

        for event in data.get("events", []):
            if event["resource_type"] == "task":
                task_id = event["resource"]["gid"]
                action = event["action"]
                change_field = event.get("change", {}).get("field")

                if change_field == "tags":
                    update_task_description(task_id, action)

        return jsonify({"message": "Processed"}), 200

def update_task_description(task_id, action):
    """Append timestamp to task description based on tag add/remove action."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    note = f"\n- Tag {action} at {timestamp}"

    # Fetch current task details
    response = requests.get(f"https://app.asana.com/api/1.0/tasks/{task_id}", headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Error fetching task {task_id}: {response.json()}")
        return

    task_data = response.json().get("data", {})
    current_description = task_data.get("notes", "")

    # Append new note
    updated_description = current_description + note
    update_payload = {"data": {"notes": updated_description}}

    # Send update request
    response = requests.put(f"https://app.asana.com/api/1.0/tasks/{task_id}", json=update_payload, headers=HEADERS)
    if response.status_code == 200:
        print(f"✅ Updated task {task_id} description with: {note}")
    else:
        print(f"❌ Error updating task {task_id}: {response.json()}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
