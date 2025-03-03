from flask import Flask, request, jsonify, Response
import requests
import datetime
import os

app = Flask(__name__)

# Set your Asana PAT and workspace details
ASANA_PAT = "2/1204220771478700/1209548487495577:be3f4f050183a87e91bf18de543df9c5"
HEADERS = {
    "Authorization": f"Bearer {ASANA_PAT}",
    "Content-Type": "application/json"
}

# Project and section details
PROJECT_ID = "1209353707682767"
SECTION_ID = "1209544289104123"
TRB_TASK_NAME_PREFIX = "TRB -"

@app.route('/')
def home():
    return "Hello, Railway! JP Asana Webhook API is running."

@app.route('/webhook', methods=['POST', 'GET'])
def asana_webhook():
    if request.method == 'GET':
        # Asana webhook validation request
        challenge = request.args.get('challenge')
        if challenge:
            return jsonify({'challenge': challenge})

    if request.method == 'POST':
        # Log the webhook event data
        data = request.json
        print("Webhook Event Received:", data)

        for event in data.get("events", []):
            if event.get("resource", {}).get("resource_type") == "task" and event.get("action") == "changed":
                task_id = event["resource"]["gid"]
                handle_task_update(task_id)

        return jsonify({"status": "processed"}), 200

def handle_task_update(task_id):
    """ Process the task update event to update the TRB task """
    print(f"\n✅ Task Change Event - Processing Task ID: {task_id}")

    # Fetch all tasks in the project
    tasks = get_project_tasks()
    
    if not tasks:
        print("❌ No tasks found in the project.")
        return

    # Calculate remaining budget
    total_remaining_budget = calculate_remaining_budget(tasks)
    formatted_budget = f"${total_remaining_budget:,.0f}"  # Add commas, remove decimals

    print(f"✅ Total Remaining Budget Calculated: {formatted_budget}")

    # Find the TRB task
    trb_task = find_trb_task(tasks)
    
    # Update or create the TRB task
    update_trb_task(trb_task, formatted_budget)

def get_project_tasks():
    """ Retrieve all tasks from the project """
    url = f"https://app.asana.com/api/1.0/projects/{PROJECT_ID}/tasks?opt_fields=name,completed,custom_fields"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"❌ Error fetching tasks: {response.json()}")
        return []

def calculate_remaining_budget(tasks):
    """ Calculate total remaining budget from incomplete tasks """
    total_remaining_budget = 0

    for task in tasks:
        # Find the budget field in custom fields
        budget_value = None
        for field in task.get("custom_fields", []):
            if field.get("gid") == "YOUR_BUDGET_FIELD_ID":
                budget_value = field.get("number_value")

        if budget_value is None:
            print(f"⚠️ Warning: Task '{task['name']}' has no budget value. Skipping.")
            continue

        if not task["completed"]:
            total_remaining_budget += budget_value

    return total_remaining_budget

def find_trb_task(tasks):
    """ Find the TRB task in the section """
    for task in tasks:
        if task["name"].startswith(TRB_TASK_NAME_PREFIX):
            return task  # Return the existing TRB task
    return None

def update_trb_task(trb_task, formatted_budget):
    """ Update the existing TRB task with the latest budget and timestamp """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    task_name = f"TRB - {timestamp} - {formatted_budget}"

    if trb_task:
        # Update existing TRB task
        url = f"https://app.asana.com/api/1.0/tasks/{trb_task['gid']}"
        response = requests.put(url, headers=HEADERS, json={"name": task_name})

        if response.status_code == 200:
            print(f"✅ TRB Task Updated: {task_name}")
        else:
            print(f"❌ Error updating TRB task: {response.json()}")
    else:
        # Create new TRB task if not found
        create_trb_task(task_name)

def create_trb_task(task_name):
    """ Create a new TRB task in the designated section """
    url = "https://app.asana.com/api/1.0/tasks"
    payload = {
        "name": task_name,
        "projects": [PROJECT_ID],
        "section": SECTION_ID
    }
    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 201:
        print(f"✅ TRB Task Created: {task_name}")
    else:
        print(f"❌ Error creating TRB task: {response.json()}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
