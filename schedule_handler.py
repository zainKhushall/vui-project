from datetime import datetime
import json
import os

EVENTS_FILE = "events.json"

def add_event(event_name, event_date, event_time):
    # Load existing events if the file exists
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as file:
            events = json.load(file)
    else:
        events = []

    # Check if an event with the same date and time already exists
    for event in events:
        if event["date"] == event_date and event["time"] == event_time:
            return f"An event is already scheduled on {event_date} at {event_time}. Please choose a different time."

    # Add the new event if no conflicts found
    new_event = {"name": event_name, "date": event_date, "time": event_time}
    events.append(new_event)

    # Save updated events list to file
    with open(EVENTS_FILE, "w") as file:
        json.dump(events, file, indent=4)

    return f"Event '{event_name}' scheduled on {event_date} at {event_time}."

def get_schedule():
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as file:
            events = json.load(file)
            if events:
                return "\n".join(
                    f"{event['name']} on {event['date']} at {event['time']}" for event in events
                )
            else:
                return "No events scheduled."
    else:
        return "No events scheduled."

def remove_event(event_name, event_date, event_time):
    # Load existing events if the file exists
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as file:
            events = json.load(file)
    else:
        return "No events found to remove."

    # Check if the event exists
    event_found = False
    updated_events = []
    for event in events:
        if event["name"] == event_name and event["date"] == event_date and event["time"] == event_time:
            event_found = True  # Mark that the event was found
        else:
            updated_events.append(event)  # Keep other events

    if event_found:
        # Save updated events list to file after removal
        with open(EVENTS_FILE, "w") as file:
            json.dump(updated_events, file, indent=4)
        return f"Event '{event_name}' on {event_date} at {event_time} has been removed."
    else:
        return f"No event named '{event_name}' found on {event_date} at {event_time}."


def get_current_datetime():
    """Returns the current date and time as a formatted string."""
    now = datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")  # Format as YYYY-MM-DD HH:MM:SS
    return formatted_datetime