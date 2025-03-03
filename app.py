from flask import Flask, request, jsonify, Response
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Load Asana API Token and Resource IDs
ASANA_API_TOKEN = os.getenv("ASANA_API_TOKEN")
ASANA_PROJECT_ID = os.getenv("ASANA_PROJECT_ID")
ASANA_SECTION_ID = os.getenv("ASANA_SECTION_ID")
ASANA_BUDGET_FIELD_ID = os.getenv("ASANA_BUDGET_FIELD_ID")

# Debugging: Print API token to logs (do not use in production)
print(f"DEBUG: Loaded Asana API Token: {ASANA_API_TOKEN}")

# Headers for Asana API requests
HEADERS = {
    "Authorization": f"Bearer {ASANA_API_TOKEN}",
    "Content-Type": "application/json"
}

@app.route('/')
def home():
    return "Hello, Railway! JP Asana Webhook API is running."

@app.route('/webhook', methods=['POST', 'GET'])
def asana_webhook():
    if request.method == 'GET':
        challenge = request.args.get('challenge')
        if challenge:
            return jsonify({'challenge': challenge})

    if request.method == 'POST':
        data = request.json
        print("🔹 Webhook Event Received:", data)

        for event in data.get("events", []):
            if event.get("resource", {}).get("resource_type") == "task" and event.get("action") in ["changed", "added"]:
                task_id = event["resource"]["gid"]
                print(f"🔹 Task Change Event - Processing Task ID: {task_id}")
                handle_task_update(task_id)

    return jsonify({"message": "Webhook received"}), 200

@app.route('/manual_trigger', methods=['POST'])
def manual_trigger():
    print("🚀 Manually Triggered TRB Calculation")
    calculate_and_update_trb()
    return jsonify({"message": "TRB update completed"})

def handle_task_update(task_id):
    try:
        print(f"Processing task update for Task ID: {task_id}")
        tasks = fetch_project_tasks()
        if tasks is None:
            print("❌ Failed to fetch project tasks")
            return

        remaining_budget = calculate_remaining_budget(tasks)
        print(f"✅ Total Remaining Budget Calculated: ${remaining_budget:,}")

        update_trb_task(remaining_budget)

    except Exception as e:
        print(f"❌ Error processing task update: {str(e)}")

def fetch_project_tasks():
    url = f"https://app.asana.com/api/1.0/projects/{ASANA_PROJECT_ID}/tasks?opt_fields=gid,name,completed,custom_fields"
    
    # Debugging: Print Headers Before Request
    print("🔹 Fetching project tasks with headers:", HEADERS)

    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Error fetching project tasks: {response.json()}")
        return None

    tasks = response.json().get("data", [])
    print(f"✅ Successfully fetched {len(tasks)} project tasks.")
    return tasks

def calculate_remaining_budget(tasks):
    total_remaining_budget = 0

    for task in tasks:
        if task.get("completed"):
            continue  # Skip completed tasks
        
        budget_value = None
        for field in task.get("custom_fields", []):
            if field["gid"] == ASANA_BUDGET_FIELD_ID:
                budget_value = field.get("number_value")

        if budget_value is not None:
            total_remaining_budget += budget_value
        else:
            print(f"⚠️ Warning: Task '{task.get('name')}' has no budget value. Skipping.")

    return total_remaining_budget

def update_trb_task(remaining_budget):
    url = f"https://app.asana.com/api/1.0/tasks"
    headers = HEADERS

    # Debugging: Print Headers Before Request
    print("🔹 Updating TRB Task with headers:", headers)

    # Fetch existing TRB task
    tasks = fetch_project_tasks()
    trb_task = None
    for task in tasks:
        if task["name"].startswith("TRB"):
            trb_task = task
            break

    trb_name = f"TRB - {datetime.now().strftime('%Y-%m-%d')} - ${remaining_budget:,}"

    if trb_task:
        trb_task_id = trb_task["gid"]
        update_url = f"https://app.asana.com/api/1.0/tasks/{trb_task_id}"
        payload = {
            "data": {
                "name": trb_name
            }
        }
        response = requests.put(update_url, headers=headers, json=payload)

        if response.status_code == 200:
            print(f"✅ TRB Task Updated: {trb_name}")
        else:
            print(f"❌ Error updating TRB task: {response.json()}")

    else:
        # Create new TRB task if no existing task is found
        create_url = f"https://app.asana.com/api/1.0/tasks"
        payload = {
            "data": {
                "name": trb_name,
                "projects": [ASANA_PROJECT_ID],
                "memberships": [{"section": ASANA_SECTION_ID}]
            }
        }
        response = requests.post(create_url, headers=headers, json=payload)

        if response.status_code == 201:
            print(f"✅ New TRB Task Created: {trb_name}")
        else:
            print(f"❌ Error creating TRB task: {response.json()}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
