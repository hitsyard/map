import streamlit as st
import folium
import requests
from pymongo import MongoClient
from urllib.parse import quote_plus

# Function to fetch latitude and longitude for a given address using OpenCage Geocoding API
def get_lat_lon(address, api_key):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={address}&key={api_key}"
    response = requests.get(url).json()
    if response['status']['code'] == 200 and response['results']:
        location = response['results'][0]['geometry']
        return location['lat'], location['lng']
    else:
        return None, None

# Function to generate a folium map with all markers in red color
def generate_map(addresses):
    # Create a map centered around a default location
    map_ = folium.Map(location=[20.5937, 78.9629], zoom_start=5)  # Default center is India

    # Add markers for all addresses in the dictionary with red color
    for address, (lat, lon) in addresses.items():
        folium.Marker(location=[lat, lon], popup=f"{address}: ({lat}, {lon})", icon=folium.Icon(color='red')).add_to(map_)
    
    # Save the map as HTML
    map_html = map_._repr_html_()
    return map_html

# Connect to MongoDB
def get_mongo_client():
    username = quote_plus("socialhityard")  # Replace with your actual username
    password = quote_plus("hityard@001")  # Replace with your actual password
    connection_string = f"mongodb+srv://{username}:{password}@hits.g1nlzw0.mongodb.net/?retryWrites=true&w=majority&appName=hits"
    client = MongoClient(connection_string)
    return client

# Store address coordinates in MongoDB
def store_address_in_db(address, lat, lon):
    client = get_mongo_client()
    db = client['address_db']
    collection = db['addresses']
    collection.update_one(
        {"address": address},
        {"$set": {"lat": lat, "lon": lon}},
        upsert=True
    )
    client.close()

# Fetch all addresses from MongoDB
def fetch_addresses_from_db():
    client = get_mongo_client()
    db = client['address_db']
    collection = db['addresses']
    addresses = {doc['address']: (doc['lat'], doc['lon']) for doc in collection.find()}
    client.close()
    return addresses

# Set the page title and description
st.title("Address to Map Marker")
st.markdown("Enter an address in the sidebar to place a red marker on the map.")

# Sidebar layout for adding address
st.sidebar.title("Add Location")
address = st.sidebar.text_input("Enter Address")
add_address_button = st.sidebar.button("Add Address")

# Add address to MongoDB when button is clicked
if add_address_button:
    api_key = "28775787abd8490bb43264af7bf836aa"  # Replace with your actual API key
    lat, lon = get_lat_lon(address, api_key)
    if lat and lon:
        store_address_in_db(address, lat, lon)
        st.sidebar.success(f"Added {address}: ({lat}, {lon})")
    else:
        st.sidebar.error("Could not find coordinates for the given address")

# Show the map and a list of added addresses
if st.button("Show Map"):
    addresses = fetch_addresses_from_db()
    if addresses:
        st.markdown("### Map with Red Markers")
        map_html = generate_map(addresses)
        st.components.v1.html(map_html, height=500)

        st.markdown("### Added Addresses")
        for address, (lat, lon) in addresses.items():
            st.write(f"{address}: ({lat}, {lon})")
    else:
        st.error("No addresses added yet")

# Clear all addresses button
if st.button("Clear All"):
    client = get_mongo_client()
    db = client['address_db']
    collection = db['addresses']
    collection.delete_many({})
    client.close()
    st.success("Cleared all addresses")

# Add some spacing
st.markdown("<br><br>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("**Developed by Your Name**")
