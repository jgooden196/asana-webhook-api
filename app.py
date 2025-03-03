from flask import Flask, request, jsonify, Response
import requests
import datetime

app = Flask(__name__)

# ✅ Asana API Credentials
ASANA_ACCESS_TOKEN = "2/1204220771478700/1209548487495577:be3f4f050183a87e91bf18de543df9c5"
PROJECT_ID = "1209353707682767"
CALCULATED_TOTAL_SECTION_ID = "1209544289104123"
BUDGET_CUSTOM_FIELD_ID = "1209353707682778"

# ✅ Headers for Asana API requests
HEADERS = {
    "Authorization": f"Bearer {ASANA_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

@app.route('/')
def home():
    return "Hello, Railway! JP Asana Webhook API is running."

@app.route('/webhook', methods=['POST', 'GET'])
def asana_webhook():
    """Handles Asana webhook validation and task updates."""
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

        # ✅ Process Task Updates
        if "events" in data:
            for event in data["events"]:
                if event["resource"]["resource_type"] == "task" and event["action"] == "changed":
                    handle_task_update(event["resource"]["gid"])

        return jsonify({"status": "received"}), 200

def handle_task_update(task_id):
    """Processes an Asana task update event and recalculates the TRB."""
    print(f"Processing task update for Task ID: {task_id}")

    # ✅ Get all tasks in the project
    tasks = get_project_tasks(PROJECT_ID)

    if not tasks:
        print("❌ No tasks found. Skipping TRB calculation.")
        return

    # ✅ Calculate the total remaining budget
    remaining_budget = calculate_remaining_budget(tasks)

    # ✅ Create or update the TRB task
    create_trb_task(remaining_budget)

def get_project_tasks(project_id):
    """Fetches all tasks in the project."""
    url = f"https://app.asana.com/api/1.0/projects/{project_id}/tasks?opt_fields=gid,name,completed,custom_fields"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"❌ Error fetching tasks: {response.status_code}", response.json())
        return []

def calculate_remaining_budget(tasks):
    """Calculates the total remaining budget for incomplete tasks."""
    total_remaining_budget = 0

    for task in tasks:
        if not task.get("completed"):  # ✅ Ignore completed tasks
            custom_fields = task.get("custom_fields", [])
            for field in custom_fields:
                if field.get("gid") == BUDGET_CUSTOM_FIELD_ID:  # ✅ Match correct custom field
                    value = field.get("number_value", 0)
                    total_remaining_budget += float(value)
    
    print(f"✅ Total Remaining Budget: ${total_remaining_budget:.2f}")
    return total_remaining_budget

def create_trb_task(remaining_budget):
    """Creates a new TRB task in the 'Calculated Total Updates' section."""
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    task_name = f"TRB - {today} - ${remaining_budget:.2f}"

    task_data = {
        "name": task_name,
        "projects": [PROJECT_ID],
        "memberships": [{"project": PROJECT_ID, "section": CALCULATED_TOTAL_SECTION_ID}]
    }

    url = "https://app.asana.com/api/1.0/tasks"
    response = requests.post(url, json={"data": task_data}, headers=HEADERS)

    if response.status_code == 201:
        print(f"✅ TRB Task Created: {task_name}")
    else:
        print(f"❌ Error Creating TRB Task: {response.status_code}", response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
