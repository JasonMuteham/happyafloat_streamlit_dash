import streamlit as st
import duckdb
import pandas as pd
import numpy as np
import plotly.graph_objects as go

local = True

st.markdown('''

# happyafloat.com

Family Adventures at Sea.
''')
st.divider()
col1, col2 = st.columns(2)

@st.cache_resource(ttl=60*60)
def define_connection(local):
    if local:
        con = duckdb.connect("data/happyafloat.duckdb", read_only=True)
    else:
        con = duckdb.connect(f'''md:{st.secrets["md_db"]}?token={st.secrets["md_token"]}''',read_only=True)  # noqa: E501
    return con
con=define_connection(local)

@st.cache_data(ttl=60*60)
def get_nm():
    return con.sql("SELECT sum(nautical_miles)::integer AS 'NM' FROM raw.log_data").fetchall()[0][0]
nm = get_nm()

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

def get_motoring_sailing_hrs():
    return con.sql("""
                    SELECT
                        YEAR(log_date)::varchar AS "year", 
                        SUM(motoring_minutes + (motoring_hours * 60 )) + SUM(sailing_minutes + (sailing_hours * 60 )) AS "Total Minutes",
                        SUM(motoring_minutes + (motoring_hours * 60 )) AS "motoring", 
                        SUM(sailing_minutes + (sailing_hours * 60 )) AS "sailing",
                        ((motoring / "Total Minutes")*100)::Decimal(4,1) AS "Motoring %",
                        ((sailing / "Total Minutes")*100)::decimal(4,1) AS "Sailing %"
                    FROM raw.log_data
                    GROUP BY year 
                                    
                   """).df()

motor_sail_hrs = get_motoring_sailing_hrs()
motor_sail_hrs                   

col1.line_chart(motor_sail_hrs,x="year",y=["Total Minutes","motoring","sailing"],
                color = [[10,100,10],[.5,.5,.8], '#0000FF'])
col2.bar_chart(motor_sail_hrs,
               x="year",
               y=["Motoring %","Sailing %"],
               color = [[.5,.5,.8], '#0000FF']
               )
