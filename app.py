from flask import Flask, request, jsonify, Response
import requests
import datetime

app = Flask(__name__)

# Asana API Token (Replace with your actual token)
ASANA_ACCESS_TOKEN = "2/1204220771478700/1209548487495577:be3f4f050183a87e91bf18de543df9c5"
PROJECT_ID = "1209353707682767"
CALCULATED_TOTAL_SECTION_ID = "1209544289104123"  # Section where TRB tasks will be added

# Headers for Asana API requests
HEADERS = {
    "Authorization": f"Bearer {ASANA_ACCESS_TOKEN}",
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
        print("Webhook Event Received:", data)

        x_hook_secret = request.headers.get('X-Hook-Secret')
        if x_hook_secret:
            response = Response("Webhook received")
            response.headers["X-Hook-Secret"] = x_hook_secret
            return response

        # Process Task Updates
        if "events" in data:
            for event in data["events"]:
                if event["resource"]["resource_type"] == "task":
                    handle_task_update(event)

        return jsonify({"status": "received"}), 200

def handle_task_update(event):
    """Processes an Asana task update event."""
    if event["action"] == "changed":
        print("Task Updated:", event)

        # Get all tasks in the project
        tasks = get_project_tasks(PROJECT_ID)

        # Calculate total remaining budget
        remaining_budget = calculate_remaining_budget(tasks)

        # Create the TRB task
        create_trb_task(remaining_budget)

def get_project_tasks(project_id):
    """Fetch all tasks in the project."""
    url = f"https://app.asana.com/api/1.0/projects/{project_id}/tasks?opt_fields=name,completed,custom_fields"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print("Error fetching tasks:", response.json())
        return []

def calculate_remaining_budget(tasks):
    """Calculates the total remaining budget from uncompleted tasks."""
    remaining_budget = 0
    for task in tasks:
        if not task.get("completed"):  # Check if task is NOT completed
            custom_fields = task.get("custom_fields", [])
            for field in custom_fields:
                if field.get("name") == "Budget Amount":
                    remaining_budget += float(field.get("number_value", 0))

    print("Total Remaining Budget:", remaining_budget)
    return remaining_budget

def create_trb_task(remaining_budget):
    """Creates a TRB task in the project under the 'Calculated Total Updates' section."""
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    task_name = f"TRB - {today} - ${remaining_budget:.2f}"

    task_data = {
        "name": task_name,
        "projects": [PROJECT_ID],
        "parent": None,  # Ensure it's a standalone task
        "memberships": [{"project": PROJECT_ID, "section": CALCULATED_TOTAL_SECTION_ID}]
    }

    url = "https://app.asana.com/api/1.0/tasks"
    response = requests.post(url, json={"data": task_data}, headers=HEADERS)

    if response.status_code == 201:
        print("TRB Task Created Successfully:", response.json())
    else:
        print("Error Creating TRB Task:", response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
