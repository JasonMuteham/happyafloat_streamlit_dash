import streamlit as st
import duckdb
import plotly.graph_objects as go

col1, col2, col3 = st.columns([2, 3, 1])
col2.markdown('''

# Happyafloat

Countdown to 10,000 nautical miles.
''')

@st.cache_resource(ttl=60*60)
def define_connection():
    #con = duckdb.connect("data/happyafloat.duckdb")
    con = duckdb.connect(f'''md:{st.secrets["md_db"]}?token={st.secrets["md_token"]}''',read_only=True)  # noqa: E501
    return con
con=define_connection()

@st.cache_data(ttl=60*60)
def get_data():
    return con.sql("SELECT sum(nautical_miles)::integer AS 'NM' FROM raw.log_data").fetchall()[0][0]

nm = get_data()

fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = nm,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "Nautical Miles"},
    gauge = {'bar': {'color': "blue"},
             'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 10000}
             }
             ))

st.plotly_chart(fig)