import pandas as pd
import numpy as np
import requests

import streamlit as st

# Request de data en sla de response op in een variabele 


@st.cache_data  # Cache the data to speed up app performance
def load_data():
    data = pd.read_csv("data/laadpalen.csv")
    filtered_data = dataclean(data)
    return filtered_data

def dataclean(data):

    # Convert to right datatypes
    objects = [
    'OperatorInfo.IsPrivateIndividual',
    'OperatorInfo.IsRestrictedEdit',
    'UsageType.IsPayAtLocation',
    'UsageType.IsMembershipRequired',
    'UsageType.IsAccessKeyRequired',
    'Connection.ConnectionType.IsDiscontinued',
    'Connection.ConnectionType.IsObsolete',
    'Connection.StatusType.IsOperational',
    'Connection.StatusType.IsUserSelectable',
    'Connection.Level.IsFastChargeCapable',
    ]
    for obj in objects:
        data[obj] = data[obj].astype('bool')

    return data


# Load the data
export = realTimeLaadPalenData = load_data()
