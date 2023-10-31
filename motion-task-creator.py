import csv
import time
import requests
import datetime
from dateutil.parser import parse
from dateutil.tz import tzoffset
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
# Constants
API_URL = "https://api.usemotion.com/v1/tasks"
RATE_LIMIT = 10  # requests per minute
DELAY = 60 / RATE_LIMIT  # delay in seconds between requests

def remove_bom_from_csv(csv_file):
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        content = file.read()
    with open(csv_file, 'w', encoding='utf-8') as file:
        file.write(content)

def validate_row(row):
    # Check if all the fields are non-empty.
    for field, value in row.items():
        if not value:
            return False, f"Field '{field}' is empty."
    # Check if the date format is correct.
    try:
        # Try parsing with the format 'MM/DD/YY' and fallback to default parsing
        due_date = datetime.datetime.strptime(row["dueDate"], '%m/%d/%y')
        row["dueDate"] = due_date.strftime('%Y-%m-%d')
    except ValueError:
        try:
            parse(row["dueDate"])
        except ValueError:
            return False, f"Invalid date format for 'dueDate' in row {row['name']}."
    return True, ""

def create_task(api_key, task_data):
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Convert 'labels' from comma-separated string to list of strings
    if "labels" in task_data and isinstance(task_data["labels"], str):
        task_data["labels"] = [label.strip() for label in task_data["labels"].split(',')]
    
    # Convert 'duration' to integer (assuming it's given in minutes in the CSV)
    if "duration" in task_data:
        task_data["duration"] = int(task_data["duration"])
    
    # Calculate the startDate by subtracting 14 days from the dueDate
    due_date = parse(task_data["dueDate"])
    start_date = due_date - datetime.timedelta(days=14)
    
    # Adjust to GMT -3 and format in ISO 8601 format
    tz = tzoffset(None, -3*3600)
    task_data["dueDate"] = due_date.astimezone(tz).isoformat()
    
    # Set autoScheduled fields
    task_data["autoScheduled"] = {
        "startDate": start_date.astimezone(tz).isoformat(),
        "deadlineType": "HARD",
        "schedule": "Task Hours"
    }
    
    response = requests.post(API_URL, headers=headers, json=task_data)
    return response.status_code, response.json()


def main(api_key, csv_file):
    # Remove BOM from the CSV file
    remove_bom_from_csv(csv_file)
    log_filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.log"
    with open(csv_file, 'r') as file, open(log_filename, 'w') as log:
        reader = csv.DictReader(file, delimiter=';', quotechar='"')
        for row in reader:
            valid, error = validate_row(row)
            if not valid:
                log.write(f"Error in row {reader.line_num}: {error}\n")
                continue
            
            status_code, response = create_task(api_key, row)
            if status_code == 201:  # HTTP 201 Created
                log.write(f"Task '{row['name']}' created successfully.\n")
            else:
                log.write(f"Error creating task '{row['name']}': {response}\n")
            
            time.sleep(DELAY)

if __name__ == "__main__":
    CSV_FILE_NAME = "tasks.csv"  # Assuming the CSV is named tasks.csv and is in the same folder
    main(API_KEY, CSV_FILE_NAME)
