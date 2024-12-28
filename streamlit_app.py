 import streamlit as st
import folium
from streamlit_folium import st_folium
from bostonzoning import BostonZoningApp
import os
from dotenv import load_dotenv

# Initialize session state
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'last_search' not in st.session_state:
    st.session_state.last_search = None
if 'last_result' not in st.session_state:
    st.session_state.last_result = None
if 'last_coordinates' not in st.session_state:
    st.session_state.last_coordinates = None

# Load environment variables
load_dotenv()

# Initialize the zoning app
zoning_app = BostonZoningApp()

# Page config
st.set_page_config(
    page_title="Boston Zoning Information",
    page_icon="🏢",
    layout="wide"
)

# Title
st.title("Boston Zoning Information")

# Sidebar with disclaimer
with st.sidebar:
    st.info("""
    **Disclaimer:** This information is provided for guidance only. 
    Please consult official documents or professionals for legal zoning advice.
    """)

# Create two columns
col1, col2 = st.columns([1, 1])

def search_address(address):
    """Function to handle address search"""
    with st.spinner("Retrieving zoning information..."):
        try:
            # Get coordinates
            coordinates = zoning_app.get_coordinates(address)
            
            if coordinates:
                st.session_state.last_coordinates = coordinates
                # Get zoning information
                response = zoning_app.get_zoning_info_raw(address)
                
                if response:
                    st.session_state.last_result = response
                    st.session_state.last_search = address
                    
                    # Add to search history if not already present
                    if address not in st.session_state.search_history:
                        st.session_state.search_history.append(address)
                    
                    return True
                else:
                    st.error("Unable to retrieve zoning information")
            else:
                st.error("Could not find coordinates for this address")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        return False

with col1:
    # Address input
    address = st.text_input(
        "Enter Boston address",
        placeholder="e.g., 1 City Hall Square, Boston, MA"
    )
    
    if st.button("Get Zoning Info", type="primary"):
        if address:
            search_address(address)
        else:
            st.warning("Please enter an address")

# Display results if they exist
if st.session_state.last_result and st.session_state.last_coordinates:
    with col1:
        st.subheader("Zoning Information")
        st.write(st.session_state.last_result)
        
        # Add download button
        st.download_button(
            label="Download Zoning Report",
            data=st.session_state.last_result,
            file_name=f"zoning_report_{st.session_state.last_search.replace(' ', '_')}.txt",
            mime="text/plain"
        )
    
    with col2:
        # Display map with marker
        m = folium.Map(location=st.session_state.last_coordinates, zoom_start=16)
        folium.Marker(
            st.session_state.last_coordinates, 
            popup=st.session_state.last_search
        ).add_to(m)
        st_folium(m, height=400, width=None)
else:
    # Initial map (Boston center)
    with col2:
        m = folium.Map(location=[42.3601, -71.0589], zoom_start=12)
        st_folium(m, height=400, width=None)

# Display search history in sidebar
with st.sidebar:
    if st.session_state.search_history:
        st.subheader("Recent Searches")
        for prev_address in st.session_state.search_history[-5:]:  # Show last 5 searches
            if st.button(prev_address, key=prev_address):
                search_address(prev_address) 
