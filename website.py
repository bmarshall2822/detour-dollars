import streamlit as st

st.set_page_config(page_title="Detour Dollars", page_icon="⛽")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

html, body, .stApp,
h1, h2, h3, p, label, input, button {
    font-family: 'Nunito', sans-serif !important;
}
h1 {
    font-weight: 800 !important;
}
.stButton button {
    border-radius: 12px;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

st.title("Detour Dollars  ⛽")
st.markdown("**Is cheaper gas worth the drive?**")

units = st.radio(
    "Choose your units",
    ["Canada (L / km)", "USA (US gal / miles)"],
    horizontal=True,
    label_visibility="collapsed"
)

canada = units == "Canada (L / km)"

# Separate input keys keep Canadian and American entries independent.
prefix = "ca" if canada else "us"

if canada:
    price_unit = "cents/L"
    volume_unit = "litres"
    distance_unit = "km"
    consumption_label = "Fuel consumption (L/100 km)"

    price_example = "192.9"
    volume_example = "40"
    consumption_example = "8.5"

    volume_help = (
        "Enter the amount you plan to buy, not your full tank capacity.\n\n"
        "Rough tank-size estimates:\n\n"
        "• Car: 40–60 L\n\n"
        "• SUV: 50–80 L\n\n"
        "• Pickup truck: 80–130 L\n\n"
        "Actual sizes vary by model."
    )

    consumption_help = (
        "Litres used to travel 100 km. Lower means less fuel used.\n\n"
        "Rough gasoline-vehicle estimates, not measured averages:\n\n"
        "• Car: 6–9 L/100 km\n\n"
        "• SUV: 8–12 L/100 km\n\n"
        "• Pickup truck: 11–16 L/100 km\n\n"
        "Use your dashboard's average when available."
    )

else:
    price_unit = "$/US gal"
    volume_unit = "US gallons"
    distance_unit = "miles"
    consumption_label = "Fuel economy (MPG — US gallons)"

    price_example = "3.49"
    volume_example = "12"
    consumption_example = "28"

    volume_help = (
        "Enter the amount you plan to buy, not your full tank capacity.\n\n"
        "Rough tank-size estimates:\n\n"
        "• Car: 11–16 US gal\n\n"
        "• SUV: 13–21 US gal\n\n"
        "• Pickup truck: 21–34 US gal\n\n"
        "Actual sizes vary by model."
    )

    consumption_help = (
        "Miles travelled per US gallon. Higher means less fuel used.\n\n"
        "Rough gasoline-vehicle estimates, not measured averages:\n\n"
        "• Car: 26–39 MPG\n\n"
        "• SUV: 20–29 MPG\n\n"
        "• Pickup truck: 15–21 MPG\n\n"
        "Use your dashboard's average when available. "
        "These are US gallons, not British imperial gallons."
    )

nearby_price = st.number_input(
    f"Nearby gas price ({price_unit})",
    min_value=0.001,
    max_value=1000.0,
    value=None,
    step=0.1 if canada else 0.01,
    format="%.1f" if canada else "%.3f",
    placeholder=f"Example: {price_example}",
    help="Compare the same fuel grade at both stations.",
    key=f"{prefix}_nearby"
)

cheaper_price = st.number_input(
    f"Farther gas price ({price_unit})",
    min_value=0.001,
    max_value=1000.0,
    value=None,
    format="%.1f" if canada else "%.3f",
    step=0.1 if canada else 0.01,
    
    placeholder=f"Example: {'180.9' if canada else '3.29'}",
    key=f"{prefix}_farther"
)

amount = st.number_input(
    f"How many {volume_unit} will you buy?",
    min_value=0.1,
    max_value=1000.0,
    value=None,
    step=1.0,
    placeholder=f"Example: {volume_example}",
    help=volume_help,
    key=f"{prefix}_amount"
)

consumption = st.number_input(
    consumption_label,
    min_value=0.1,
    max_value=300.0,
    value=None,
    step=0.1,
    placeholder=f"Example: {consumption_example}",
    help=consumption_help,
    key=f"{prefix}_consumption"
)

extra_distance = st.number_input(
    f"Total extra {distance_unit}",
    min_value=0.0,
    max_value=10000.0,
    value=None,
    step=1.0,
    placeholder="Example: 10",
    help=(
        "Enter only the extra distance compared with using the nearby "
        "station, including the return trip or detour."
    ),
    key=f"{prefix}_distance"
)

if st.button("Calculate savings", type="primary"):
    entries = [
        nearby_price, cheaper_price, amount,
        consumption, extra_distance
    ]

    if any(value is None for value in entries):
        st.warning("Please fill in every box.")
        st.stop()

    # Convert Canadian cents to dollars.
    # American prices are already in dollars.
    nearby_dollars = nearby_price / 100 if canada else nearby_price
    farther_dollars = cheaper_price / 100 if canada else cheaper_price

    gross_savings = (nearby_dollars - farther_dollars) * amount

    if canada:
        fuel_per_distance = consumption / 100  # Litres per km
    else:
        fuel_per_distance = 1 / consumption    # US gallons per mile

    extra_fuel = extra_distance * fuel_per_distance
    driving_cost = extra_fuel * farther_dollars
    net_savings = round(gross_savings - driving_cost, 2)

    currency = "CAD" if canada else "USD"

    if net_savings > 0:
        st.success(
            f"The farther station saves you "
            f"${net_savings:.2f} !"
        )
    elif net_savings < 0:
        st.warning(
            f"The nearby station saves you "
            f"${abs(net_savings):.2f} !"
        )
    else:
        st.info("Both options cost the same to the nearest cent.")

    st.write(
        f"Savings before driving costs: "
        f"${gross_savings:.2f} "
    )
    st.write(
        f"Extra driving cost: ${driving_cost:.2f} "
    )

    cost_per_distance = fuel_per_distance * farther_dollars

    if gross_savings > 0:
        break_even = gross_savings / cost_per_distance
        st.write(
            f"You break even at {break_even:.1f} "
            f"total extra {distance_unit}."
        )
    else:
        st.write("There are no fuel-price savings to justify a detour.")

st.caption(
    "Fuel costs only. Excludes your time and vehicle wear. "
    "Extra fuel is valued at the farther station's price."
)