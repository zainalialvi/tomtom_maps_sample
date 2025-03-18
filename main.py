import streamlit as st
import requests
import json
from typing import List, Tuple


# ---------------------------
# API Functions
# ---------------------------

def calculate_route(api_key: str, start_coords: str, end_coords: str, route_params: dict) -> dict:
    """
    Calculate a single route using the TomTom Routing API.
    """
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start_coords}:{end_coords}/json"
    params = {
        "routeRepresentation": route_params.get("routeRepresentation", "summaryOnly"),
        "computeTravelTimeFor": route_params.get("computeTravelTimeFor", "all"),
        "routeType": route_params.get("routeType", "fastest"),
        "traffic": route_params.get("traffic", "true"),
        "avoid": route_params.get("avoid", "unpavedRoads"),
        "key": api_key
    }
    response = requests.get(url, params=params)
    try:
        return response.json()
    except json.JSONDecodeError:
        st.error("Failed to decode JSON response for Single Route. Raw response:")
        st.error(response.text)
        return {}


def calculate_reachable_range(api_key: str, origin: str, budgets: dict) -> dict:
    """
    Calculate the reachable range from an origin using time, distance, or fuel budgets.
    """
    url = f"https://api.tomtom.com/routing/1/calculateReachableRange/{origin}/json"
    params = {
        "timeBudgetInSec": budgets.get("timeBudgetInSec"),
        "distanceBudgetInMeters": budgets.get("distanceBudgetInMeters"),
        "fuelBudgetInLiters": budgets.get("fuelBudgetInLiters"),
        "key": api_key
    }
    response = requests.post(url, params=params)
    try:
        return response.json()
    except json.JSONDecodeError:
        st.error("Failed to decode JSON response for Reachable Range. Raw response:")
        st.error(response.text)
        return {}


def batch_routing(api_key: str, routes: List[Tuple[str, str]], route_params: dict) -> dict:
    """
    Perform batch routing requests.
    """
    url = "https://api.tomtom.com/routing/1/batch/sync/json"
    headers = {"Content-Type": "application/json"}
    batch_items = []
    for start_coords, end_coords in routes:
        item = {
            "query": f"/routing/1/calculateRoute/{start_coords}:{end_coords}/json",
            "params": {
                "routeRepresentation": route_params.get("routeRepresentation", "summaryOnly"),
                "computeTravelTimeFor": route_params.get("computeTravelTimeFor", "all"),
                "routeType": route_params.get("routeType", "fastest"),
                "traffic": route_params.get("traffic", "true"),
                "avoid": route_params.get("avoid", "unpavedRoads"),
                "key": api_key
            }
        }
        batch_items.append(item)
    payload = {"batchItems": batch_items}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    try:
        return response.json()
    except json.JSONDecodeError:
        st.error("Failed to decode JSON response for Batch Routing. Raw response:")
        st.error(response.text)
        return {}


def matrix_routing(api_key: str, origins: List[Tuple[float, float]], destinations: List[Tuple[float, float]],
                   route_params: dict) -> dict:
    """
    Calculate a travel time/distance matrix between multiple origins and destinations.
    """
    url = "https://api.tomtom.com/routing/1/matrix/sync/json"
    headers = {"Content-Type": "application/json"}
    data = {
        "origins": [{"point": {"latitude": o[0], "longitude": o[1]}} for o in origins],
        "destinations": [{"point": {"latitude": d[0], "longitude": d[1]}} for d in destinations]
    }
    params = {
        "routeRepresentation": route_params.get("routeRepresentation", "summaryOnly"),
        "computeTravelTimeFor": route_params.get("computeTravelTimeFor", "all"),
        "routeType": route_params.get("routeType", "fastest"),
        "traffic": route_params.get("traffic", "true"),
        "avoid": route_params.get("avoid", "unpavedRoads"),
        "key": api_key
    }
    response = requests.post(url, headers=headers, params=params, json=data)
    try:
        return response.json()
    except json.JSONDecodeError:
        st.error("Failed to decode JSON response for Matrix Routing. Raw response:")
        st.error(response.text)
        return {}


# ---------------------------
# Streamlit User Interface
# ---------------------------

st.set_page_config(page_title="TomTom Routing API Explorer", layout="wide")
st.title("TomTom Routing API Explorer - Comprehensive")

# Sidebar: API Configuration and common parameters
with st.sidebar:
    st.header("API Configuration")
    api_key = st.text_input(value="kpcAP1yx7CaBHvUyfez9WySoKdWnWW6V", label="Enter your TomTom API Key", type="password")

    st.header("Common Route Parameters")
    route_representation = st.selectbox("Route Representation", ["summaryOnly", "polyline", "none"])
    compute_travel_time_for = st.selectbox("Compute Travel Time For", ["all", "none", "allExceptBlocked"])
    route_type = st.selectbox("Route Type", ["fastest", "shortest", "eco", "thrilling"])
    traffic = st.selectbox("Traffic", ["true", "false"])
    avoid = st.multiselect("Avoid", ["unpavedRoads", "tollRoads", "motorways", "ferries", "carpools"])
    common_params = {
        "routeRepresentation": route_representation,
        "computeTravelTimeFor": compute_travel_time_for,
        "routeType": route_type,
        "traffic": traffic,
        "avoid": ",".join(avoid) if avoid else ""
    }

# Create Tabs for Different Functionalities
tab1, tab2, tab3, tab4 = st.tabs(["Single Route", "Reachable Range", "Batch Routing", "Matrix Routing"])

# ---------------------------
# Tab 1: Single Route Calculation
# ---------------------------
with tab1:
    st.header("Single Route Calculation")
    col1, col2 = st.columns(2)
    with col1:
        start_lat = st.number_input("Start Latitude", value=42.37806, format="%.6f", key="single_start_lat")
        start_lon = st.number_input("Start Longitude", value=-87.94427, format="%.6f", key="single_start_lon")
    with col2:
        end_lat = st.number_input("End Latitude", value=42.39081, format="%.6f", key="single_end_lat")
        end_lon = st.number_input("End Longitude", value=-87.95857, format="%.6f", key="single_end_lon")

    if st.button("Calculate Single Route"):
        if api_key:
            start_coords = f"{start_lat},{start_lon}"
            end_coords = f"{end_lat},{end_lon}"
            result = calculate_route(api_key, start_coords, end_coords, common_params)
            st.subheader("Single Route Result")
            st.json(result)
        else:
            st.error("Please enter your API Key in the sidebar.")

# ---------------------------
# Tab 2: Reachable Range Calculation
# ---------------------------
with tab2:
    st.header("Reachable Range Calculation")
    origin_lat = st.number_input("Origin Latitude", value=42.37806, format="%.6f", key="range_origin_lat")
    origin_lon = st.number_input("Origin Longitude", value=-87.94427, format="%.6f", key="range_origin_lon")
    time_budget = st.number_input("Time Budget (sec)", value=3600, step=60)
    distance_budget = st.number_input("Distance Budget (meters)", value=10000, step=100)
    fuel_budget = st.number_input("Fuel Budget (liters)", value=10.0, format="%.2f")

    if st.button("Calculate Reachable Range"):
        if api_key:
            origin = f"{origin_lat},{origin_lon}"
            budgets = {
                "timeBudgetInSec": time_budget,
                "distanceBudgetInMeters": distance_budget,
                "fuelBudgetInLiters": fuel_budget
            }
            result = calculate_reachable_range(api_key, origin, budgets)
            st.subheader("Reachable Range Result")
            st.json(result)
        else:
            st.error("Please enter your API Key in the sidebar.")

# ---------------------------
# Tab 3: Batch Routing
# ---------------------------
with tab3:
    st.header("Batch Routing")
    num_routes = st.number_input("Number of Routes", min_value=1, max_value=5, value=1, step=1, key="batch_num_routes")
    batch_routes = []
    for i in range(int(num_routes)):
        st.markdown(f"### Route {i + 1}")
        col1, col2 = st.columns(2)
        with col1:
            b_start_lat = st.number_input(f"Start Latitude {i + 1}", value=42.37806, format="%.6f",
                                          key=f"batch_start_lat_{i}")
            b_start_lon = st.number_input(f"Start Longitude {i + 1}", value=-87.94427, format="%.6f",
                                          key=f"batch_start_lon_{i}")
        with col2:
            b_end_lat = st.number_input(f"End Latitude {i + 1}", value=42.39081, format="%.6f",
                                        key=f"batch_end_lat_{i}")
            b_end_lon = st.number_input(f"End Longitude {i + 1}", value=-87.95857, format="%.6f",
                                        key=f"batch_end_lon_{i}")
        batch_routes.append((f"{b_start_lat},{b_start_lon}", f"{b_end_lat},{b_end_lon}"))

    if st.button("Calculate Batch Routes"):
        if api_key:
            result = batch_routing(api_key, batch_routes, common_params)
            st.subheader("Batch Routing Result")
            st.json(result)
        else:
            st.error("Please enter your API Key in the sidebar.")

# ---------------------------
# Tab 4: Matrix Routing
# ---------------------------
with tab4:
    st.header("Matrix Routing")

    st.markdown("#### Origins")
    num_origins = st.number_input("Number of Origins", min_value=1, max_value=5, value=1, step=1,
                                  key="matrix_num_origins")
    origins = []
    for i in range(int(num_origins)):
        col1, col2 = st.columns(2)
        with col1:
            origin_lat = st.number_input(f"Origin Latitude {i + 1}", value=42.37806, format="%.6f",
                                         key=f"matrix_origin_lat_{i}")
        with col2:
            origin_lon = st.number_input(f"Origin Longitude {i + 1}", value=-87.94427, format="%.6f",
                                         key=f"matrix_origin_lon_{i}")
        origins.append((origin_lat, origin_lon))

    st.markdown("#### Destinations")
    num_destinations = st.number_input("Number of Destinations", min_value=1, max_value=5, value=1, step=1,
                                       key="matrix_num_destinations")
    destinations = []
    for i in range(int(num_destinations)):
        col1, col2 = st.columns(2)
        with col1:
            dest_lat = st.number_input(f"Destination Latitude {i + 1}", value=42.39081, format="%.6f",
                                       key=f"matrix_dest_lat_{i}")
        with col2:
            dest_lon = st.number_input(f"Destination Longitude {i + 1}", value=-87.95857, format="%.6f",
                                       key=f"matrix_dest_lon_{i}")
        destinations.append((dest_lat, dest_lon))

    if st.button("Calculate Matrix Routing"):
        if api_key:
            result = matrix_routing(api_key, origins, destinations, common_params)
            st.subheader("Matrix Routing Result")
            st.json(result)
        else:
            st.error("Please enter your API Key in the sidebar.")
