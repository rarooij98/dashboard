import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import time

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

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
In dit data dashboard analyseren we elektrische laadpalen in Nederland. 
Op de eerste pagina zullen we data onderzoeken over het gebruik van de laadpalen, we vragen ons bijvoorbeeld af: hoelang wordt er gemiddeld geladen, wanneer is het het drukst bij de laadpalen?
Op de tweede pagina zullen we de locaties van de laadpalen in Nederland weergeven, en kijken waar er over de jaren heen laadpalen bij zijn gebouwd. 
Ten slotte duiken we op de derde pagina in de voertuigregistratie gegevens van de RDW om een beeld te krijgen van wat voor voertuigen gebruik maken van de laadpalen.
''')

# Create a dropdown to select which DataFrame to display
st.write('''
### 📈 Data
* Open Charge Map (OCM) API: https://openchargemap.org/site/develop/api#/
* RDW: https://opendata.rdw.nl/browse?category=Voertuigen&provenance=official
* 'Laadpaaldata.csv' met de laaddata van een aantal laadpalen
''')
selected_df = st.selectbox("Selecteer hieronder een optie om de gebruikte data in te zien:", [
                           "Open Charge Map", "Laadpaaldata", "RDW"])

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
                ## 🚘 Registraties per maand
                ''')
    # Create a grouped bar chart
    fig = px.bar(
        merged_counts,
        x='Month',
        y=['Registrations_Tenaamstelling', 'Registrations_EersteTenaamstelling'],
        title='Aantal voertuigregistraties per maand',
        
    )

    st.plotly_chart(fig)

if selected_df == "Open Charge Map":
    st.write(df_ocm[['ID','OperatorID','UsageTypeID','UsageCost','Connections','NumberOfPoints','DateCreated','OperatorInfo.Title',
    'UsageType.IsPayAtLocation','UsageType.IsMembershipRequired','UsageType.IsAccessKeyRequired','UsageType.ID',
    'UsageType.Title','StatusType.IsOperational','AddressInfo.AddressLine1','AddressInfo.Town','AddressInfo.StateOrProvince']].head())
    
    st.subheader("🔎 Data Exploratie")
    fig = make_subplots(
        rows=5, cols=3,
        horizontal_spacing=0.05, vertical_spacing=0.075,  
        specs=[ 
            [{"rowspan": 2}, {"rowspan": 2}, {"rowspan": 2}],
            [None, None, None],
            [{"colspan": 3, "rowspan": 3}, None, None],
            [None, None, None],
            [None, None, None]
        ],
        subplot_titles=("% Operationele laadpalen", "% Laadpalen met fast charging", " % Laadpalen met membership", "Aantal laadpalen per stad")
    )
    # Hoeveel procent van de locaties zijn operationeel?
    fig.add_trace(go.Histogram(x=df_ocm['StatusType.IsOperational'], histnorm='percent', marker_color=['#00CC96', '#EF553B']), row=1, col=1)
    # Hoeveel procent van de locaties heeft fast charging?
    fig.add_trace(go.Histogram(x=df_ocm['Connection.Level.IsFastChargeCapable'], histnorm='percent', marker_color=['#EF553B', '#00CC96']), row=1, col=2)
    # Bij hoeveel percentage van de locaties heb je een membership nodig?
    fig.add_trace(go.Histogram(x=df_ocm['UsageType.IsMembershipRequired'], histnorm='percent', marker_color=['#00CC96', '#EF553B']), row=1, col=3)
    # Hoeveel locaties zijn er per stad? (geeft top 25)
    fig.add_trace(go.Histogram(y=df_ocm[df_ocm['AddressInfo.Town'].value_counts().sort_values(ascending=False).head(25)], marker_color='#636EFA'), row=3, col=1)
    fig.update_layout(height=800, width=800, title_text="Elektrische laadpalen in Nederland", showlegend=False)
    fig.update_annotations(font_size=12) # subplot titels
    st.plotly_chart(fig)

    # Histogram for 'Connection.PowerKW'
    st.subheader("⚡ Verdeling PowerKW")
    fig2 = px.histogram(df_ocm, x="Connection.PowerKW")
    st.plotly_chart(fig2)
    
    # Linechart for registration over time
    st.subheader("📅 Laadpaal registraties 2010-2023")
    # Convert 'DateCreated' column to datetime
    df_ocm['DateCreated'] = pd.to_datetime(df_ocm['DateCreated'])
    # Group the data by date and count the number of rows created on each date
    daily_counts = df_ocm.groupby(df_ocm['DateCreated'].dt.date)['DateCreated'].count()
    # Create a line chart
    fig3 = px.line(x=daily_counts.index, y=daily_counts.values, labels={"x": "Date", "y": "Number of Rows Created"})
    st.plotly_chart(fig3)