import requests
import streamlit as st
import json


def calculate_route(a: str, start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json"
    params = {
        "routeRepresentation": "summaryOnly",
        "computeTravelTimeFor": "all",
        "routeType": "fastest",
        "traffic": "true",
        "avoid": "unpavedRoads",
        "key": a
    }
    headers = {"accept": "*/*"}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error making request: {e}")
        return None

st.set_page_config(page_title="TomTom Route Planner", layout="wide")
st.title("TomTom Route Planner")

col1, col2 = st.columns(2)
with col1:
    start_lat = st.number_input("Start Latitude", value=42.37806, format="%f")
    end_lat = st.number_input("End Latitude", value=42.39081, format="%f")
with col2:
    start_lon = st.number_input("Start Longitude", value=-87.94427, format="%f")
    end_lon = st.number_input("End Longitude", value=-87.95857, format="%f")

if st.button("Calculate Route"):
    a = "kpcAP1yx7CaBHvUyfez9WySoKdWnWW6V"
    if a:
        route_result = calculate_route(a, start_lat, start_lon, end_lat, end_lon)
        if route_result:
            st.subheader("Route Summary")
            route_summary = route_result.get("routes", [{}])[0].get("summary", {})
            st.json(route_summary, expanded=False)

            st.subheader("Full Response")
            st.json(route_result, expanded=False)
    else:
        st.warning("exception")
