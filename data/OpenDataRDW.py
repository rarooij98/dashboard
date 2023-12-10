import pandas as pd
import streamlit as st


@st.cache_data  # Cache the data to speed up app performance
def load_data():
    data = pd.read_csv("data/car_data.csv")
    filtered_data = dataclean(data)
    return filtered_data


def dataclean(data: pd.DataFrame) -> pd.DataFrame:
    # Filter out cars with 'Catalogusprijs' above 200,000
    data = data[data['Catalogusprijs'] <= 200000]
    return data


# Load the data
export = rdw_data = load_data()
