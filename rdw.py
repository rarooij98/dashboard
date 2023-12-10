import pandas as pd
import streamlit as st
from database import DataHandler
import pandas as pd
import plotly.express as px

# Load your dataset
@st.cache_data
def load_data():
    return pd.read_csv('e-carsdata.csv')  # Replace with your dataset path

data = load_data()

# Create the Streamlit app
st.title("Your Dataset Dashboard")

# Display the dataset
st.write("## Dataset Preview")
st.write(data)

# Add filters for specific columns
st.sidebar.title("Data Filters")
selected_columns = st.sidebar.multiselect("Select columns to display", data.columns)

# Filter the dataset based on selected columns
if selected_columns:
    filtered_data = data[selected_columns]
    st.write("### Filtered Data")
    st.write(filtered_data)

# Create visualizations for selected columns (example: histogram)
st.sidebar.title("Data Visualizations")
column_to_plot = st.sidebar.selectbox("Select a column for visualization", data.columns)
if column_to_plot:
    st.write(f"### {column_to_plot} Histogram")
    fig = px.histogram(data, x=column_to_plot, title=f"{column_to_plot} Distribution")
    st.plotly_chart(fig)

# Add summary statistics for selected columns
st.sidebar.title("Summary Statistics")
column_to_summarize = st.sidebar.selectbox("Select a column for summary statistics", data.columns)
if column_to_summarize:
    st.write(f"### Summary Statistics for {column_to_summarize}")
    st.write(data[column_to_summarize].describe())

# Grafiek van de meest voorkomende automerken
st.write("## Meest Voorkomende Automerken")

# Bepaal de frequentie van elk automerk in de dataset
frequentie_automerken = data['Merk'].value_counts()

# Top 10 meest voorkomende automerken
top_10_automerken = frequentie_automerken.head(10)

# Maak een staafdiagram van de top 10 meest voorkomende automerken
fig = px.bar(top_10_automerken, x=top_10_automerken.index, y=top_10_automerken.values, labels={'x': 'Automerk', 'y': 'Aantal'})
fig.update_layout(xaxis_title="Automerk", yaxis_title="Aantal")
st.plotly_chart(fig)

# Streamlit-app maken
st.title("Aggregatie per Week en Lijngrafiek")

# Voeg een kolom toe voor de week van het jaar
data['Datum tenaamstelling'] = pd.to_datetime(data['Datum tenaamstelling'])
data['Week van het jaar'] = data['Datum tenaamstelling'].dt.strftime('%Y-%U')

# Voeg een filter voor automerken toe
merk_filter = st.selectbox("Selecteer een automerk", data['Merk'].unique())

# Filter de dataset op basis van het geselecteerde automerk
filtered_data = data[data['Merk'] == merk_filter]

# Aggregatie per week
aggregated_data = filtered_data.groupby('Week van het jaar').size().reset_index(name='Aantal')

# Lijngrafiek
fig = px.line(aggregated_data, x='Week van het jaar', y='Aantal', title=f'Aantal voertuigen van {merk_filter} per week')
fig.update_xaxes(title_text='Week van het jaar')
fig.update_yaxes(title_text='Aantal voertuigen')
st.plotly_chart(fig)