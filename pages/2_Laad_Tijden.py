import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st
import plotly.express as px
import statsmodels.formula.api as smf
from statsmodels.tools import add_constant

# ---------------- SETTINGS -------------------
page_title = 'Laadtijden rapportage'
page_icon = '💈' #https://www.webfx.com/tools/emoji-cheat-sheet/
layout = 'centered'

st.set_page_config(
    page_title=page_title,
    page_icon=page_icon,
    layout=layout,
    initial_sidebar_state="expanded",
)

# ----------------- DATA ----------------------
from data.laadpaaldata import laadpaal_data as df_lp

# ----------------- PAGES ---------------------
st.title(page_title + ' ' + page_icon)

st.write('''
         **Histogram**
In de histogram wordt de verdeling van de oplaadtijden in minuten weergegeven. Uit de grafiek blijkt dat de gemiddelde oplaadtijd 105 minuten bedraagt, terwijl de mediaan 134 minuten is.
''')

# Create a histogram of ChargeTime_min
fig_3, ax = plt.subplots()
ax.hist(df_lp['ChargeTime_min'], bins=range(0, 520, 20), edgecolor='black')
# Add labels and title
ax.set_xlabel('Charge Time (minutes)')
ax.set_ylabel('Frequency')
ax.set_title('Histogram of Charge Times')
# Add annotation for mean and median
mean = df_lp['ChargeTime_min'].mean()
median = df_lp['ChargeTime_min'].median()
ax.axvline(mean, color='red', linestyle='dashed', linewidth=1)
ax.axvline(median, color='green', linestyle='dashed', linewidth=1)
ax.annotate(f"Mean: {mean:.0f}", xy=(mean, 1400), xytext=(mean-120, 1300), arrowprops=dict(facecolor='red', arrowstyle='->'))
ax.annotate(f"Median: {median:.0f}", xy=(median, 1400), xytext=(median+60, 1300), arrowprops=dict(facecolor='green', arrowstyle='->'))
# Display the plot in Streamlit
st.pyplot(fig_3)


st.write('''
         **verdeling laadpalen**
In de grafiek en staafdiagram ziet u de verdeling van laadpalen gedurende de dag. Uit de grafiek is af te leiden dat het om 7 uur 's ochtends het drukst is, met 1053 oplaadsessies. Om 1 uur 's nachts is het daarentegen het rustigst, met slechts 4 oplaadsessies. Verder valt op te maken uit de staafdiagram dat de ochtenduren het drukst zijn, gevolgd door een afname gedurende de dag.
''')

# Converteer de 'Started' en 'Ended' kolommen naar datetime-objecten
df_lp['Started'] = pd.to_datetime(df_lp['Started'])
df_lp['Ended'] = pd.to_datetime(df_lp['Ended'])

# Bepaal de tijdsintervallen (bijv. per uur)
df_lp['Hour'] = df_lp['Started'].dt.hour

# Tel het aantal oplaadsessies per uur
hourly_counts = df_lp.groupby('Hour').size().reset_index(name='Count')

# Plotly Line Chart
fig = px.line(hourly_counts, x='Hour', y='Count', title='Charging station occupancy throughout the day')
fig.update_traces(mode='markers+lines', marker=dict(size=8, line=dict(width=2)))
fig.update_xaxes(title='Hour of the day')
fig.update_yaxes(title='Number of charging sessions')
st.plotly_chart(fig)

# Bepaal het tijdstip van de dag op basis van het starttijdstip
def get_time_of_day(hour):
    if 5 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour < 21:
        return 'Evening'
    else:
        return 'Night'

df_lp['TimeOfDay'] = df_lp['Started'].dt.hour.apply(get_time_of_day)

# Tel het aantal oplaadsessies per tijdstip van de dag
time_of_day_counts = df_lp['TimeOfDay'].value_counts().reset_index()
time_of_day_counts.columns = ['TimeOfDay', 'Count']

# Plotly Bar Chart
fig = px.bar(time_of_day_counts, x='TimeOfDay', y='Count', title='Charging station occupancy at various times of the day')
fig.update_xaxes(title='Time of day')
fig.update_yaxes(title='Number of charging sessions')
st.plotly_chart(fig)

st.write('''
    ## Scatter plot met Regression Line
    De kosten zijn berekend aan de hand van de prijs per kWh, die online is gevonden, vermenigvuldigd met het totale energieverbruik in kWh.
    De hoeveelheid energie in kWh is ook berekend door het totale energieverbruik in kWh te delen door de aangesloten tijd.
    Uit het onderstande spreidingsdiagram kunnen we zien dat de maximale kracht ongeveer 16,11 kWh is, wat ons een kostprijs oplevert van 19,66.
    Ook is het gemiddelde energieverbruik ongeveer 2,45, wat ons een kostprijs oplevert van ongeveer 4,69.
''')

# Perform linear regression
model = smf.ols(formula='Cost ~ Power_kwh', data=df_lp).fit()

# Add constant to the independent variable
X = add_constant(df_lp['Power_kwh'])

# Perform linear regression with a constant term
model = smf.ols(formula='Cost ~ Power_kwh', data=pd.concat([df_lp['Cost'], X], axis=1)).fit()

# Create scatter plot
fig_7, ax = plt.subplots()
sns.scatterplot(x=df_lp['Power_kwh'], y=df_lp['Cost'], ax=ax)

# Generate regression line
x_values = np.linspace(df_lp['Power_kwh'].min(), df_lp['Power_kwh'].max(), 100)
y_values = model.predict(pd.DataFrame({'Power_kwh': x_values}))
ax.plot(x_values, y_values, color='red', label='Regression Line')
ax.legend()

# Display the plot
st.pyplot(fig_7)