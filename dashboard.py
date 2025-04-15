#1
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st


st.set_page_config(layout="wide")
sns.set(style="whitegrid")


@st.cache_data
def load_data():
    riyadh = pd.read_csv("Riyadh_cleaned.csv")
    paris = pd.read_csv("Paris_cleaned.csv")
    lax = pd.read_csv("LAX_BEI_cleaned.csv")
    weather = pd.read_csv("weather_temp.csv")

    return riyadh, paris, lax, weather

riyadh, paris, lax, weather = load_data()



st.header("📅 Seasonal Overview")

all_data = pd.concat([riyadh, paris, lax])
season_group = all_data.groupby("Season")

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg. Flight Price", f"${all_data['Price'].mean():.2f}")
col2.metric("Avg. Duration", f"{all_data['Duration in Minutes'].mean():.0f} min")
col3.metric("Most Common Airline", all_data['Airline'].mode()[0])
col4.metric("Avg. Temperature", f"{weather['Average Temp (°C)'].mean():.1f}°C")

# Filter options in the first column (beside the chart)
with col1:
    st.subheader("Filter Options")
    country = st.selectbox("Select Country", ["Riyadh", "Paris", "LAX"], index=0)
    season = st.selectbox("Select Season", ["Winter", "Spring", "Summer", "Fall"])

# Filter data based on user selection
if country == "Riyadh":
    selected_data = riyadh
elif country == "Paris":
    selected_data = paris
else:
    selected_data = lax

# Filter the data by selected season
season_filtered_data = selected_data[selected_data['Season'] == season]

# Pie Chart for Flight Type per Selected Season
with col2:
    st.subheader(f"✈️ Flight Types in {season} for {country}")
    flight_types_season = season_filtered_data['Flight Type'].value_counts()

    # Plot pie chart for the selected season and country
    fig1, ax1 = plt.subplots(figsize=(6, 6))  # Smaller pie chart size
    flight_types_season.plot.pie(autopct='%1.1f%%', ax=ax1, labels=flight_types_season.index, title=f"Flight Types in {season}")
    ax1.set_ylabel('')
    st.pyplot(fig1)


# Line Chart

country = st.selectbox("Select Country", ["Riyadh", "Paris", "LAX"], index=0, key="country_selectbox")

# Label route (country) for each dataset
riyadh['Route'] = 'Riyadh'
paris['Route'] = 'Paris'
lax['Route'] = 'LAX'

# Combine all datasets
all_data = pd.concat([riyadh, paris, lax])
all_data['Departure'] = pd.to_datetime(all_data['Departure'])
all_data['Month'] = all_data['Departure'].dt.to_period('M').astype(str)

# Filter the data based on the selected country
filtered_data = all_data[all_data['Route'] == country]

# Group by Route, Month, and Season
grouped = filtered_data.groupby(['Route', 'Month', 'Season'])['Price'].mean().reset_index()

# Plot for the selected country
st.subheader(f"📈 Avg. Price Over Time by Season - {country}")

# Pivot the data for plotting
pivot = grouped.pivot(index='Month', columns='Season', values='Price').fillna(0)

# Plot the line chart
fig, ax = plt.subplots(figsize=(8, 4))
pivot.plot(ax=ax, marker='o')
ax.set_title(f"Avg. Price Over Time by Season - {country}")
ax.set_xlabel("Month")
ax.set_ylabel("Average Price")
ax.legend(title="Season")
st.pyplot(fig)


# Group by Airline to get average price
# Filter options for country with a unique key
st.subheader("Top 20 Avg Airline Price per Country")
country = st.selectbox("Select Country", ["Riyadh", "Paris", "LAX"], index=0, key="country_selectbox_unique")

# Function to get top 20 airlines and their average prices for a country
def plot_top_20_airlines(df, route_label):
    top20_airlines = df['Airline'].value_counts().nlargest(20).index
    df_top20 = df[df['Airline'].isin(top20_airlines)]

    avg_prices = df_top20.groupby('Airline')['Price'].mean().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=avg_prices.values, y=avg_prices.index, ax=ax, palette='viridis')
    ax.set_title(f"{route_label} - Top 20 Airlines by Avg Price")
    ax.set_xlabel("Average Price ($)")
    ax.set_ylabel("Airline")
    st.pyplot(fig)

# Map the selected country to the corresponding DataFrame
if country == "Riyadh":
    plot_top_20_airlines(riyadh, 'Riyadh')
elif country == "Paris":
    plot_top_20_airlines(paris, 'Paris')
else:
    plot_top_20_airlines(lax, 'LAX')

st.subheader("💰 Price vs Competitor Price (Top 15 Airlines Per Country)")

def plot_price_comparison(df, route_label):
    # Get top 15 airlines by frequency
    top_airlines = df['Airline'].value_counts().nlargest(15).index
    df_filtered = df[df['Airline'].isin(top_airlines)]

    # Group by Airline and calculate average Price and Competitor Price
    grouped = df_filtered.groupby('Airline')[['Price', 'Competitor Price']].mean().sort_values(by='Price', ascending=False)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    grouped.plot(kind='bar', ax=ax, width=0.75)
    ax.set_title(f"{route_label} - Avg Price vs Competitor Price")
    ax.set_xlabel("Airline")
    ax.set_ylabel("Price ($)")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

# One plot per country
plot_price_comparison(riyadh, 'Riyadh')
plot_price_comparison(paris, 'Paris')
plot_price_comparison(lax, 'LAX')

st.subheader("📊 Price Type Distribution Across Seasons")




# Group by Season and Price Type
season_price_type = all_data.groupby(['Season', 'Price Type']).size().unstack(fill_value=0)

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
season_price_type.plot(kind='bar', stacked=True, ax=ax, colormap='Set2')
ax.set_title("Price Type Count by Season")
ax.set_xlabel("Season")
ax.set_ylabel("Number of Flights")
ax.legend(title="Price Type")
st.pyplot(fig)


# Filter by Season


st.subheader("📊 Price per Hour vs Transit (Per Country)")
selected_route = st.selectbox("Choose Route", ['Riyadh', 'Paris', 'LAX'])
season_options = all_data['Season'].unique()
selected_season = st.selectbox("Select Season", season_options)
route_data = all_data[all_data['Route'] == selected_route]

fig, ax = plt.subplots(figsize=(7, 4))
sns.boxplot(x='Transit', y='Price per Hour', data=route_data, ax=ax, palette='pastel')
ax.set_title(f'Price per Hour vs Transit - {selected_route}')
ax.set_xlabel('Number of Transit Stops')
ax.set_ylabel('Price per Hour ($)')
st.pyplot(fig)

import plotly.express as px

st.header("🌡️ Temperature vs. Flight Prices")

# Add interactive filters
col1, col2 = st.columns(2)
with col1:
    selected_country = st.selectbox(
        "Select Departure Country",
        ["All", "Riyadh", "Paris", "LAX"],
        index=0
    )
with col2:
    selected_season = st.selectbox(
        "Select Season",
        ["All", "Winter", "Spring", "Summer", "Fall"],
        index=0
    )

# Prepare Beirut weather data
weather_beirut = weather[weather['Location'] == "Beirut"].copy()
weather_beirut['Date'] = pd.to_datetime(weather_beirut['Date'])


# Function to merge flight data with Beirut weather
def prepare_flight_weather(flight_df, route_name):
    flight_df['Departure'] = pd.to_datetime(flight_df['Departure'])
    merged = pd.merge(flight_df, weather_beirut, left_on='Departure', right_on='Date')
    merged['Route'] = route_name
    return merged


# Prepare data for all routes
all_routes = pd.concat([
    prepare_flight_weather(riyadh, "Riyadh"),
    prepare_flight_weather(paris, "Paris"),
    prepare_flight_weather(lax, "LAX")
])

# Apply filters
filtered_data = all_routes.copy()
if selected_country != "All":
    filtered_data = filtered_data[filtered_data['Route'] == selected_country]

if selected_season != "All":
    filtered_data = filtered_data[filtered_data['Season'] == selected_season]

# Visualization 1: Scatter plot
st.subheader(
    f"🟠 Temperature vs. Price ({selected_country if selected_country != 'All' else 'All Routes'} - {selected_season if selected_season != 'All' else 'All Seasons'})")

# Using matplotlib as fallback if Plotly fails
try:
    fig1 = px.scatter(
        filtered_data,
        x='Average Temp (°C)',
        y='Price',
        color='Route',
        trendline="ols",
        hover_data=['Departure', 'Airline', 'Flight Type']
    )
    st.plotly_chart(fig1, use_container_width=True)
except:
    # Fallback to matplotlib if Plotly fails
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=filtered_data,
        x='Average Temp (°C)',
        y='Price',
        hue='Route',
        style='Season',
        s=100
    )
    plt.title(f"Temperature vs. Price ({selected_country if selected_country != 'All' else 'All Routes'})")
    plt.xlabel("Beirut Temperature (°C)")
    plt.ylabel("Flight Price ($)")
    st.pyplot(plt.gcf())


# Visualization 2: Seasonal breakdown (only show if no season filter)
if selected_season == "All":
    st.subheader("📈 Seasonal Patterns")
    seasons = ["Winter", "Spring", "Summer"]  # Removed "Fall" from this list

    # Create a 1x3 grid of seasonal plots (3 seasons now)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))  # Changed to 1 row, 3 columns

    for i, season in enumerate(seasons):
        season_data = filtered_data[filtered_data['Season'] == season]
        sns.scatterplot(
            data=season_data,
            x='Average Temp (°C)',
            y='Price',
            hue='Route',
            ax=axes[i]
        )
        axes[i].set_title(season)
        axes[i].set_xlabel("Temperature (°C)")
        axes[i].set_ylabel("Price ($)")  # Now showing on all plots since they're in one row

    plt.tight_layout()
    st.pyplot(fig)


st.header("🌡️ Flight Prices by Temperature Range")

# Get Beirut temperature range from weather data
min_temp = int(weather['Average Temp (°C)'].min())
max_temp = int(weather['Average Temp (°C)'].max())

# Create temperature slider
temp_range = st.slider(
    "Select Temperature Range (°C)",
    min_value=min_temp,
    max_value=max_temp,
    value=(10, 25)  # Default range
)

# Filter weather data for Beirut
beirut_weather = weather[weather['Location'] == "Beirut"].copy()
beirut_weather['Date'] = pd.to_datetime(beirut_weather['Date'])

# Merge flight data with weather
def merge_flight_weather(flight_df, route_name):
    flight_df['Departure'] = pd.to_datetime(flight_df['Departure'])
    merged = pd.merge(flight_df, beirut_weather, left_on='Departure', right_on='Date')
    merged['Route'] = route_name
    return merged

# Prepare combined data
all_routes = pd.concat([
    merge_flight_weather(riyadh, "Riyadh"),
    merge_flight_weather(paris, "Paris"),
    merge_flight_weather(lax, "LAX")
])

# Filter by temperature range
filtered = all_routes[
    (all_routes['Average Temp (°C)'] >= temp_range[0]) &
    (all_routes['Average Temp (°C)'] <= temp_range[1])
]

# Create visualization
fig = px.box(
    filtered,
    x='Route',
    y='Price',
    color='Route',
    points="all",
    hover_data=['Departure', 'Airline'],
    title=f"Flight Prices at {temp_range[0]}°C to {temp_range[1]}°C in Beirut"
)

# Customize layout
fig.update_layout(
    xaxis_title="Departure City",
    yaxis_title="Price ($)",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# Show raw data
with st.expander("View Raw Data"):
    st.dataframe(filtered[['Route', 'Departure', 'Airline', 'Price', 'Average Temp (°C)']]
                .sort_values('Price', ascending=False))


