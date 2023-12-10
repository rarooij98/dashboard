# 🔌 Laadpaal data
This app shows the data about the electric charging stations in the Netherlands.

## 📦 Packages

- Python 3.11
- Streamlit 1.27.0
- Pandas 2.1.1
- Numpy 1.26.0
- Matplotlib 3.8.0
- Seaborn 0.12.2
- Plotly 5.17.0
- Geopandas 0.14
- Folium 0.14.0
- Streamlit_folium 0.15.0
- Statsmodels 0.14.0

## 🚀 Getting Started

### Installation

1. Clone the repository to your local machine: 
```bash
git clone https://github.com/rarooij98/dashboard.git
```
2. Navigate to the project directory.
3. Create a virtual environment (recommended):
```bash
python -m venv venv
```
4. Activate the virtual environment (recommended):
- On Windows:
```bash
venv\Scripts\activate
```
- On macOS and Linux:
```bash
source venv/bin/activate
```
5. Install all project dependencies from requirements.txt:
```bash
pip install -r requirements.txt
```
6. Start the app by running this script:
```bash
streamlit run app.py
```

## 📈 Data
* Open Charge Map (OCM) API: https://openchargemap.org/site/develop/api#/
* RDW: https://opendata.rdw.nl/browse?category=Voertuigen&provenance=official
* CSV 'Laadpaaldata' with data from some electric charging stations

### Dataset Column Information

Here is a breakdown of the columns in the 'Laadpaaldata' dataset:

1. **Started:** 
   - Description: The date and time when the event started.
   - Format: YYYY-MM-DD HH:MM:SS

2. **Ended:** 
   - Description: The date and time when the event ended.
   - Format: YYYY-MM-DD HH:MM:SS

3. **TotalEnergy:** 
   - Description: The total energy consumption during the event (in some units).
   - Example: 1830

4. **ConnectedTime:** 
   - Description: The duration of the event while the device was connected (in hours).
   - Example: 0.5219

5. **ChargeTime:** 
   - Description: The duration of the event while the device was charging (in hours).
   - Example: 0.5219

6. **MaxPower:** 
   - Description: The maximum power consumption during the event (in watts).
   - Example: 3524

### Column Explanations

- **Started** and **Ended** columns provide the timestamp for when each event started and ended, allowing you to track the duration of each event.

- **TotalEnergy** indicates the total energy consumed during the event, providing insight into energy usage.

- **ConnectedTime** represents the time the device was actively connected during the event, which may be useful for analyzing usage patterns.

- **ChargeTime** specifies the time the device spent charging, which can be important for understanding how much time the device spent replenishing its power.

- **MaxPower** reveals the maximum power consumption observed during the event, which can be valuable for assessing peak power demands.


