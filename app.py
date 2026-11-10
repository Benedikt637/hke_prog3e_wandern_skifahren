#This is the main file of the project. It is executed when the project is run. It imports the necessary libraries and packages, as well as the functions and data from the main package. It then runs the main function of the project.
# Ausgabe der Projektdaten über main/application.py

### Infos für mich
#py -m  streamlit run  app.py
###


#-----Import of necessary libraries and packages-----#
import streamlit as st
import folium as fm
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation



#-----Import of functions and data-----#
import main         #__init__ is executed and imports the main/data.py and main/functions.py files

#------------------------------------------------------------------------#


#-----Initialization of the Page Layout-----#
st.set_page_config(layout="wide")
st.title("Hiking Routes Finder")
column1, column2 = st.columns([1, 4])



#-----Page Data-----#
with column1:
    selected_route = st.selectbox("Choose Hiking Destination:",
        sorted(main.data.route_names))
    st.text_input("Difficulty") 
    find_route = st.button("Find Route")


with column2:
    map = fm.Map(location=[47.714849, 10.312662], zoom_start=18, control_scale=True) #default location is HS-Kempten
    

    #if get_detected_location() is permitted by user, the map will be centered on the user's location otherwise it will be centered on the default location (HS-Kempten), a marker will show the centered location
    #-----Centeres the map on users location, otherweise HS-Kempten-----# 
    user_location = main.functions.get_detected_location()
    if ( 
        user_location
        and user_location.get("latitude") is not None
        and user_location.get("longitude") is not None
    ):
        map.location = [user_location["latitude"], user_location["longitude"]]
        main.functions.add_detected_location_marker(map, user_location) #adds a marker to the map at the user's location
    else:
        fm.Marker(location=[47.714849, 10.312662], tooltip="HS-Kempten").add_to(map) #adds a marker to the map at the default location (HS-Kempten) if the user's location is not detected



    #-----Displays the hiking routes-----#
    if find_route:
        selected_route_data = main.data.hiking_routes[
            main.data.hiking_routes["name"] == selected_route
            ]

    
        if not selected_route_data.empty:
            #-----Adds selected route to map-----#
            fm.GeoJson(
                main.data.hiking_routes,
                name="All Hiking Routes",
                style_function=lambda feature: {
                    "color": "green",
                    "weight": 3,
                    "opacity": 0.8
                },
                tooltip=fm.GeoJsonTooltip(
                    fields=["name"],
                    aliases=["Route Name:"],
                    labels=True
                )
            ).add_to(map)

        bounds = selected_route_data.total_bounds
        map.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    #-----Creates the map-----#
    st_folium(map, width=None, height=800, use_container_width=True) #generates the map in the streamlit app