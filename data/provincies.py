import pandas as pd
import streamlit as st
import geopandas as gpd

# Maak een GeoDataFrame met provincie grenzen
# Bron: https://www.nationaalgeoregister.nl/geonetwork/srv/dut/catalog.search#/metadata/e73b01f6-28c7-4bb7-a782-e877e8113e2c

@st.cache_data  # Cache the data to speed up app performance
def load_data():
    provincies = gpd.read_file('data/provincies.json')
    filtered_data = dataclean(provincies)
    return filtered_data


def dataclean(provincies):
    provincies['PROVINCIENAAM'] = provincies['PROVINCIENAAM'].str.replace('Fryslân', 'Friesland')
    geo_df_crs = {'init' : 'epsg:4326'}
    gdf_provincies = gpd.GeoDataFrame(provincies)
    gdf_provincies = gdf_provincies.to_crs(geo_df_crs)
    return provincies


# Load the data
export = gdf_provincies = load_data()
