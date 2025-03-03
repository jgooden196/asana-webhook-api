from flask import Flask, request, jsonify, Response
import requests
import datetime

app = Flask(__name__)

# Asana API Configuration
ASANA_PAT = "2/1204220771478700/1209548487495577:be3f4f050183a87e91bf18de543df9c5"
PROJECT_ID = "1209353707682767"
SECTION_ID = "1209544289104123"
BUDGET_FIELD_ID = "1209353707682778"
TRB_TASK_NAME_PREFIX = "TRB -"

HEADERS = {
    "Authorization": f"Bearer {ASANA_PAT}",
    "Content-Type": "application/json"
}

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
        data = request.json
        print("Webhook Event Received:", data)

        x_hook_secret = request.headers.get('X-Hook-Secret')
        response = Response("Webhook event processed.")
        response.headers["X-Hook-Secret"] = x_hook_secret

        # Extract task ID if available
        for event in data.get("events", []):
            if event["resource"]["resource_type"] == "task":
                task_id = event["resource"]["gid"]
                print(f"🔹 Task Change Event - Processing Task ID: {task_id}")
                handle_task_update(task_id)

        return response

def handle_task_update(task_id):
    """ Trigger the TRB calculation when a relevant task is updated. """
    print(f"Processing task update for Task ID: {task_id}")

    # Get all tasks
    tasks = get_project_tasks()
    
    # Calculate remaining budget
    total_remaining_budget = calculate_remaining_budget(tasks)
    formatted_budget = f"${total_remaining_budget:,.0f}"  # Format with commas, no decimals

    print(f"✅ Total Remaining Budget Calculated: {formatted_budget}")

    # Find TRB task
    trb_task = find_trb_task(tasks)

    # Update TRB task
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
        budget_value = None
        for field in task.get("custom_fields", []):
            if field.get("gid") == BUDGET_FIELD_ID:
                budget_value = field.get("number_value")

        if budget_value is None:
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
        print("❌ No TRB task found. Check Asana for existing TRB task.")

@app.route('/manual_trigger', methods=['POST'])
def manual_trigger():
    """ Manually triggers the TRB calculation """
    print("\n🚀 Manually Triggered TRB Calculation")
    
    # Get all tasks
    tasks = get_project_tasks()
    
    # Calculate remaining budget
    total_remaining_budget = calculate_remaining_budget(tasks)
    formatted_budget = f"${total_remaining_budget:,.0f}"  # Add commas, remove decimals

    print(f"✅ Total Remaining Budget Calculated: {formatted_budget}")

    # Find TRB task
    trb_task = find_trb_task(tasks)

    # Update TRB task
    update_trb_task(trb_task, formatted_budget)

    return jsonify({"message": "TRB update completed", "updated_budget": formatted_budget}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
