from datetime import datetime, timedelta
import streamlit as st
from fetch import AmadeusAPI
from algorithms import geographic_midpoint, find_cheapest_combination
import folium
from streamlit_folium import folium_static

if 'amadeus' not in st.session_state:
  st.session_state.amadeus = AmadeusAPI(client_id=st.secrets.AMADEUS_CLIENT_ID,
                                        client_secret=st.secrets.AMADEUS_CLIENT_SECRET)

prices = {}
flight_paths = {}
destination_airports = []
possible_lat_offsets = [0, 5, -5]
possible_long_offsets = [0, 5, -5]

st.title('Where To Meet? ✈️')

# Date inputs for departure and return dates and number of guests
col1, col2, col3 = st.columns(3)
with col1:
  departure_date = st.date_input("Departure Date", value=datetime.now() + timedelta(days=1))
  if departure_date == datetime.now().date():
    st.warning("Please select a future date")
with col2:
  return_date = st.date_input("Return Date", value=datetime.now() + timedelta(days=7))
with col3:
  num_guests = st.number_input("Number of Guests", min_value=2, max_value=8, step=1)

# Guest details input
guests = []
cols = st.columns(2)
for i in range(num_guests):
  col = cols[i % 2]
  with col:
    st.html("<div style='border: 1px solid #ddd;'></div>")
    st.subheader(f"Guest {i + 1}")
    sub_col1, sub_col2 = st.columns(2)
    name = sub_col1.text_input(f"Name", key=f"name_{i}")
    home_airport = sub_col2.text_input(f"Home Airport", key=f"home_airport_{i}")
    guests.append({"name": name, "home_airport": home_airport})

  if i % 2 == 1 and i != num_guests - 1:
    cols = st.columns(2)

# Button to trigger the API call
if st.button("Fetch Data"):
  # Fetch coordinates for each guest's home airport
  with st.spinner('Fetching airport coordinates...'):
    for guest in guests:
      coordinates = st.session_state.amadeus.get_airport_coordinates(guest['home_airport'])
      if coordinates:
        guest['lat'], guest['long'] = coordinates
      else:
        st.error(f"Failed to fetch coordinates for {guest['home_airport']}")
        st.stop()

  with st.spinner("Calculating the geographic midpoint..."):
    # Calculate the geographic midpoint of all guests' home airports
    latitudes = [guest['lat'] for guest in guests]
    longitudes = [guest['long'] for guest in guests]
    midpoint = geographic_midpoint(list(zip(latitudes, longitudes)))
    if not midpoint:
      st.error("Failed to calculate the geographic midpoint")
      st.stop()

  with st.spinner("Finding the closet airport..."):
    midpoint_lat, midpoint_long = midpoint
    for i in range(len(possible_lat_offsets)):
        possible_airport = st.session_state.amadeus.get_nearest_airport(midpoint_lat + possible_lat_offsets[i], midpoint_long + possible_long_offsets[i])

        if possible_airport and possible_airport not in destination_airports:
          destination_airports.append(possible_airport)

    st.success(f"The midpoint airports are: {destination_airports}")

  # Fetch flight offers for each guest
  with st.spinner('Fetching flight offers...'):
    for destination_airport in destination_airports:
      for guest in guests:
        with st.spinner(f"Fetching data for {guest['name']} going to {destination_airport}..."):
          data = st.session_state.amadeus.get_flight_offers(guest['home_airport'], destination_airport, departure_date, return_date)
          if data:
            if prices.get(destination_airport) is None:
              prices[destination_airport] = {}

            if flight_paths.get(destination_airport) is None:
              flight_paths[destination_airport] = {}

            for offer in data:
              prices[destination_airport][guest['name']] = offer['price']
              flight_paths[destination_airport][guest['name']] = offer['flight_paths']

          else:
            st.error(f"Failed to fetch data for {guest['home_airport']}")
            st.stop()

  if len(prices) > 0:
    print(flight_paths)
    cheapest_destination, min_total_cost = find_cheapest_combination(prices)

    # Display the result
    # Display the result in a pretty table
    st.header("Destination 📍 and Cost 🤑")
    col1, col2 = st.columns(2)
    col1.metric("Optimized Destination", cheapest_destination)
    col2.metric("Minimum Total Cost", f"${min_total_cost:.2f}")

    # Display a table of each guest and their flight paths to the cheapest destination
    st.header(f"Flight Info 🛫")

    # Calculate the average cost per person
    average_cost = min_total_cost / num_guests

    # Create columns for each guest
    rows = (num_guests + 1) // 2
    for row in range(rows):
      cols = st.columns(2)
      for col_idx in range(2):
        guest_idx = row * 2 + col_idx
        if guest_idx < num_guests:
          guest = guests[guest_idx]
          with cols[col_idx]:
            st.metric(label="Guest", value=guest['name'])
            if guest['name'] in flight_paths[cheapest_destination]:
              for i, path in enumerate(flight_paths[cheapest_destination][guest['name']].values()):
                st.metric(label="to" if i == 0 else "return", value=" ➡️ ".join(path))

              price = prices[cheapest_destination][guest['name']]
              delta = price - average_cost
              st.metric(label="Price", value=f"${price:.2f}", delta=f"{delta:.2f}", delta_color="normal")
            else:
              st.write("No flight path available")
              st.metric(label="Price", value="N/A")

    # Create a map centered around the midpoint
    st.header("Flight Map 🧭")

    destination_airport_coords = st.session_state.amadeus.get_airport_coordinates(cheapest_destination)
    m = folium.Map(location=destination_airport_coords, zoom_start=3)

    # Add markers for each guest's home airport
    for guest in guests:
      folium.Marker(
      location=[guest['lat'], guest['long']],
      popup=f"{guest['name']} - {guest['home_airport']}",
      icon=folium.Icon(color='blue')
      ).add_to(m)

    # Add markers for each destination airport
    folium.Marker(
      location=destination_airport_coords,
      popup=f"Destination: {cheapest_destination}",
      icon=folium.Icon(color='red')
    ).add_to(m)

    # Draw lines from each guest's home airport to the destination airport
    for guest in guests:
      folium.PolyLine(
      locations=[[guest['lat'], guest['long']], destination_airport_coords],
      color='green',
      weight=2.5,
      opacity=1
      ).add_to(m)

    # Display the map
    folium_static(m)