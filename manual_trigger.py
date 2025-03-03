import requests
import datetime

# Set your Asana API details
ASANA_PAT = "YOUR_ASANA_PAT"
PROJECT_ID = "YOUR_PROJECT_ID"
SECTION_ID = "YOUR_SECTION_ID"
TRB_TASK_NAME_PREFIX = "TRB -"

HEADERS = {
    "Authorization": f"Bearer {ASANA_PAT}",
    "Content-Type": "application/json"
}

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
            if field.get("gid") == "YOUR_BUDGET_FIELD_ID":
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

if __name__ == "__main__":
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
