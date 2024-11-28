import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Custom CSS for background image and styling the title
st.markdown("""
    <style>
        body {
            background-image: url('https://img.lovepik.com/background/20211022/large/lovepik-gorgeous-high-tech-picture-background-image_500638596.jpg');
            background-size: cover;
            background-position: center center;
            color: white;
        }
        .title {
            font-family: 'Arial', sans-serif;
            font-size: 36px;
            color: #FF4500;
            text-align: center;
        }
        .subtitle {
            font-family: 'Arial', sans-serif;
            font-size: 24px;
            color: #FFD700;
        }
        .stButton>button {
            background-color: #FF6347;
            color: white;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# App Title
st.markdown('<p class="title">Comprehensive Dashboard for Climate Data and Crop Yield Suggestions</p>', unsafe_allow_html=True)

# File Upload
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    # Load the dataset
    df = pd.read_csv(uploaded_file)

    # Normalize column names
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()

    # Sidebar: Filters for Country and Year
    st.sidebar.header("Filters")
    unique_countries = sorted(df['country'].unique())
    selected_country = st.sidebar.selectbox("Select Country", [None] + unique_countries)

    unique_years = sorted(df['year'].unique())
    selected_year = st.sidebar.selectbox("Select Year", [None] + unique_years)

    # Apply filters to the data
    filtered_df = df.copy()
    if selected_country:
        filtered_df = filtered_df[filtered_df['country'] == selected_country]
    if selected_year:
        filtered_df = filtered_df[filtered_df['year'] == selected_year]

    # Part 1: Predicted Temperature, CO2, and Crop Yield Suggestions
    st.header("Part 1: Predicted Temperature, CO2, and Crop Yield Suggestions")
    if not filtered_df.empty:
        predicted_temp = filtered_df['temperature_anomaly'].mean()
        predicted_co2 = filtered_df['average_co2'].mean()

        # Display predictions
        st.write(f"**Predicted Temperature Anomaly:** {predicted_temp:.2f}°C")
        st.write(f"**Predicted Average CO2 Level:** {predicted_co2:.2f} ppm")

        # Crop suggestion logic
        st.subheader("Suggested Crop to Yield")
        if predicted_temp > 1.5 and predicted_co2 > 400:
            st.write("It is recommended to yield crops like **Wheat, Corn, or Soybeans**.")
        elif predicted_temp > 1.0 and predicted_co2 <= 400:
            st.write("It is recommended to yield crops like **Rice, Oats, or Barley**.")
        else:
            st.write("It is recommended to yield crops like **Potatoes, Tomatoes, or Lettuce**.")
    else:
        st.warning("No data available for the selected country and year. Adjust filters or upload a different dataset.")

    # Part 2: Dual-Axis Plot (Entire Dataset)
    st.header("Part 2: Temperature and CO2 Levels Over Time (Entire Dataset)")
    if not df.empty:
        fig = go.Figure()

        # Add Temperature (C) trace
        fig.add_trace(go.Scatter(
            x=df['year'],
            y=df['temperature_anomaly'],
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Temperature (C)'
        ))

        # Add CO2 Concentration (PPM) trace
        fig.add_trace(go.Scatter(
            x=df['year'],
            y=df['average_co2'],
            mode='lines',
            line=dict(color='black'),
            name='CO2 (PPM)'
        ))

        # Customize layout with secondary y-axis
        fig.update_layout(
            title="Temperature and CO2 Concentration Over Time (Entire Dataset)",
            xaxis=dict(title="Year"),
            yaxis=dict(
                title="Temperature (C)",
                titlefont=dict(color="red"),
                tickfont=dict(color="red"),
            ),
            yaxis2=dict(
                title="Concentration (PPM)",
                titlefont=dict(color="black"),
                tickfont=dict(color="black"),
                overlaying="y",
                side="right",
            ),
            legend=dict(
                x=0.5,
                y=1.2,
                orientation="h"
            ),
            plot_bgcolor="rgba(0, 0, 0, 0.1)"  # Add slight transparency to the background
        )

        # Display the dual-axis plot
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available to display the dual-axis plot. Please upload a dataset.")

    # Part 3: Map Visualization (Highlight Selected Country and Year)
    st.header("Part 3: Map of Predicted Temperature and CO2 Levels")

    # Prepare the data for mapping
    map_data = df[df['year'] == selected_year] if selected_year else df

    if not map_data.empty:
        map_data['highlight'] = map_data['country'].apply(
            lambda x: "Selected Country" if x == selected_country else "Other Countries"
        )

        # Generate map plot using country names
        map_fig = px.choropleth(
            map_data,
            locations="country",  # Column containing country names
            locationmode="country names",  # Maps the names to the map
            color="temperature_anomaly",  # Color represents temperature anomaly
            hover_name="country",  # Hover information
            hover_data=["average_co2", "temperature_anomaly"],  # Show CO2 and temperature anomaly on hover
            title="Predicted Temperature and CO2 Levels by Country",
            color_continuous_scale="Viridis",
        )

        # Highlight the selected country
        if selected_country:
            map_fig.update_traces(
                marker=dict(line=dict(color="black", width=0.5)),
                selector=dict(name="Selected Country"),
            )

        # Display map
        st.plotly_chart(map_fig, use_container_width=True)
    else:
        st.warning("No data available for the selected year to display the map.")

    # Part 4: Custom Plots (Sidebar Options)
    st.sidebar.header("Visualization Options")
    plot_type = st.sidebar.selectbox("Select Plot Type", ["Scatter Plot", "Line Chart", "Bar Chart", "Pie Chart", "Histogram"])
    x_axis = st.sidebar.selectbox("Select X-Axis", df.columns)
    y_axis = st.sidebar.selectbox("Select Y-Axis", df.columns, disabled=(plot_type == "Pie Chart"))
    color = st.sidebar.selectbox("Select Color (Optional)", [None] + list(df.columns))

    # Generate custom plot
    st.header(f"Custom {plot_type}")
    if plot_type == "Scatter Plot":
        fig = px.scatter(df, x=x_axis, y=y_axis, color=color if color else None, title=f"{y_axis} vs {x_axis}")
    elif plot_type == "Line Chart":
        fig = px.line(df, x=x_axis, y=y_axis, color=color if color else None, title=f"{y_axis} over {x_axis}")
    elif plot_type == "Bar Chart":
        fig = px.bar(df, x=x_axis, y=y_axis, color=color if color else None, title=f"{y_axis} by {x_axis}")
    elif plot_type == "Pie Chart":
        pie_values = st.sidebar.selectbox("Select Values for Pie", df.columns)
        fig = px.pie(df, names=x_axis, values=pie_values, title=f"Distribution of {pie_values}")
    elif plot_type == "Histogram":
        fig = px.histogram(df, x=x_axis, color=color if color else None, title=f"Histogram of {x_axis}", nbins=20)

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Please upload a CSV file to proceed.")
