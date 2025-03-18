import json
import os
from datetime import datetime

def get_schedule_file_path(conversation_filename):
    """Derives the schedule file path from the conversation filename."""
    base_path, _ = os.path.splitext(conversation_filename)
    schedule_filename = f"{base_path}_schedule.json"
    return schedule_filename

def add_event(conversation_filename, event_name, event_date, event_time):
    """Adds an event to the user's schedule file."""
    schedule_file = get_schedule_file_path(conversation_filename)

    # Load existing events
    if os.path.exists(schedule_file):
        with open(schedule_file, "r") as file:
            events = json.load(file)
    else:
        events = []

    # Check for conflicts
    for event in events:
        if event["date"] == event_date and event["time"] == event_time:
            return f"An event is already scheduled on {event_date} at {event_time}. Please choose a different time."

    # Add new event
    new_event = {"name": event_name, "date": event_date, "time": event_time}
    events.append(new_event)

    # Save events
    with open(schedule_file, "w") as file:
        json.dump(events, file, indent=4)

    return f"Event '{event_name}' scheduled on {event_date} at {event_time}."

def get_schedule(conversation_filename):
    """Returns the user's scheduled events as a formatted string."""
    schedule_file = get_schedule_file_path(conversation_filename)

    if os.path.exists(schedule_file):
        with open(schedule_file, "r") as file:
            events = json.load(file)
            if events:
                return "\n".join(
                    f"{event['name']} on {event['date']} at {event['time']}" for event in events
                )
            else:
                return "No events scheduled."
    else:
        return "No events scheduled."

def remove_event(conversation_filename, event_name, event_date, event_time):
    """Removes an event from the user's schedule."""
    schedule_file = get_schedule_file_path(conversation_filename)

    if os.path.exists(schedule_file):
        with open(schedule_file, "r") as file:
            events = json.load(file)
    else:
        return "No events found to remove."

    # Filter events
    updated_events = []
    event_found = False
    for event in events:
        if event["name"] == event_name and event["date"] == event_date and event["time"] == event_time:
            event_found = True
        else:
            updated_events.append(event)

    if event_found:
        with open(schedule_file, "w") as file:
            json.dump(updated_events, file, indent=4)
        return f"Event '{event_name}' on {event_date} at {event_time} has been removed."
    else:
        return f"No event named '{event_name}' found on {event_date} at {event_time}."

def get_current_datetime():
    """Returns the current date and time."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")
