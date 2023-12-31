import streamlit as st
import duckdb
import plotly.graph_objects as go
import plotly.express as px
import pydeck as pdk

st.set_page_config(
    page_title="Happyafloat Dashboard",
    page_icon="⛵",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.happyafloat.com',
        'Report a bug': "https://www.happyafloat.com",
        'About': "# Happyafloat Dash\n\nNumber crunching data from our log book!"
    }
)
st.title('happyafloat.com')
st.subheader('Family Adventures at Sea')
api_url = st.secrets["api_url"]

@st.cache_resource
def define_connection():
        return duckdb.connect("")
    
con=define_connection()    

@st.cache_data
def get_nm():
     return con.sql(f"SELECT * FROM read_json_auto('{api_url}/nm/')").fetchall()[0][0]

@st.cache_data
def get_ports(ports):
    return con.sql("""
                    SELECT end_port, any_value(lat)::FLOAT as latitude, any_value(lng)::FLOAT as longitude, COUNT(end_port) as visits
                    FROM  ports
                    GROUP BY end_port""").df()  

@st.cache_data
def get_all_ports():
    return con.sql(f"SELECT * FROM read_json_auto('{api_url}/ports/')").df()

@st.cache_data
def get_motoring_sailing_hrs():
    return con.sql(f"SELECT * FROM read_json_auto('{api_url}/hours/')").df()
    


tab1, tab2, tab3 , tab4 = st.tabs(["Main", "Charts", "Map", "Data"])
with tab1:
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

 
with tab3:
    all_ports = get_all_ports()
    ports = get_ports(all_ports)
    st.subheader('Destinations 2019-2023')
    px_map_tiles = 'carto-darkmatter'
    plot_size = ports['visits']
    mg = dict(l=0, r=0, b=20, t=10)
    cp = {'lat':55.6,'lon':-3}
    fig = px.scatter_mapbox(ports, lat="latitude", lon="longitude", center=cp, 
                            color=plot_size, color_continuous_scale='blues',
                            opacity=0.8, zoom=4, size="visits", size_max=16,  
                            height=500, hover_name="end_port", hover_data={"visits":True, "latitude":False, "longitude":False})
    fig.update_coloraxes(colorbar_ticklabelposition='inside',colorbar_ticks='inside',cmax=20,cmin=1,showscale=False)
    fig.update_layout(mapbox_style=px_map_tiles,margin=mg)
    st.plotly_chart(fig, use_container_width=True)


    st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=51.55,
        longitude=0.75,
        zoom=9.5,
        pitch=85,
        bearing=350,
    ),    tooltip={
        'html': '<b>Visits:</b> {elevationValue}',
        'style': {'color': 'white'}
    },
    layers=[
        pdk.Layer(
           'HexagonLayer',
           data=all_ports,
           get_position='[lng, lat]',
           radius=100,
           elevation_scale=10,
           elevation_range=[0, 1000],
           pickable=True,
           extruded=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=all_ports,
            get_position='[lat, lng]',
            get_color='[200, 30, 0, 160]',
            get_radius=1000,
        ),
    ],
))
    
with tab4:
    """
    Ports
    """
    ports

    """
    All Ports
    """
    all_ports

    """
    motor_sail_hrs
    """
    motor_sail_hrs