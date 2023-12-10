import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import time

# ---------------- SETTINGS -------------------
page_title = 'Elektrisch Laadpalen'
page_icon = '⚡' # https://www.webfx.com/tools/emoji-cheat-sheet/
layout = 'centered'

st.set_page_config(
    page_title=page_title,
    page_icon=page_icon,
    layout=layout,
    initial_sidebar_state="expanded",
)

# ----------------- DATA ----------------------
from data.OpenChargeMapAPI import realTimeLaadPalenData as df_ocm
from data.OpenDataRDW import rdw_data as df_rdw
from data.laadpaaldata import laadpaal_data as df_lp

# ----------------- PAGES ---------------------
st.title(page_title + ' ' + page_icon)

st.write('''
### Introductie
In deze week's data-analyse dashboard onderzoeken we de wereld van elektrische laadpalen in Nederland. 
Op de eerste pagina zullen we data analyseren over het gebruik van de laadpalen, we vragen ons bijvoorbeeld af: hoelang wordt er gemiddeld geladen, wanneer is het het drukst bij de laadpalen?
Op de tweede pagina zullen we de locaties van de laadpalen in Nederland weergeven, en kijken waar er over de jaren heen laadpalen bij zijn gebouwd. 
Ten slotte duiken we op de derde pagina in de voertuigregistratie gegevens van de RDW om een beeld te krijgen van wat voor voertuigen gebruik maken van de laadpalen.
''')

# Create a dropdown to select which DataFrame to display
st.write('''
### Data
* Open Charge Map (OCM) API: https://openchargemap.org/site/develop/api#/
* RDW: https://opendata.rdw.nl/browse?category=Voertuigen&provenance=official
* 'Laadpaaldata.csv' met de laaddata van een aantal laadpalen
''')
selected_df = st.selectbox("Selecteer hieronder een optie om de gebruikte data in te zien:", [
                           "Laadpaaldata", "RDW", "Open Charge Map"])

# Display the selected DataFrame
if selected_df == "Laadpaaldata":
    st.write(df_lp.head())
    st.subheader("Interactive Scatter Plot")
    fig = px.scatter(df_lp, x="Started", y="TotalEnergy",
                     title="Charging Session Energy vs. Start Time")
    st.plotly_chart(fig)

if selected_df == "RDW":
    st.write(df_rdw.head())
    progress_text = "🏃 Loading..."
    my_bar = st.progress(0, text=progress_text)
    # Assuming you have date columns for both dates
    df_rdw['Datum tenaamstelling DT'] = pd.to_datetime(
        df_rdw['Datum tenaamstelling DT'])
    df_rdw['Datum eerste tenaamstelling in Nederland DT'] = pd.to_datetime(
        df_rdw['Datum eerste tenaamstelling in Nederland DT'])
    # Extract the month from both dates
    df_rdw['Month_Tenaamstelling'] = df_rdw['Datum tenaamstelling DT'].dt.month
    df_rdw['Month_EersteTenaamstelling'] = df_rdw['Datum eerste tenaamstelling in Nederland DT'].dt.month

    # Count the number of registrations for each month and date
    monthly_counts = df_rdw['Month_Tenaamstelling'].value_counts(
    ).reset_index()
    monthly_counts.columns = ['Month', 'Registrations_Tenaamstelling']

    monthly_counts_eerste_tenaamstelling = df_rdw['Month_EersteTenaamstelling'].value_counts(
    ).reset_index()
    monthly_counts_eerste_tenaamstelling.columns = [
        'Month', 'Registrations_EersteTenaamstelling']

    # Merge the two DataFrames on the 'Month' column
    merged_counts = monthly_counts.merge(
        monthly_counts_eerste_tenaamstelling, on='Month', how='outer').fillna(0)
    
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(1)
    my_bar.empty()

    st.write('''
                ## Registraties per maand
                ''')
    st.write('- Registrations_Tenaamstelling is de registratie aankomst algemeen van de autos')
    st.write('- Registrations_EersteTenaamstelling is de registratie aankomst algemeen van de autos in Nederland')
    # Create a grouped bar chart
    fig = px.bar(
        merged_counts,
        x='Month',
        y=['Registrations_Tenaamstelling', 'Registrations_EersteTenaamstelling'],
        title='Number of Registrations per Month',
        
    )

    st.plotly_chart(fig)

if selected_df == "Open Charge Map":
    st.write(df_ocm.head())
    # Plot 1: Scatter plot for 'DateCreated' vs
    # Convert 'DateCreated' column to datetime
    df_ocm['DateCreated'] = pd.to_datetime(df_ocm['DateCreated'])

    # Group the data by date and count the number of rows created on each date
    daily_counts = df_ocm.groupby(df_ocm['DateCreated'].dt.date)['DateCreated'].count()

    # Create a line chart
    st.subheader("Line Chart: Number of Rows Created Over Time for df_ocm")
    fig = px.line(x=daily_counts.index, y=daily_counts.values, labels={"x": "Date", "y": "Number of Rows Created"})
    st.plotly_chart(fig)

    # Plot 2: Bar chart for 'NumberOfPoints' vs 'OperatorInfo.Title'
    st.subheader("Bar Chart: NumberOfPoints vs OperatorInfo.Title")
    fig2 = px.bar(df_ocm, x="NumberOfPoints", y="OperatorInfo.Title")
    st.plotly_chart(fig2)

    # Plot 3: Histogram for 'Connection.PowerKW'
    st.subheader("Histogram: Connection.PowerKW")
    fig3 = px.histogram(df_ocm, x="Connection.PowerKW")
    st.plotly_chart(fig3)