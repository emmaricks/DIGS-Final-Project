import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from threading import Thread

# reading the data from excel file


st.set_page_config(layout="wide")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
image = Image.open('pink.png')
dataset = pd.read_csv('/Users/emmaricks/Desktop/DataScience/DIGS20004/Projects/Final/GapMinderBasedViz.csv')
long_df = pd.read_csv('/Users/emmaricks/Desktop/DataScience/DIGS20004/Projects/Final/GestationalAgeByState.csv')
tot_abort = pd.read_csv('/Users/emmaricks/Desktop/DataScience/DIGS20004/Projects/Final/TotalAbortions.csv')
AbortionCostOverTime = pd.read_csv('/Users/emmaricks/Desktop/DataScience/DIGS20004/Projects/Final/AbortionCostOverTime.csv')



##################

state_political_affiliation = {
    'AL': 'Republican',
    'AK': 'Republican',
    'AZ': 'Republican',
    'AR': 'Republican',
    'CA': 'Democrat',
    'CO': 'Democrat',
    'CT': 'Democrat',
    'DE': 'Democrat',
    'FL': 'Swing',
    'GA': 'Republican',
    'HI': 'Democrat',
    'ID': 'Republican',
    'IL': 'Democrat',
    'IN': 'Republican',
    'IA': 'Republican',
    'KS': 'Republican',
    'KY': 'Republican',
    'LA': 'Republican',
    'ME': 'Democrat',
    'MD': 'Democrat',
    'MA': 'Democrat',
    'MI': 'Democrat',
    'MN': 'Democrat',
    'MS': 'Republican',
    'MO': 'Republican',
    'MT': 'Republican',
    'NE': 'Republican',
    'NV': 'Democrat',
    'NH': 'Democrat',
    'NJ': 'Democrat',
    'NM': 'Democrat',
    'NY': 'Democrat',
    'NC': 'Swing',
    'ND': 'Republican',
    'OH': 'Republican',
    'OK': 'Republican',
    'OR': 'Democrat',
    'PA': 'Swing',
    'RI': 'Democrat',
    'SC': 'Republican',
    'SD': 'Republican',
    'TN': 'Republican',
    'TX': 'Republican',
    'UT': 'Republican',
    'VT': 'Democrat',
    'VA': 'Democrat',
    'WA': 'Democrat',
    'WV': 'Republican',
    'WI': 'Swing',
    'WY': 'Republican'
}

state_colors = {
    'US': 'blue',
    'AL': 'lightcoral',
    'AK': 'lightgreen',
    'AZ': 'tomato',
    'AR': 'yellowgreen',
    'CA': 'green',
    'CO': 'slateblue',
    'CT': 'mediumvioletred',
    'DE': 'teal',
    'FL': 'orange',
    'GA': 'pink',
    'HI': 'deepskyblue',
    'ID': 'lightsteelblue',
    'IL': 'mediumblue',
    'IN': 'darkorange',
    'IA': 'mediumseagreen',
    'KS': 'orchid',
    'KY': 'goldenrod',
    'LA': 'red',
    'ME': 'cadetblue',
    'MD': 'darkviolet',
    'MA': 'crimson',
    'MI': 'chartreuse',
    'MN': 'forestgreen',
    'MS': 'indianred',
    'MO': 'midnightblue',
    'MT': 'indigo',
    'NE': 'seashell',
    'NV': 'darkslategray',
    'NH': 'skyblue',
    'NJ': 'blueviolet',
    'NM': 'coral',
    'NY': 'purple',
    'NC': 'darkkhaki',
    'ND': 'mediumslateblue',
    'OH': 'gold',
    'OK': 'peachpuff',
    'OR': 'darkgreen',
    'PA': 'chocolate',
    'RI': 'saddlebrown',
    'SC': 'hotpink',
    'SD': 'lightyellow',
    'TN': 'darkred',
    'TX': 'red',
    'UT': 'peru',
    'VT': 'blue',
    'VA': 'yellow',
    'WA': 'violet',
    'WV': 'lightpink',
    'WI': 'lightskyblue',
    'WY': 'darkturquoise',
}

def create_dash_app():
    app_ = dash.Dash(__name__)


    # Dropdown options for selecting states or political groups
    dropdown_options = [
        {'label': 'All States', 'value': 'All States'},
        {'label': 'Republican States', 'value': 'Republican'},
        {'label': 'Democrat States', 'value': 'Democrat'},
        {'label': 'Swing States', 'value': 'Swing'},
    ] + [{'label': state, 'value': state} for state in long_df['State'].unique()]

    # Define the layout
    app_.layout = html.Div(style={'backgroundColor': 'white', 'padding': '20px'}, children=[
        html.H1("Percentage of Abortions by Gestational Stage"),
        dcc.Dropdown(
            id='state-dropdown',
            options=dropdown_options,
            value=['All States'],  # Default value, All States is selected
            multi=True  # Allow multiple states to be selected
        ),
        dcc.Graph(id='gestational-stackedbar-chart')
    ])

    # Define callback to update the chart based on dropdown selection
    @app_.callback(
        Output('gestational-stackedbar-chart', 'figure'),
        [Input('state-dropdown', 'value')]
    )
    def update_figure(selected_states):
        # Print selected states for debugging
        print(f"Selected States: {selected_states}")

        # If "All States" is selected, show all states
        if 'All States' in selected_states or not selected_states:
            filtered_df = long_df
        elif 'Republican' in selected_states:
            # Filter for Republican states
            republican_states = [state for state, affiliation in state_political_affiliation.items() if affiliation == 'Republican']
            filtered_df = long_df[long_df['State'].isin(republican_states)]
        elif 'Democrat' in selected_states:
            # Filter for Democrat states
            democrat_states = [state for state, affiliation in state_political_affiliation.items() if affiliation == 'Democrat']
            filtered_df = long_df[long_df['State'].isin(democrat_states)]
        elif 'Swing' in selected_states:
            # Filter for Democrat states
            swing_states = [state for state, affiliation in state_political_affiliation.items() if affiliation == 'Swing']
            filtered_df = long_df[long_df['State'].isin(swing_states)]
        else:
            # If specific states are selected, filter based on those states
            filtered_df = long_df[long_df['State'].isin(selected_states)]  

        # Define the order of the 'age' categories for the x-axis
        age_order = ['≤6', '7–9', '10–13', '14–15', '16–17', '18–20', '≥21']
        color_map = {
        '≤6': 'rgb(255, 99, 132)',
        '7–9': 'rgb(54, 162, 235)',
        '10–13': 'rgb(75, 192, 192)',
        '14–15': 'rgb(153, 102, 255)',
        '16–17': 'rgb(255, 159, 64)',
        '18–20': 'rgb(255, 205, 86)',
        '≥21': 'rgb(199, 199, 199)',
    }
        
        # Create the bar chart
        fig_gest = px.bar(filtered_df, 
                    x="State", 
                    y="percent", 
                    color="age", 
                    barmode="stack", 
                    category_orders={"age": age_order},
                    title="Percentage of Abortions by Gestational Stage for Selected States", color_discrete_map=color_map)
        #fig_gest.update_traces(marker=dict(color=[color_map[age] for age in filtered_df['age']]))
        
        return fig_gest
    return app_

def run_dash_app():
    app = create_dash_app()
    app.run_server(debug=False, port=8097)
def start_dash_in_thread():
    thread = Thread(target=run_dash_app())
    thread.daemon = True
    thread.start()
    
def create_abortion_over_time_app():
    # Create the Dash app
    dropdown_options = [{'label': 'US', 'value': 'US'}] + [{'label': state, 'value': state} for state in tot_abort['state'] if state != 'US']
    tot_rate = dash.Dash(__name__)
    tot_rate.layout = html.Div(style={'backgroundColor': 'white', 'padding': '20px'}, children=[
        html.H1("Abortion Totals by State and Year"),
        dcc.Dropdown(
            id='state-dropdown',
            options=dropdown_options,
            value=['US'],  # Default value is 'US' selected
            multi=True  # Allow multiple states to be selected
        ),
        dcc.Graph(id='totabortion-line-graph')
    ])

    # Define callback to update the chart based on dropdown selection
    @tot_rate.callback(
        Output('totabortion-line-graph', 'figure'),
        [Input('state-dropdown', 'value')]
    )
    def update_totabort(selected_states):
        # If "US" is selected, include it, otherwise show the selected states
        if 'US' in selected_states:
            filtered_df = tot_abort[tot_abort['state'].isin(selected_states)]  # Filter for selected states and US
        else:
            filtered_df = tot_abort[tot_abort['state'].isin(selected_states)]  # Only the selected states

        # Plot the interactive line graph
        fig = px.line(filtered_df, 
                    x='Year', 
                    y='AbortionTotal', 
                    color='state', 
                    title="Abortion Totals by State Over Time",
                    labels={'AbortionTotal': 'Total Abortions', 'Year': 'Year'},
                    color_discrete_map=state_colors ,
                    markers=True) 

        return fig
    return tot_rate

def run_totabort_app():
    app = create_abortion_over_time_app()
    app.run_server(debug=False, port=8096)
def start_totabort_in_thread():
    thread = Thread(target=run_totabort_app())
    thread.daemon = True
    thread.start()

def run_dash_app(app, port):
    app.run_server(debug=False, port=port, use_reloader=False)  # Disable reloader when running in threads

# Start Dash apps in different threads
def start_dash_apps():
    # Create Dash apps
    app1 = create_dash_app()
    app2 = create_abortion_over_time_app()

    # Run Dash apps in separate threads
    thread1 = Thread(target=run_dash_app, args=(app1, 8096))
    thread2 = Thread(target=run_dash_app, args=(app2, 8097))

    thread1.daemon = True
    thread2.daemon = True
    thread1.start()
    thread2.start()


##################

col1, col2 = st.columns([0.1,0.9])
with col1:
    st.image(image,width=100)

html_title = """
    <style>
    .title-test {
    font-weight:bold;
    padding:5px;
    border-radius:6px;
    }
    </style>
    <center><h1 class="title-test">United State Abortion Data Dashboard</h1></center>"""
with col2:
    st.markdown(html_title, unsafe_allow_html=True)
    st.write("This dashboard shows information on abortion data by state, gestational stage, total abortions, and cost.")

col3, col4, col5 = st.columns([0.1,0.45,0.45])
with col3:
    box_date = str(datetime.datetime.now().strftime("%d %B %Y"))
    st.write(f"Last updated by:  \n {box_date}")

with col4:
    start_dash_apps()
    st.markdown(""" <iframe src="http://127.0.0.1:8096" width="600" height="500"></iframe>
""", unsafe_allow_html=True)

#_, view1, dwn1, view2, dwn2 = st.columns([0.15,0.20,0.20,0.20,0.20])
#with view1:
 #   expander = st.expander("Retailer wise Sales")
  #  data = df[["Retailer","TotalSales"]].groupby(by="Retailer")["TotalSales"].sum()
  #  expander.write(data)
#with dwn1:
   # st.download_button("Get Data", data = data.to_csv().encode("utf-8"),
    #                   file_name="RetailerSales.csv", mime="text/csv")


with col5:
    st.markdown(""" <iframe src="http://127.0.0.1:8097" width="600" height="500"></iframe>
""", unsafe_allow_html=True)

st.write("Writing! XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.")   

st.divider()


_, col6 = st.columns([0.1,1])
with col6:
    years_from_col = set(dataset['year'])
    years_ints = sorted(list(years_from_col))
    years = [str(year) for year in years_ints]

    continents = []
    for continent in dataset['political_affiliation']:
        if continent not in continents:
            continents.append(continent)


    figure = {
        'data': [],
        'layout': {},
        'frames': [],
        'config': {'scrollzoom': True}
    }

    # Layout for axes, hovermode, etc.
    figure['layout']['xaxis'] = {'range': [0, 520], 'title': 'Total Abortions', 'gridcolor': '#FFFFFF'}
    figure['layout']['yaxis'] = {'range': [0, 170], 'title': 'Number of Facilities', 'gridcolor': '#FFFFFF'}
    figure['layout']['hovermode'] = 'closest'
    figure['layout']['plot_bgcolor'] = 'rgb(223, 232, 243)'
    sliders_dict = {
    'active': 0,
    'yanchor': 'top',
    'xanchor': 'left',
    'currentvalue': {
        'font': {'size': 20},
        'prefix': 'Year:',
        'visible': True,
        'xanchor': 'right'
    },
    'transition': {'duration': 300, 'easing': 'cubic-in-out'},
    'pad': {'b': 10, 't': 50},
    'len': 0.9,
    'x': 0.1,
    'y': 0,
    'steps': []
    }
    figure['layout']['updatemenus'] = [
    {
        'buttons': [
            {
                'args': [None, {'frame': {'duration': 500, 'redraw': False},
                               'fromcurrent': True, 'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}],
                'label': 'Play',
                'method': 'animate'
            },
            {
                'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate',
                                  'transition': {'duration': 0}}],
                'label': 'Pause',
                'method': 'animate'
            }
        ],
        'direction': 'left',
        'pad': {'r': 10, 't': 87},
        'showactive': False,
        'type': 'buttons',
        'x': 0.1,
        'xanchor': 'right',
        'y': 0,
        'yanchor': 'top'
        }
    ]

    # Define custom colors for continents
    custom_colors = {
        'Republican': 'rgb(255, 0, 0)',
        'Democrat': 'rgb(0, 0, 255)',
        'Swing': 'rgb(128, 0, 128)'
    }
    year = 2017
    for continent in continents:
        dataset_by_year_and_cont = dataset[(dataset['year'] == int(year)) & (dataset['political_affiliation'] == continent)]
        
        # Trace data for each continent
        data_dict = go.Scatter(
            x=dataset_by_year_and_cont['tot_abortions'],
            y=dataset_by_year_and_cont['number_of_centers'],
            mode='markers',
            text=dataset_by_year_and_cont['State'],
            marker=dict(
                sizemode='area',
                sizeref=10,
                size=dataset_by_year_and_cont['cost'],
                color=custom_colors[continent]
            ),
            name=continent
        )
        figure['data'].append(data_dict)
        
    for year in years:
        frame_data = []
        for continent in continents:
            dataset_by_year_and_cont = dataset[(dataset['year'] == int(year)) & (dataset['political_affiliation'] == continent)]
            
            # Trace data for each continent in the current year
            data_dict = go.Scatter(
                x=dataset_by_year_and_cont['tot_abortions'],
                y=dataset_by_year_and_cont['number_of_centers'],
                mode='markers',
                text=dataset_by_year_and_cont['State'],
                marker=dict(
                    sizemode='area',
                    sizeref=10,
                    size=dataset_by_year_and_cont['cost'],
                    color=custom_colors[continent]
                ),
                name=continent
            )
            frame_data.append(data_dict)

        # Append the frame data
        figure['frames'].append(go.Frame(
            data=frame_data,
            name=str(year)
        ))

        # Slider step for the current year
        slider_step = {
            'args': [
                [year],
                {'frame': {'duration': 300, 'redraw': False},
                'mode': 'immediate',
                'transition': {'duration': 300}}
            ],
            'label': year,
            'method': 'animate'
        }
        sliders_dict['steps'].append(slider_step)


    figure['layout']['sliders'] = [sliders_dict]
    fig = go.Figure(
    data=figure['data'],
    layout=figure['layout'],
    frames=figure['frames']
    )
    st.plotly_chart(fig,use_container_width=True)
_, view3, dwn3 = st.columns([0.5,0.45,0.45])
with view3:
    expander = st.expander("View Abortion Data By State")
    expander.write(dataset)
with dwn3:
    st.download_button("Get Data", data = dataset.to_csv().encode("utf-8"), 
                       file_name = "Abortion_Data_Per_State.csv", mime="text/csv")
st.write("Writing! XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.")   

st.divider()

_, col7 = st.columns([0.1,1])


fig_cost = px.choropleth(
    AbortionCostOverTime,
    locations="State",  
    locationmode="USA-states",  
    color="cost",
    animation_frame="year",  
    color_continuous_scale="Blues",
    scope="usa",
    title="Abortion Cost Over Time",
    range_color=[150,850] #[long_df[long_df["cost"] != 0]["cost"].min(), long_df["cost"].max()]  
)


with col7:
    st.subheader(":point_right: Cost of Abortion By State")
    st.plotly_chart(fig_cost,use_container_width=True)

_, view4, dwn4 = st.columns([0.5,0.45,0.45])
with view4:
    expander = st.expander("View data for Abortion Cost over Time")
    expander.write(AbortionCostOverTime)
with dwn4:
    st.download_button("Get Data", data = AbortionCostOverTime.to_csv().encode("utf-8"),
                                        file_name="AbortionCostPerState.csv", mime="text.csv")
st.write("Writing!! XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.")   

#_,view5, dwn5 = st.columns([0.5,0.45,0.45])
#with view5:
   # expander = st.expander("View Sales Raw Data")
    #expander.write(df)
#with dwn5:
   # st.download_button("Get Raw Data", data = df.to_csv().encode("utf-8"),
     #                  file_name = "SalesRawData.csv", mime="text/csv")
st.divider()
