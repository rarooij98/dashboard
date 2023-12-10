import pandas as pd
import streamlit as st


@st.cache_data  # Cache the data to speed up app performance
def load_data():
    data = pd.read_csv(
        'data/laadpaaldata.csv')
    filtered_data = dataclean(data)
    return filtered_data


def dataclean(data):
    # time over due
    data['Time over due'] = data['ConnectedTime'] - data['ChargeTime']
    # Convert total energy from watt to kilowatt
    data['TotalEnergy in kwh'] = data['TotalEnergy'] / 1000
    # Calculate the power per row in the dataset
    data['Power_kwh'] = data['TotalEnergy in kwh'] / data['ConnectedTime']
    # Convert 'Started' and 'Ended' columns to datetime format
    data['Started'] = pd.to_datetime(data['Started'], errors='coerce')
    data['Ended'] = pd.to_datetime(data['Ended'], errors='coerce')
    # Calculate the charging speed in kWh per hour
    data['Charging speed'] = (data['TotalEnergy in kwh'] / (((data['Ended'] - data['Started']).dt.total_seconds()) / 3600 ))
    # Calculate the efficiency of the charging session
    data['Efficiency'] = data['TotalEnergy in kwh'] / data['ChargeTime']
    # Define the price per kilowatt-hour (kWh) of electricity
    price_per_kwh = 0.50
    # Calculate the cost of each charging session
    data['Cost'] = data['TotalEnergy in kwh'] * price_per_kwh
    # Calculate the charge Time in minutes
    data['ChargeTime_min'] = data['ChargeTime'] * 60
    # Display
    return data


# Load the data
export = laadpaal_data = load_data()
