import streamlit as st
import duckdb
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

local = False

st.markdown('''

# happyafloat.com

Family Adventures at Sea.
''')
st.divider()
col1, col2, col3 = st.columns(3)

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
    title = {'text': "10K Nautical Miles"},
    gauge = {'bar': {'color': "blue"},
             'threshold' : {'line': {'color': "red", 'width': 4}, 
                                    'thickness': 0.75, 
                                    'value': 10000}
             }
             ))

col1.plotly_chart(fig, use_container_width=True)

@st.cache_data(ttl=60*60)
def get_motoring_sailing_hrs():
    return con.sql("""
                   SELECT Year, "Total Minutes", "motoring", "sailing", "Motoring %", "Sailing %", "Nautical Miles",
                   SUM("Nautical Miles") OVER (ORDER BY Year) as "Cumulative Miles" 
                   FROM (
                    SELECT
                        YEAR(log_date)::varchar AS "Year", 
                        SUM(motoring_minutes + (motoring_hours * 60 )) + SUM(sailing_minutes + (sailing_hours * 60 )) AS "Total Minutes",
                        SUM(motoring_minutes + (motoring_hours * 60 )) AS "motoring", 
                        SUM(sailing_minutes + (sailing_hours * 60 )) AS "sailing",
                        ((motoring / "Total Minutes")*100)::Decimal(4,1) AS "Motoring %",
                        ((sailing / "Total Minutes")*100)::decimal(4,1) AS "Sailing %",
                        SUM(nautical_miles)::integer AS "Nautical Miles"
                    FROM raw.log_data
                    GROUP BY Year 
                    ORDER BY Year)
                                    
                   """).df()  # noqa: E501

motor_sail_hrs = get_motoring_sailing_hrs()

motor_sail_hrs       


fig = px.bar(motor_sail_hrs, x="Year", y=["Motoring %","Sailing %"],
             barmode='group',title = "Motoring vs Sailing"
             )
fig.update_layout(yaxis_title='Percent', xaxis_title='', showlegend=True, )
fig.update_coloraxes(colorbar_ticklabelposition='inside',colorbar_ticks='inside',showscale=False)
fig.update_traces(hovertemplate='%{y}%',marker_line_color='darkblue', marker_line_width=1.0)
col2.plotly_chart(fig, use_container_width=True)

fig = px.line(motor_sail_hrs, x="Year", y=["motoring","sailing"])
col3.plotly_chart(fig, use_container_width=True)