from models.route_model import Route
from datetime import time
import json

def parse_start_location(google_response):
    start_location = google_response["routes"][0]["legs"][0]["start_address"]
    return start_location

def parse_end_location(google_response):
    end_location = google_response["routes"][0]["legs"][0]["end_address"]
    return end_location

def parse_waypoints(google_response):
    """Creates a waypoint string that can be directly placed into a URI for Google Maps"""

    # Appends the starting point to the waypoint string
    waypoints = str(len(google_response["routes"][0]["legs"][0]["steps"])) + "via:"
    waypoints += str(google_response["routes"][0]["legs"][0]["start_location"]["lat"])[:10]
    waypoints += "%2C"
    waypoints += str(google_response["routes"][0]["legs"][0]["start_location"]["lng"])[:10]
    waypoints += "%7C"

    # Google can only accept 23 lat/lng waypoints, beyond start/end locations
    # If more than 23 intermediate waypoints in the user's route, we need to
    # trim the waypoints that have the shortest distance (theoretically, the least routing impact)
    # This list will end up the [distance][value] of the 23 longest steps
    # All other distances will be discarded
    distances_qualifying_for_waypoints_list = []
    for leg in google_response["routes"][0]["legs"]:
        for step in leg["steps"]:
            distances_qualifying_for_waypoints_list.append(step["distance"]["value"])

    distances_qualifying_for_waypoints_list.sort(reverse=True)
    distances_qualifying_for_waypoints_list = distances_qualifying_for_waypoints_list[:23]

    # Use the list of qualifying distances in a loop to append
    # Qualifying step's lat/lng's to the waypoints string
    i = 0
    for leg in google_response["routes"][0]["legs"]:
        for step in leg["steps"]:
            if step["distance"]["value"] in distances_qualifying_for_waypoints_list:
                waypoints += str(step["end_location"]["lat"])[:10] + "%2C" + str(step["end_location"]["lng"])[:10] + "%7C"
                waypoints += step["instructions"]

    # Appends the ending points to the waypoint string
    waypoints += str(google_response["routes"][0]["legs"][0]["end_location"]["lat"])[:10]
    waypoints += "%2C"
    waypoints += str(google_response["routes"][0]["legs"][0]["end_location"]["lng"])[:10]
       
    return waypoints

def create_route(my_account, form_data):
    google_response = json.loads(form_data["google_response"])
    
    route_data = {}

    route_data["phone"] = my_account.phone
    route_data["active"] = True
    route_data["start_location"] = parse_start_location(google_response)
    route_data["start_location_type"] = form_data["start_location_type"]
    route_data["end_location"] = parse_end_location(google_response)
    route_data["end_location_type"] = form_data["end_location_type"]
    route_data["waypoints"] = parse_waypoints(google_response)
    run_hour = int(form_data["local_run_time"][:2])
    run_minute = int(form_data["local_run_time"][3:])
    run_timezone_offset = int(form_data["local_timezone_offset"])
    route_data["local_run_time"] = time(run_hour, run_minute)
    route_data["local_timezone_offset"] = run_timezone_offset
    route_data["run_time"] = time(run_hour - run_timezone_offset, run_minute)
    route_data["delay_tolerance"] = form_data["delay_tolerance"]
    route_data["run_sunday"] = True if form_data.get("Sunday") else False
    route_data["run_monday"] = True if form_data.get("Monday") else False
    route_data["run_tuesday"] = True if form_data.get("Tuesday") else False
    route_data["run_wednesday"] = True if form_data.get("Wednesday") else False
    route_data["run_thursday"] = True if form_data.get("Thursday") else False
    route_data["run_friday"] = True if form_data.get("Friday") else False
    route_data["run_saturday"] = True if form_data.get("Saturday") else False

    new_route = Route(route_data)
    new_route.save()
    return "successssssss"
    