import streamlit as st
import psycopg2
import pandas as pd

DB_URL = "postgresql://postgres.yalulvtrtuamcytshetg:Mohan16Sai98@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"

st.set_page_config(page_title="Flight Operations Intelligence", layout="wide")
st.title("✈️ Real-Time Flight Operations Intelligence")

@st.cache_data(ttl=300)
def load_data():
    conn = psycopg2.connect(DB_URL)
    df = pd.read_sql("SELECT * FROM flight_snapshots", conn)
    conn.close()
    return df

df = load_data()

latest = df[df['collected_at'] == df['collected_at'].max()]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Aircraft Tracked", df['icao24'].nunique())
col2.metric("Avg Speed (m/s)", round(latest['velocity_ms'].mean(), 1))
col3.metric("Avg Altitude (m)", round(latest['altitude_m'].mean(), 0))
col4.metric("Near Hyderabad", len(latest[
    (latest['latitude'].between(15.0, 20.0)) &
    (latest['longitude'].between(76.0, 82.0))
]))

st.subheader("Live Aircraft Map")
st.map(latest[['latitude', 'longitude']].dropna().rename(
    columns={'latitude': 'lat', 'longitude': 'lon'}),
    zoom=4)
st.subheader("Aircraft by Country")
country_df = latest.groupby('origin_country')['icao24'].count().reset_index()
country_df.columns = ['Country', 'Aircraft']
country_df = country_df.sort_values('Aircraft', ascending=False).head(15)
st.bar_chart(country_df.set_index('Country'))

st.subheader("Aircraft Activity Over Time")
hourly = df.groupby('collected_at')['icao24'].nunique().reset_index()
hourly.columns = ['Time', 'Aircraft Count']
st.line_chart(hourly.set_index('Time'))

st.subheader("Data Quality")
st.dataframe({
    'Total Records': [len(df)],
    'Total Snapshots': [df['collected_at'].nunique()],
    'Unique Aircraft': [df['icao24'].nunique()],
    'Missing Coords': [df['latitude'].isna().sum()],
    'Missing Callsign': [df['callsign'].isna().sum()],
    'Latest Snapshot': [df['collected_at'].max()]
})