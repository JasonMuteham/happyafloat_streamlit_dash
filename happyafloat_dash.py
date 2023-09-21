import streamlit as st
import duckdb
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

@st.cache_resource(ttl=60*60)
def define_connection(local):
    if local:
        con = duckdb.connect("data/happyafloat.duckdb", read_only=True)
    else:
        con = duckdb.connect(f'''md:{st.secrets["md_db"]}?token={st.secrets["md_token"]}''',read_only=True)  # noqa: E501
    return con

@st.cache_data(ttl=60*60)
def get_nm():
    return con.sql("SELECT sum(nautical_miles)::integer AS 'NM' FROM raw.log_data").fetchall()[0][0]

@st.cache_data(ttl=60*60)
def get_motoring_sailing_hrs():
    return con.sql("""
                   SELECT Year, "Total Minutes", "motoring", "sailing", "Motoring %", "Sailing %", "Nautical Miles",
                   SUM("Nautical Miles") OVER (ORDER BY Year) AS "Rolling NM",
                   ("motoring" / 60)::integer AS "Motoring Hrs",
                   ("sailing" / 60)::integer AS "Sailing Hrs"
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

local = False

st.markdown('''

# happyafloat.com

Family Adventures at Sea.
''')


con=define_connection(local)

#st.divider()
tab1, tab2, tab3 = st.tabs(["Main", "Charts", "Map"])
with tab1:
    #with st.container():
#   c1,c2,c3 = st.columns(3)
        nm = get_nm()

        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = nm,
          domain = {'x': [0, 1], 'y': [0, 1]},
         title = {'text': "Total Nautical Miles"},
            gauge = {'bar': {'color': "steelblue"},
                     'threshold' : {'line': {'color': "green", 'width': 4}, 
                                            'thickness': 0.75, 
                                            'value': 10000}
                     }))

        st.plotly_chart(fig, use_container_width=True)




with tab2:

    col1, col2 = st.columns(2)

    motor_sail_hrs = get_motoring_sailing_hrs()

#motor_sail_hrs       


    fig = px.bar(motor_sail_hrs, x="Year", y=["Motoring %","Sailing %"],
                 barmode='group',title = "Motoring vs Sailing",text_auto=True)

    fig.update_layout(yaxis_title='%', xaxis_title='', showlegend=True, legend_title="")
    fig.update_coloraxes(colorbar_ticklabelposition='inside',colorbar_ticks='inside',showscale=False)
    fig.update_traces(hovertemplate='%{y}%',marker_line_color='blue', marker_line_width=1.0)

    col1.plotly_chart(fig, use_container_width=True)

    fig = px.line(motor_sail_hrs, x="Year", y="Rolling NM", 
                  title = "Nautical Miles Over Time")
    fig.update_layout(yaxis_title='Nautical Miles', xaxis_title='', showlegend=True, )
    fig.add_shape(type="line", x0=2019, y0=1000, x1=2023, y1=8000, line_color='lightblue', line_dash='dash') 
    fig.update_traces(hovertemplate='%{y} Nautical Miles',marker_line_color='blue', marker_line_width=1.0)

    col2.plotly_chart(fig, use_container_width=True)