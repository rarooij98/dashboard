import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.impute import SimpleImputer


# ---------------- SETTINGS -------------------
page_title = 'Elektrische voertuigen'
page_icon = '🚘' #https://www.webfx.com/tools/emoji-cheat-sheet/
layout = 'centered'

st.set_page_config(
    page_title=page_title,
    page_icon=page_icon,
    layout=layout,
    initial_sidebar_state="expanded",
)

# ----------------- DATA ----------------------
from data.laadpaaldata import laadpaal_data as df_lp
from data.OpenDataRDW import rdw_data as df_rdw

# ----------------- PAGES ---------------------
st.title(page_title + ' ' + page_icon)

# car brands
frequentie_automerken = df_rdw['Merk'].value_counts()

# Histogram van meest voorkomende automerken
st.write("### Meest voorkomende automerken")
st.write("Deze histogram laat de verdeling zien van de meest voorkomende automerken voor elektrische auto's.")
# Create a slider of the ammount of cars per brand
car_brand_slider = st.slider("Selecteer het aantal automerken:", 0, frequentie_automerken.__len__(), 5)

# Create a Histrogram types of cars from handelsbenaming at a Merk
top_automerken = frequentie_automerken.head(car_brand_slider)
fig = px.histogram(df_rdw, x=top_automerken.index, y=top_automerken.values, labels={'x': 'Automerk', 'y': 'Aantal'})
fig.update_layout(xaxis_title="Automerk", yaxis_title="Aantal")
st.plotly_chart(fig)

# Histogram van meest voorkomende modellen
st.write("### Meest voorkomende auto modellen")
# Choose a car brand
car_brand = st.selectbox("Selecteer een automerk", top_automerken.index)
df_rdw_filtered = df_rdw[df_rdw['Merk'] == car_brand]
st.write(f"Deze histogram laat de meest voorkomende elektrische auto's zien van het automerk '{car_brand}'.")
fig = px.histogram(df_rdw_filtered, x=df_rdw_filtered['Handelsbenaming'], labels={'x': 'Handelsbenaming'})
fig.update_layout(xaxis_title="Handelsbenaming", yaxis_title="Aantal")
st.plotly_chart(fig)

# Histogram van meest voorkomende kleuren
st.write("### Meest voorkomende auto kleuren")
st.write(f"Deze histogram laat de meest voorkomende kleuren zien van elektrische auto's van het automerk '{car_brand}'.")
fig = px.histogram(df_rdw_filtered, x=df_rdw_filtered['Eerste kleur'], labels={'x': 'Eerste kleur'})
fig.update_layout(xaxis_title="Eerste kleur", yaxis_title="Aantal")
st.plotly_chart(fig)

# Histogram van meest voorkomende kleuren
st.write("### Catalogusprijs")
st.write("Dit zijn de gemiddelde catalogusprijzen voor de meest geregistreerde elektrische automerken.")

# Calculate the average Catalogusprijs for the top car brands
average_prices = df_rdw.groupby('Merk')['Catalogusprijs'].mean().reset_index()
# Filter the data for the selected top car brands
selected_brands = top_automerken.index
filtered_data = df_rdw[df_rdw['Merk'].isin(selected_brands)]
# Calculate the average Catalogusprijs for the selected top car brands
average_selected_prices = filtered_data.groupby('Merk')['Catalogusprijs'].mean().reset_index()
# Calculate and add the average total price (Gemiddelde)
average_total_price = df_rdw['Catalogusprijs'].mean()
gemiddelde_row = pd.DataFrame({'Merk': ['Gemiddelde'], 'Catalogusprijs': [average_total_price]})
average_selected_prices = pd.concat([average_selected_prices, gemiddelde_row])
# Sort the data so that 'Gemiddelde' is at the bottom
average_selected_prices = average_selected_prices.sort_values(by='Catalogusprijs', ascending=False)

# Create a bar plot for the selected top car brands and the average total
# Gemiddelde Catalogusprijs voor meest voorkomende automerken
fig = px.bar(average_selected_prices, x='Merk', y='Catalogusprijs', 
             labels={'x': 'Automerk', 'y': 'Gemiddelde Catalogusprijs'},
             color_discrete_sequence=['blue', 'red'])  # 'Gemiddelde' bar color is set to red
fig.update_layout(xaxis_title="Automerk", yaxis_title="Gemiddelde Catalogusprijs")
st.plotly_chart(fig)

st.write("### Catalogusprijs voorspelling")

# Selecteer de kenmerken (voorspellers) en de doelvariabele
X = df_rdw[['Aantal zitplaatsen', 'Lengte', 'Breedte', 'Vermogen massarijklaar']]
y = df_rdw['Catalogusprijs']
# Handle missing values by imputing with mean
imputer = SimpleImputer(strategy='mean')
X = imputer.fit_transform(X)
# Splits de gegevens in trainings- en testsets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# Normalize the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
# Create a Ridge regression model
ridge_model = Ridge(alpha=1.0)  # You can adjust the alpha (regularization strength)
# Fit the model
ridge_model.fit(X_train, y_train)
# Make predictions
y_pred = ridge_model.predict(X_test)
# Calculate residuals
residuals = y_test - y_pred
# Create a DataFrame to include residuals
results_df = pd.DataFrame({'Werkelijke Catalogusprijs': y_test, 'Voorspelde Catalogusprijs': y_pred, 'Residuen': residuals})

# Create a DataFrame with actual and predicted values
brand_predictions_df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
st.write(brand_predictions_df.columns)
# Add a 'Automerk' column to the DataFrame based on your original DataFrame 'df_rdw'
brand_predictions_df['Automerk'] = df_rdw.loc[y_test.index, 'Automerk'].values
# Group by Automerk and calculate the mean of actual and predicted values
brand_means = brand_predictions_df.groupby('Automerk').mean()
# Sort the DataFrame by the predicted values
brand_means = brand_means.sort_values(by='Predicted')

# Create a bar plot
plt.figure(figsize=(12, 6))
sns.barplot(x=brand_means.index, y='Predicted', data=brand_means, color='blue')
plt.xticks(rotation=45, ha='right')
plt.title('Predicted Catalog Prices per Car Brand')
plt.xlabel('Car Brand')
plt.ylabel('Predicted Catalog Price')
plt.show()

# Scatter plot van werkelijke vs. voorspelde Catalogusprijs
st.write("Voorspelde Catalogusprijs met Residuen")
st.write("Met een lineare regressie model hebben we geprobeerd om de catalogusprijs te voorspellen. Deze scatterplot laat de vergelijking zien tussen de werkelijke en voorspelde catalogusprijs.")
# Create a scatter plot of actual vs. predicted values with a color scale based on residuals
fig = px.scatter(results_df, x='Werkelijke Catalogusprijs', y='Voorspelde Catalogusprijs', color='Residuen',
                 labels={'x': 'Werkelijke Catalogusprijs', 'y': 'Voorspelde Catalogusprijs'},
                 title='Werkelijke vs. Voorspelde Catalogusprijs met Residuen',
                 color_continuous_scale='RdBu', range_color=[-200000, 200000])

# Customize the colorbar title
fig.update_coloraxes(colorbar_title='Residuen')
st.plotly_chart(fig)
