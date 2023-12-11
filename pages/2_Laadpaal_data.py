import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

# ---------------- SETTINGS -------------------
page_title = 'Laadpaal data'
page_icon = '🔌' #https://www.webfx.com/tools/emoji-cheat-sheet/
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
### Oplaad momenten
Dit is de verdeling van het gebruik van de laadpalen gedurende de dag. Om 7 uur 's ochtends is het het drukst is, met 1053 oplaadsessies. Om 1 uur 's nachts is het daarentegen het rustigst, met slechts 4 oplaadsessies. 
Er lijken pieken te zijn wanneer mensen 's morgens de deur uitgaan (06:00-08:00), tijdens de lunch (11:00) en aan het einde van de werkdag (16:00).
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

# Plot Charge time VS Connected time
st.write('''
### ConnectedTime vs ChargeTime
De meeste auto's zijn veel langer verbonden met de laadpaal dan dat ze daadwerkelijk opladen, gemiddeld wel 3 keer zo lang.
''')
# Calculate the mean connected time and mean charging time
filtered_df = df_lp[(df_lp['ChargeTime'] >= 0) & (df_lp['ConnectedTime'] >= 0)]
mean_connected_time = filtered_df['ConnectedTime'].mean()
mean_charge_time = filtered_df['ChargeTime'].mean()
mean_df = pd.DataFrame({'Type': ['Connected Time', 'Charge Time'],
                        'Mean Time': [mean_connected_time, mean_charge_time]})
# Create a grouped bar chart for mean values
fig = px.bar(mean_df, x='Type', y='Mean Time')
# Update layout
fig.update_xaxes(title='Type')
fig.update_yaxes(title='Time (hours)')
# Add title
fig.update_layout(title_text='Mean Connected Time vs Mean Charge Time')
# Show the figure
st.plotly_chart(fig)

st.write('''
### Verdeling oplaadtijd
De gemiddelde oplaadtijd is 106 minuten, de mediaan ligt iets hoger met 134 minuten.
''')
# Set a custom style (optional)
sns.set(style="whitegrid")

# Create a smaller figure with a specified size
fig_3, ax = plt.subplots(figsize=(8, 6))

# Plot the histogram using seaborn for improved aesthetics
sns.histplot(df_lp['ChargeTime_min'], bins=range(0, 520, 20), edgecolor='black', ax=ax, kde=False)

# Add labels and title
ax.set_xlabel('Charge Time (minutes)')
ax.set_ylabel('Frequency')
ax.set_title('Histogram of Charge Times')

# Add annotation for mean and median
mean = df_lp['ChargeTime_min'].mean()
median = df_lp['ChargeTime_min'].median()
ax.axvline(mean, color='red', linestyle='dashed', linewidth=1)
ax.axvline(median, color='green', linestyle='dashed', linewidth=1)
ax.annotate(f"Mean: {mean:.0f}", xy=(mean, 1400), xytext=(mean-120, 1300),
            arrowprops=dict(color='red', arrowstyle='->'))
ax.annotate(f"Median: {median:.0f}", xy=(median, 1400), xytext=(median+60, 1300),
            arrowprops=dict(color='green', arrowstyle='->'))

# Adjust the layout to prevent clipping of labels
plt.tight_layout()

# Show the plot
st.pyplot(fig_3)