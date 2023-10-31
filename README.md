# Motion Task Creator

This is a simple python script designed to batch add tasks to my Motion list.

I created it with the help of Chat-GPT (GPT4 with Advanced Data Analysis) and a bit of brute force of my poor python habilities.

Feel free to use it and change as you need, this is probably never getting updated as it already fits everything I need.

## How it works

You have to generate an API key inside the settings page and add it to an .env file:

    API_KEY=YOUR-API-KEY

And add all your tasks to the tasks.csv file

    dueDate,duration,name,projectId,workspaceId,description,priority,labels

## Installation

I use Conda for package management, so you can just clone this repository and create a new env from ny enviroment.yml:

```bash
conda env create -f environment.yml
```

After filling everything, just run it from your terminal and wait a few seconds for it to run.

    python motion-task-creator.py

## Workarounds and limitations

### Motion limits API usage

Motion has a hard limit of 12 requests per minute, to avoid going over it, I'm lockign at 10 per minute, you shouldn't change it:

```python
RATE_LIMIT = 10  # requests per minute
DELAY = 60 / RATE_LIMIT  # delay in seconds between requests
```

### You have to manually find projectId and workspaceId

The projectId and workspaceId can both be queried from Motion's API documentation and test enviroment:

<https://docs.usemotion.com/docs/motion-rest-api/49d282a3fe58b-list-workspaces>

<https://docs.usemotion.com/docs/motion-rest-api/653816f032dd4-list-projects>

### Start date is manually set to -14 days

By default, the startdate of a task is -14 days from the delivery date. This fits my purpose, but you can change it to whatever fits yours

```python
# Calculate the startDate by subtracting 14 days from the dueDate
    due_date = parse(task_data["dueDate"])
    start_date = due_date - datetime.timedelta(days=14)
```

### Timezone set to GTM-3

Since I'm in Brazil, the ISO8601 time convertion sets it automatically to my timezone, you can change it to yours

```python
# Adjust to GMT -3 and format in ISO 8601 format
    tz = tzoffset(None, -3*3600)
    task_data["dueDate"] = due_date.astimezone(tz).isoformat()
```

### Auto Scheduling feature

The autoschedule is set to always put tasks as HARD deadlines and use the schedule "Task Hours", that's a schedule you can set in settings and I use it to keep a different Task and Meetings calendar avaiability. You can do the same os change it to the default "Meeting Hours"

```python
# Set autoScheduled fields
    task_data["autoScheduled"] = {
        "startDate": start_date.astimezone(tz).isoformat(),
        "deadlineType": "HARD",
        "schedule": "Task Hours"
    }
```

### It automatically creates a .log

To be able to debug and know if something is working or not, it automatically creates a \*.log file at every run with the current date+time as its name. You can delete it if you want.
