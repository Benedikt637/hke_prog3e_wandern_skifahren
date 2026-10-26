import folium
from streamlit_geolocation import streamlit_geolocation


#-----Add Current Location as Marker-----#
def get_detected_location():
    return streamlit_geolocation()


def add_detected_location_marker(map_object, detected_location):

    if not detected_location or "latitude" not in detected_location or "longitude" not in detected_location:
        return map_object  # Return the original map if no location is detected

    detected_latitude = detected_location["latitude"]
    detected_longitude = detected_location["longitude"]
    print(f"Location found: {detected_location['latitude']}, {detected_location['longitude']}")
    map_object.location = [detected_latitude, detected_longitude]
    folium.Marker([detected_latitude, detected_longitude], tooltip="Your Location").add_to(map_object)
    return map_object