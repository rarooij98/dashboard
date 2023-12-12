import numpy as np
import pandas as pd
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# ---------------- SETTINGS -------------------
page_title = 'Laadpalen in Nederland'
page_icon = '🌎' #https://www.webfx.com/tools/emoji-cheat-sheet/
layout = 'centered'

st.set_page_config(
    page_title=page_title,
    page_icon=page_icon,
    layout=layout,
    initial_sidebar_state="expanded",
)

# ----------------- DATA ----------------------
from data.OpenChargeMapAPI import realTimeLaadPalenData as df_laadpaal
from data.provincies import gdf_provincies

# ----------------- PAGES ---------------------
st.title(page_title + ' ' + page_icon)

st.write('''
Op deze kaart wordt de verdeling van laadpalen over Nederland in een bepaald jaar weergeven. Verander het jaar met de slider en zie hoe de verdeling verandert.
''')

# Maak een DataFrame met het aantal laadpalen per provincie in het geselecteerde jaar
def create_cumcount(data, geodata):
    # Print unique locations in this dataframe
    data['Unique_Location'] = data[['AddressInfo.Latitude', 'AddressInfo.Longitude']].astype(str).agg('-'.join, axis=1)
    unique_locations = data['Unique_Location'].nunique()
    st.write(f"Number of unique locations: {unique_locations}")

    # Maak een dataframe cumcount_df met de count voor elk jaar per provincie
    cumcount_df = data.groupby(['Year', 'Provincie']).agg({'Unique_Location': 'nunique'}).reset_index()
    cumcount_df = cumcount_df.sort_values(by=['Year', 'Provincie'], ascending=True)

    # Bereken de cumulatieve count binnen elke provincie
    cumcount_df['cum_count'] = cumcount_df.groupby('Provincie')['Unique_Location'].cumsum()

    # Bereken de laadpalen per km2 (obv de cum_count)
    area_dict = geodata.set_index('PROVINCIENAAM')['SHAPE.AREA'].to_dict()
    cumcount_df['area'] = cumcount_df['Provincie'].map(area_dict)
    cumcount_df['area'] = cumcount_df['area'] / 10**9
    cumcount_df['per_km2'] = cumcount_df['cum_count'] / cumcount_df['area']
    
    return cumcount_df
# def create_cumcount(data, geodata):
#     # Print unique locations in this dataframe
#     data['Unique_Location'] = data[['AddressInfo.Latitude', 'AddressInfo.Longitude']].astype(str).agg('-'.join, axis=1)
#     unique_locations = data['Unique_Location'].nunique()
#     st.write(f"Number of unique locations: {unique_locations}")

#     # Maak een dataframe combi met alle combinaties van jaar en provincie
#     all_combinations = pd.MultiIndex.from_product([data['Year'].unique(), data['Provincie'].unique()], names=['Year', 'Provincie'])
#     combi = pd.DataFrame(index=all_combinations).reset_index()
#     # Maak een dataframe cumcount_df met de count voor elk jaar per provincie
#     cumcount_df = combi.merge(data.groupby(['Year', 'Provincie']).size().reset_index(name='count'), on=['Year', 'Provincie'], how='left')
#     cumcount_df = cumcount_df.sort_values(by=['Year', 'Provincie'], ascending=True)
#     # Bereken de cumulatieve count
#     cumcount_df['cum_count'] = cumcount_df['count'].cumsum()
#     cumcount_df['cum_count'] = np.where(cumcount_df['cum_count'].isna(), 0, cumcount_df['cum_count'])
#     for index, row in cumcount_df.iterrows():
#         if row['cum_count'] == 0 and row['Year'] > 2011:
#             selection = cumcount_df.loc[(cumcount_df['Provincie']==row['Provincie']) & (cumcount_df['Year']==row['Year']-1)]
#             cumcount_df.at[index,'cum_count'] = selection['cum_count']
#     st.write(cumcount_df)
#     # Bereken de laadpalen per km2 (obv de cum_count)
#     area_dict = geodata.set_index('PROVINCIENAAM')['SHAPE.AREA'].to_dict()
#     cumcount_df['area'] = cumcount_df['Provincie'].map(area_dict)
#     cumcount_df['area'] = cumcount_df['area'] / 10**9
#     cumcount_df['per_km2'] = cumcount_df['cum_count'] / cumcount_df['area']
    
#     return cumcount_df
cumcount_df = create_cumcount(df_laadpaal, gdf_provincies)

# Neem de geselecteerde waardes en filter hiermee de data op jaar en provincie
# User input for selecting regions
def get_selected_prov(data):
    selected_options = st.multiselect(
        "Selecteer Provincie",
        options=data['Provincie'].unique().tolist(),
        key="prov_multiselect"
    )
    return selected_options
selected_prov = get_selected_prov(df_laadpaal)

# Als er geen zijn geselecteerd:
if len(selected_prov) < 1:
    selected_prov = df_laadpaal['Provincie'].unique().tolist()
    
# Slider voor jaren
def get_selected_year():
    selected_year = st.slider('Selecteer een jaar', min_value=2012, step=1, max_value=2023, value=2016)
    return selected_year
selected_year = get_selected_year()

# User input voor het type verdeling
def get_selected_data():
    selected_options = st.selectbox(
    'Welke data wil je weergeven?',
    ('Aantal laadpalen', 'Cumulatief aantal laadpalen', 'Laadpalen per km2'))
    return selected_options

selected_data = get_selected_data()

data_column = 'count'
if selected_data == 'Aantal laadpalen':
    data_column = 'count'
elif selected_data == 'Cumulatief aantal laadpalen':
    data_column = 'cum_count'
elif selected_data == 'Laadpalen per km2':
    data_column = 'per_km2'

st.write('''
Selecteer 'Cumulatief aantal laadpalen' om te zien hoeveel laadpalen er op dat moment in de provincie aanwezig zijn. Met 'Aantal laadpalen' is alleen zichtbaar hoeveel er in dat jaar geregistreerd waren.
Of selecteer 'Laadpalen per km2' om de dichtheid van laadpalen per provincie te vergelijken.
''')

# Filter de data op jaar en provincie
prov_selection = gdf_provincies[gdf_provincies['PROVINCIENAAM'].isin(selected_prov)]
cumcount_selection = cumcount_df[cumcount_df['Year'].astype(int) == selected_year]

# Bereken de startlocatie en zoom voor de Map op basis van de geselecteerde provincie
location = [52.1326, 5.2913]
zoom = 7
# Zoom uit als meer dan 1 prov is geselecteerd
# if len(selected_prov) > 1:
#     location = [52.1326, 5.2913]
#     zoom = 7
# Zoom in als er maar 1 prov is geselecteerd
# elif len(selected_prov) == 1:
    # centroid = prov_selection.geometry.centroid
    # lat = centroid.map(lambda p: p.x)
    # lng = centroid.map(lambda p: p.y)
    # location = [lng, lat]
    # st.write(prov_selection.geometry)
    # st.write(centroid)
    # st.write(location)
    # zoom = 9

# Maak een choropleth Map van de Laadpalen data
def create_choropleth(Laadpalen):
    m = folium.Map(location=location, zoom_start=zoom, tiles='CartoDB positron')
    
    # Voeg de markers toe
    prov_markers = None;
    if len(selected_prov) < 12:
        prov_markers = MarkerCluster().add_to(m)
    
    # Definieer de markers voor het Marker Cluster
    #Laadpalen_markers = Laadpalen[(Laadpalen['Year'].astype(int) == selected_year) & (Laadpalen['Provincie'].isin(selected_prov))]
    #^ conditional statement - count or cumcount selected?
    Laadpalen_markers = Laadpalen[
        (Laadpalen['Year'].astype(int) <= selected_year) &  # Include all years before and including the selected year
        (Laadpalen['Provincie'].isin(selected_prov))
    ]
    
    Laadpalen_markers['Unique_Location'] = Laadpalen_markers[['AddressInfo.Latitude', 'AddressInfo.Longitude']].astype(str).agg('-'.join, axis=1)
    unique_locations = Laadpalen_markers['Unique_Location'].nunique()
    st.write(f"Number of unique locations: {unique_locations}")

    
    def marker_colors(status):
        if status == True:
            return {'color': 'green', 'icon': 'bolt', 'prefix': 'fa'}
        elif status == False:
            return {'color': 'red', 'icon': 'bolt', 'prefix': 'fa'}
    
    # Voor elke locatie, maak een marker en voeg deze toe aan het cluster
    if prov_markers:
        for index, row in Laadpalen_markers.iterrows():
            status = row['StatusType.IsOperational'] if 'StatusType.IsOperational' in row else False
            folium.Marker(
                [row['AddressInfo.Latitude'],
                 row['AddressInfo.Longitude']],
                popup=row['Connection.Level.Title'],
                icon=folium.map.Icon(
                    color=marker_colors(status)['color'],
                    icon_color='white',
                    icon=marker_colors(status)['icon'],
                    prefix=marker_colors(status)['prefix'],
                )
            ).add_to(prov_markers)
    
    # # Voeg de markers toe
    # if len(selected_prov) < 12:
    #     prov_markers = MarkerCluster().add_to(m)
    
    # # Definieer de markers voor het Marker Cluser
    # Laadpalen_markers = Laadpalen[(Laadpalen['Year'].astype(int) == selected_year) & (Laadpalen['Provincie'].isin(selected_prov))]
    
    # def marker_colors(status):
    #     if status == True :
    #         return {'color':'green', 'icon':'bolt', 'prefix':'fa'}
    #     elif status == False :
    #         return {'color':'red', 'icon':'bolt', 'prefix':'fa'}
    #     # Voor elke locatie, maak een marker en voeg deze toe aan het cluster
    # if prov_markers:
    #     for index, row in Laadpalen_markers.iterrows():
    #         if row['StatusType.IsOperational']:
    #             status = row['StatusType.IsOperational']
    #         else: 
    #             status = False
    #         folium.Marker(
    #             [row['AddressInfo.Latitude'], 
    #             row['AddressInfo.Longitude']],
    #             popup=row['Connection.Level.Title'],
    #             icon=folium.map.Icon(
    #                 color=marker_colors(status)['color'],
    #                 icon_color='white',
    #                 icon=marker_colors(status)['icon'],
    #                 prefix=marker_colors(status)['prefix'],
    #             )
    #         ).add_to(prov_markers)
        
    folium.Choropleth(
        geo_data=prov_selection,
        name='geometry',
        data=cumcount_selection,
        columns=['Provincie', data_column],
        key_on='feature.properties.PROVINCIENAAM',
        fill_color='PuBu',
        fill_opacity=0.5,
        legend_name=f'{selected_data} per Nederlandse provincie',
    ).add_to(m)
    
    st.map = st_folium(m, width=700, height=600)

create_choropleth(df_laadpaal)