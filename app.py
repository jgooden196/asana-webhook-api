from flask import Flask, request, jsonify, Response
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Asana API Setup
ASANA_TOKEN = os.getenv("2/1204220771478700/1209548487495577:be3f4f050183a87e91bf18de543df9c5")  # Ensure you have set this in Railway environment variables
PROJECT_ID = "1209353707682767"  # Replace with your actual Asana project ID
SECTION_ID = "1209544289104123"  # Replace with your actual Asana section ID
BUDGET_FIELD_ID = "1209353707682778"  # Replace with your actual budget field ID
TRB_TASK_NAME = "TRB - Placeholder"  # This is the placeholder task name

HEADERS = {
    "Authorization": f"Bearer {ASANA_TOKEN}",
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

        if "events" in data:
            for event in data["events"]:
                if event["resource"]["resource_type"] == "task" and event["action"] == "changed":
                    task_id = event["resource"]["gid"]
                    print(f"🔹 Task Change Event - Processing Task ID: {task_id}")
                    handle_task_update(task_id)

        return jsonify({"status": "processed"}), 200

def handle_task_update(task_id):
    """Handles task updates to calculate remaining budget and update TRB task."""
    tasks = fetch_project_tasks()
    remaining_budget = calculate_remaining_budget(tasks)

    print(f"✅ Total Remaining Budget Calculated: ${remaining_budget:,}")

    update_trb_task(remaining_budget)

def fetch_project_tasks():
    """Fetches all tasks in the project."""
    url = f"https://app.asana.com/api/1.0/projects/{PROJECT_ID}/tasks?opt_fields=gid,name,completed,custom_fields"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        tasks = response.json().get("data", [])
        print(f"✅ Successfully fetched project tasks ({len(tasks)} tasks)")
        return tasks
    else:
        print(f"❌ Error fetching project tasks: {response.json()}")
        return []

def calculate_remaining_budget(tasks):
    """Calculates the remaining budget from incomplete tasks."""
    total_remaining_budget = 0

    for task in tasks:
        if task["completed"]:
            continue

        budget_value = None
        for field in task.get("custom_fields", []):
            if field["gid"] == BUDGET_FIELD_ID:
                budget_value = field.get("number_value")
                break

        if budget_value is None:
            print(f"⚠️ Warning: Task '{task['name']}' has no budget value. Skipping.")
            continue

        total_remaining_budget += budget_value

    return int(total_remaining_budget)

def update_trb_task(remaining_budget):
    """Finds and updates the TRB task with the latest total remaining budget."""
    tasks = fetch_project_tasks()
    trb_task = None

    for task in tasks:
        if TRB_TASK_NAME in task["name"]:
            trb_task = task
            break

    formatted_budget = f"{remaining_budget:,}"  # Format with commas
    new_trb_name = f"TRB - {datetime.now().strftime('%Y-%m-%d')} - ${formatted_budget}"

    if trb_task:
        trb_task_id = trb_task["gid"]
        print(f"🔄 Updating TRB task (ID: {trb_task_id}) to '{new_trb_name}'")

        response = requests.put(
            f"https://app.asana.com/api/1.0/tasks/{trb_task_id}",
            headers=HEADERS,
            json={
                "data": {
                    "name": new_trb_name
                }
            }
        )

        if response.status_code == 200:
            print(f"✅ TRB Task Updated: {new_trb_name}")
        else:
            print(f"❌ Error updating TRB task: {response.json()}")
    else:
        print(f"❌ No existing TRB task found. Please ensure a TRB placeholder exists.")

@app.route('/manual_trigger', methods=['POST'])
def manual_trigger():
    """Manually triggers the TRB calculation and update."""
    print("🚀 Manually Triggered TRB Calculation")

    tasks = fetch_project_tasks()
    remaining_budget = calculate_remaining_budget(tasks)

    print(f"✅ Total Remaining Budget Calculated: ${remaining_budget:,}")

    update_trb_task(remaining_budget)

    return jsonify({"message": "TRB update completed", "updated_budget": f"${remaining_budget:,}"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
