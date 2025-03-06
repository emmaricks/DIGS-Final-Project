import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from threading import Thread

st.set_page_config(layout="wide")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
dataset = pd.read_csv('Data/Cleaned_Datasets/Miscarriages_Abortions_Centers.csv')#GapMinderBasedVizV2.csv')
long_df = pd.read_csv('Data/Cleaned_Datasets/GestationalAgeByState.csv')#
tot_abort = pd.read_csv('Data/Cleaned_Datasets/TotalRateAbortions.csv') #TotalAbortionsV2.csv')#
AbortionCostOverTime = pd.read_csv('Data/Cleaned_Datasets/AbortionCostOverTime.csv')#
WomenPerClinic = pd.read_csv('Data/Cleaned_Datasets/WomenPerClinicOverTime.csv')#
legality = pd.read_csv('Data/Cleaned_Datasets/legality.csv')#
preg_abort_rates = pd.read_csv('Data/Cleaned_Datasets/Pregnancy_Abortion_Rate_Age_State.csv')



#######  Dash Functions  ###########

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
    app_.layout = html.Div(style={'backgroundColor': 'white', 'padding': '5px'}, children=[
        html.H1("Percentage of Abortions by Gestational Stage (2022)", style={'fontSize': '30px'}),
        dcc.Dropdown(
            id='state-dropdown',
            options=dropdown_options,
            value=['All States'],  # Default value, All States is selected
            multi=True  # Allow multiple states to be selected
        ),
        dcc.Graph(id='gestational-stackedbar-chart', style={'marginBottom': '-10px'}),
        html.Div(
        children="Data source: CDC",
        style={'fontSize': '12px',
        'color': 'grey',
        'position': 'absolute',
        'bottom': '0px'}
    )
    ])

    # Define callback to update the chart based on dropdown selection
    @app_.callback(
        Output('gestational-stackedbar-chart', 'figure'),
        [Input('state-dropdown', 'value')]
    )
    def update_figure(selected_states):
        # Print selected states for debugging
        #print(f"Selected States: {selected_states}")

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
        fig_gest.update_layout(margin=dict(l=40, r=20, t=40, b=60),
                               yaxis=dict(
            title="Percentage",  
        )
    )
        
        return fig_gest
    return app_
def run_dash_app():
    app = create_dash_app()
    app.run_server(debug=True, port=8097)
def start_dash_in_thread():
    thread = Thread(target=run_dash_app())
    thread.daemon = True
    thread.start()
    
def create_abortion_over_time_app():
    # Create the Dash app
    #dropdown_options = [{'label': 'US', 'value': 'US'}] + [{'label': state, 'value': state} for state in tot_abort['state'] if state != 'US']
    dropdown_options = [
        {'label': 'Republican States', 'value': 'Republican'},
        {'label': 'Democrat States', 'value': 'Democrat'},
        {'label': 'Swing States', 'value': 'Swing'},
    ] + [{'label': 'US', 'value': 'US'}] + [{'label': state, 'value': state} for state in tot_abort['state'].unique() if state != 'US'] #[{'label': state, 'value': state} for state in tot_abort['State'].unique()]
    tot_rate = dash.Dash(__name__)
    tot_rate.layout = html.Div(style={'backgroundColor': 'white', 'padding': '5px'}, children=[
        html.H1("Abortion Rate by State and Year", style={'fontSize': '30px'}),
        dcc.Dropdown(
            id='state-dropdown',
            options=dropdown_options,
            value=['US'],  # Default value is 'US' selected
            multi=True  # Allow multiple states to be selected
        ),
        dcc.Graph(id='totabortion-line-graph'),
        html.Div(
        children="Data source: Guttmacher Institute",
        style={'fontSize': '12px',
        'color': 'grey',
        'position': 'absolute',
        'bottom': '0px'}
    )
    ])

    # Define callback to update the chart based on dropdown selection
    @tot_rate.callback(
        Output('totabortion-line-graph', 'figure'),
        [Input('state-dropdown', 'value')]
    )
    def update_figure(selected_states):
        if 'US' in selected_states or not selected_states:
            filtered_df =  tot_abort[tot_abort['state'].isin(selected_states)]
        elif 'Republican' in selected_states:
            # Filter for Republican states
            republican_states = [state for state, affiliation in state_political_affiliation.items() if affiliation == 'Republican']
            filtered_df = tot_abort[tot_abort['state'].isin(republican_states)]
        elif 'Democrat' in selected_states:
            # Filter for Democrat states
            democrat_states = [state for state, affiliation in state_political_affiliation.items() if affiliation == 'Democrat']
            filtered_df = tot_abort[tot_abort['state'].isin(democrat_states)]
        elif 'Swing' in selected_states:
            # Filter for Democrat states
            swing_states = [state for state, affiliation in state_political_affiliation.items() if affiliation == 'Swing']
            filtered_df = tot_abort[tot_abort['state'].isin(swing_states)]
        else:
            # If specific states are selected, filter based on those states
            filtered_df = tot_abort[tot_abort['state'].isin(selected_states)]  
        fig = px.line(filtered_df, 
                    x='Year', 
                    y='AbortionTotal', 
                    color='state', 
                    title="Abortion Rate among Women 15-44 by State Over Time",
                    labels={'AbortionTotal': 'Abortion Rate', 'Year': 'Year'},
                    color_discrete_map=state_colors ,
                    markers=True) 
        fig.update_layout(margin=dict(l=70, r=20, t=40, b=60))

        return fig
    return tot_rate
def run_totabort_app():
    app = create_abortion_over_time_app()
    app.run_server(debug=True, port=8096)
def start_totabort_in_thread():
    thread = Thread(target=run_totabort_app())
    thread.daemon = True
    thread.start()

rate_15_17 = preg_abort_rates[preg_abort_rates["age"]=="1517"]
abort_rate_15_17 = rate_15_17[rate_15_17["rate_type"]=="rate_abortions"]
preg_rate_15_17 = rate_15_17[rate_15_17["rate_type"]=="rate_pregnancies"]
    
def create_1517abortion_over_time_app():
    # Create the Dash app
    #dropdown_options = [{'label': 'US', 'value': 'US'}] + [{'label': state, 'value': state} for state in tot_abort['state'] if state != 'US']
    dropdown_options = [
        {'label': 'Republican States', 'value': 'Republican'},
        {'label': 'Democrat States', 'value': 'Democrat'},
        {'label': 'Swing States', 'value': 'Swing'},
    ] + [{'label': 'US', 'value': 'US'}] + [{'label': state, 'value': state} for state in abort_rate_15_17['State'].unique() if state != 'US'] #[{'label': state, 'value': state} for state in tot_abort['State'].unique()]
    abor_rate1517 = dash.Dash(__name__)
    abor_rate1517.layout = html.Div(style={'backgroundColor': 'white', 'padding': '5px'}, children=[
        html.H1("Abortions per 1000 Births for 15-17 Year Olds", style={'fontSize': '30px'}),
        dcc.Dropdown(
            id='state-dropdown',
            options=dropdown_options,
            value=['US'],  # Default value is 'US' selected
            multi=True  # Allow multiple states to be selected
        ),
        dcc.Graph(id='abortionrate1517-line-graph'),
        html.Div(
        children="Data source: Guttmacher Institute",
        style={'fontSize': '12px',
        'color': 'grey',
        'position': 'absolute',
        'bottom': '0px'}
    )
    ])

    # Define callback to update the chart based on dropdown selection
    @abor_rate1517.callback(
        Output('abortionrate1517-line-graph', 'figure'),
        [Input('state-dropdown', 'value')]
    )
    def update_figure(selected_states):
        if 'US' in selected_states or not selected_states:
            filtered_df =  abort_rate_15_17[abort_rate_15_17['State'].isin(selected_states)]
        elif 'Republican' in selected_states:
            # Filter for Republican states
            republican_states = [state for state, affiliation in state_political_affiliation.items() if affiliation == 'Republican']
            filtered_df = abort_rate_15_17[abort_rate_15_17['State'].isin(republican_states)]
        elif 'Democrat' in selected_states:
            # Filter for Democrat states
            democrat_states = [state for state, affiliation in state_political_affiliation.items() if affiliation == 'Democrat']
            filtered_df = abort_rate_15_17[abort_rate_15_17['State'].isin(democrat_states)]
        elif 'Swing' in selected_states:
            # Filter for Democrat states
            swing_states = [state for state, affiliation in state_political_affiliation.items() if affiliation == 'Swing']
            filtered_df = abort_rate_15_17[abort_rate_15_17['State'].isin(swing_states)]
        else:
            # If specific states are selected, filter based on those states
            filtered_df = abort_rate_15_17[abort_rate_15_17['State'].isin(selected_states)]  
        fig = px.line(filtered_df, 
                    x='year', 
                    y='rate', 
                    color='State', 
                    title="Number of Abortion per 1000 Births among Women 15-17",
                    labels={'rate': 'Abortion Ratio', 'Year': 'Year'},
                    color_discrete_map=state_colors ,
                    markers=True) 
        fig.update_layout(margin=dict(l=70, r=20, t=40, b=60))

        return fig
    return abor_rate1517
def run_abortrate1517_app():
    app = create_1517abortion_over_time_app()
    app.run_server(debug=True, port=8099)
def start_abortrate1517_in_thread():
    thread = Thread(target=run_abortrate1517_app())
    thread.daemon = True
    thread.start()

def create_1517preg_over_time_app():
    # Create the Dash app
    #dropdown_options = [{'label': 'US', 'value': 'US'}] + [{'label': state, 'value': state} for state in tot_abort['state'] if state != 'US']
    dropdown_options = [
        {'label': 'Republican States', 'value': 'Republican'},
        {'label': 'Democrat States', 'value': 'Democrat'},
        {'label': 'Swing States', 'value': 'Swing'},
    ] + [{'label': 'US', 'value': 'US'}] + [{'label': state, 'value': state} for state in abort_rate_15_17['State'].unique() if state != 'US'] #[{'label': state, 'value': state} for state in tot_abort['State'].unique()]
    preg_rate1517 = dash.Dash(__name__)
    preg_rate1517.layout = html.Div(style={'backgroundColor': 'white', 'padding': '5px'}, children=[
        html.H1("Pregnancy Rate for 15-17 year olds", style={'fontSize': '30px'}),
        dcc.Dropdown(
            id='state-dropdown',
            options=dropdown_options,
            value=['US'],  # Default value is 'US' selected
            multi=True  # Allow multiple states to be selected
        ),
        dcc.Graph(id='pregrate1517-line-graph'),
        html.Div(
        children="Data source: Guttmacher Institute",
        style={'fontSize': '12px',
        'color': 'grey',
        'position': 'absolute',
        'bottom': '0px'}
    )
    ])

    # Define callback to update the chart based on dropdown selection
    @preg_rate1517.callback(
        Output('pregrate1517-line-graph', 'figure'),
        [Input('state-dropdown', 'value')]
    )
    def update_figure(selected_states):
        if 'US' in selected_states or not selected_states:
            filtered_df =  preg_rate_15_17[preg_rate_15_17['State'].isin(selected_states)]
        elif 'Republican' in selected_states:
            # Filter for Republican states
            republican_states = [state for state, affiliation in state_political_affiliation.items() if affiliation == 'Republican']
            filtered_df = preg_rate_15_17[preg_rate_15_17['State'].isin(republican_states)]
        elif 'Democrat' in selected_states:
            # Filter for Democrat states
            democrat_states = [state for state, affiliation in state_political_affiliation.items() if affiliation == 'Democrat']
            filtered_df = preg_rate_15_17[preg_rate_15_17['State'].isin(democrat_states)]
        elif 'Swing' in selected_states:
            # Filter for Democrat states
            swing_states = [state for state, affiliation in state_political_affiliation.items() if affiliation == 'Swing']
            filtered_df = preg_rate_15_17[preg_rate_15_17['State'].isin(swing_states)]
        else:
            # If specific states are selected, filter based on those states
            filtered_df = preg_rate_15_17[preg_rate_15_17['State'].isin(selected_states)]  
        fig = px.line(filtered_df, 
                    x='year', 
                    y='rate', 
                    color='State', 
                    title="Pregnancy Rate among Women 15-17",
                    labels={'rate': 'Pregnancy Rate', 'year': 'Year'},
                    color_discrete_map=state_colors ,
                    markers=True) 
        fig.update_layout(margin=dict(l=70, r=20, t=40, b=60))

        return fig
    return preg_rate1517
def run_pregrate1517_app():
    app = create_1517preg_over_time_app()
    app.run_server(debug=True, port=8092)
def start_pregrate1517_in_thread():
    thread = Thread(target=run_pregrate1517_app())
    thread.daemon = True
    thread.start()


#For all apps:
def run_dash_app(app, port):
    app.run_server(debug=False, port=port, use_reloader=False)  # Disable reloader when running in threads
def start_dash_apps():
    # Create Dash apps
    app1 = create_dash_app()
    app2 = create_abortion_over_time_app()
    app3 = create_1517abortion_over_time_app()
    app4 = create_1517preg_over_time_app()

    # Run Dash apps in separate threads
    thread1 = Thread(target=run_dash_app, args=(app1, 8096))
    thread2 = Thread(target=run_dash_app, args=(app2, 8097))
    thread3 = Thread(target=run_dash_app, args=(app3, 8099))
    thread4 = Thread(target=run_dash_app, args=(app4, 8092))

    thread1.daemon = True
    thread2.daemon = True
    thread3.daemon = True
    thread4.daemon = True
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

###########################

col1, col2 = st.columns([0.1,0.9])
with col1:
    #st.image(image,width=100)
    box_date = str(datetime.datetime.now().strftime("%d %B %Y"))
    st.write("  \n")
    st.write("  \n")
    st.write(f" Last updated:  \n {box_date}")

html_title = """
    <style>
    .title-test {
    font-weight:bold;
    padding:5px;
    border-radius:6px;
    }
    </style>
    <center><h1 class="title-test"> 🇺🇸 United States Abortion Data Dashboard</h1></center>"""
with col2:
    st.markdown(html_title, unsafe_allow_html=True)
    st.write("This dashboard shows information on abortion data by state, gestational stage, total abortions, and cost.")
st.divider()   
_, col3 = st.columns([0.1,1])


with col3:
    st.subheader("Legality of Abortion")
    status_color_map = {
    "Banned": "red",
    "Legal": "lightgreen",
    "Ban blocked": "green",
    "Gestational limit": "#FFFF99"
}

    legal = px.choropleth(
    legality, 
    locations="state",  
    locationmode="USA-states",  
    color="Status of abortion", 
    color_discrete_map=status_color_map,  
    title="Status of Abortion by State as of March 2025",
    labels={"Status of abortion": "Abortion Status", "More details": ""},
    hover_data = ["state",  "Status of abortion", "More details"] 
)
    legal.update_geos(projection_type="albers usa", visible=True)
    legal.update_layout(
    height=600,  
    margin={"r": 0, "t": 50, "l": 0, "b": 0},  
)
    st.plotly_chart(legal,use_container_width=True)
    st.markdown(
        """
        <div style="text-align: left; font-size: 12px; color: grey;">
            Data source: New York Times
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()
col4, col5 = st.columns([0.55,0.45])
with col4:
    start_dash_apps()
    st.markdown(""" <iframe src="http://127.0.0.1:8096" width="700" height="600"></iframe>
""", unsafe_allow_html=True)

with col5:
    st.markdown(""" <iframe src="http://127.0.0.1:8097" width="600" height="600"></iframe>
""", unsafe_allow_html=True)
st.divider()
st.write("Looking at the left chart, breaking down the total number of abortions performed in 2022 by gestational age by state, we see that on average, about 35 percent of abortions in Democrat states are performed at 6 or less weeks. In Republican states, about 33 percent of abortions in Democrat states are performed at 6 or less weeks. The majority of abortions are preformed at 7 to 9 weeks across both groups of states. In the total abortions graph on the right, we see the change in the number of abortions in the US as well as by state from 2005-2020. Overall, there has been a decrease in abortions since 2005, with a bit of an uptick since 2017.")
st.divider()


_, col6 = st.columns([0.1,1])
with col6:
    st.subheader("Comparing Total Abortions, Total Miscarriages, and Number of Women's Healthcare Facilities by State")
    years_from_col = set(dataset['year'])
    years_ints = sorted(list(years_from_col))
    years = [str(year) for year in years_ints]

    states = []
    for state in dataset['political_affiliation']:
        if state not in states:
            states.append(state)


    figure = {
        'data': [],
        'layout': {},
        'frames': [],
        'config': {'scrollzoom': True}
    }

    # Layout for axes, hovermode, etc.
    figure['layout']['title'] = 'Total Miscarraiges vs Total Abortions Over Time'
    figure['layout']['xaxis'] = {'range': [680, 152400], 'title': 'Total Abortions', 'gridcolor': '#FFFFFF'}
    figure['layout']['yaxis'] = {'range': [1130, 107050], 'title': 'Total Miscarriages', 'gridcolor': '#FFFFFF'}
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
    custom_colors = {
        'Republican': 'rgb(255, 0, 0)',
        'Democrat': 'rgb(0, 0, 255)',
        'Swing': 'rgb(128, 0, 128)'
    }
    year = 2017
    for party in states:
        dataset_by_year_and_part = dataset[(dataset['year'] == int(year)) & (dataset['political_affiliation'] == party)]
        
        data_dict = go.Scatter(
            x=dataset_by_year_and_part['abortionstotal'],
            y=dataset_by_year_and_part['miscarriagestotal'],
            mode='markers',
            text=dataset_by_year_and_part['State'],
            marker=dict(
                sizemode='area',
                sizeref=1,
                size=dataset_by_year_and_part['number_of_centers'],
                color=custom_colors[party]
            ),
            name=party
        )
        figure['data'].append(data_dict)
        
    for year in years:
        frame_data = []
        for party in states:
            dataset_by_year_and_part = dataset[(dataset['year'] == int(year)) & (dataset['political_affiliation'] == party)]
            
            data_dict = go.Scatter(
                x=dataset_by_year_and_part['abortionstotal'],
                y=dataset_by_year_and_part['miscarriagestotal'],
                mode='markers',
                text=dataset_by_year_and_part['State'],
                marker=dict(
                    sizemode='area',
                    sizeref=1,
                    size=dataset_by_year_and_part['number_of_centers'],
                    color=custom_colors[party]
                ),
                name=party
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
    st.markdown(
        """
        <div style="text-align: center; font-size: 12px; color: grey;">
            Data source: Advancing New Standards in Reproductive Health and GI
        </div>
        """,
        unsafe_allow_html=True
    )
_, view3, dwn3 = st.columns([0.5,0.45,0.45])
with view3:
    expander = st.expander("View Abortion and Miscarriage Data By State")
    expander.write(dataset)
with dwn3:
    st.download_button("Get Data", data = dataset.to_csv().encode("utf-8"), 
                       file_name = "Abortion_Data_Per_State.csv", mime="text/csv")
    
st.divider()
st.write("Writing! XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.")   
st.divider()
#####################
st.divider()
col10, col11 = st.columns([0.5,0.5])
with col10:
    start_dash_apps()
    st.markdown(""" <iframe src="http://127.0.0.1:8099" width="650" height="600"></iframe>
""", unsafe_allow_html=True)

with col11:
    st.markdown(""" <iframe src="http://127.0.0.1:8092" width="650" height="600"></iframe>
""", unsafe_allow_html=True)
st.divider()
st.write("Looking at the left chart, breaking down the total number of abortions performed in 2022 by gestational age by state, we see that on average, about 35 percent of abortions in Democrat states are performed at 6 or less weeks. In Republican states, about 33 percent of abortions in Democrat states are performed at 6 or less weeks. The majority of abortions are preformed at 7 to 9 weeks across both groups of states. In the total abortions graph on the right, we see the change in the number of abortions in the US as well as by state from 2005-2020. Overall, there has been a decrease in abortions since 2005, with a bit of an uptick since 2017.")
st.divider()
######################
_, col7 = st.columns([0.1,1])


with col7:
    st.subheader("Cost of Abortion By State")
    
    fig_cost = px.choropleth(
    AbortionCostOverTime,
    locations="State",  
    locationmode="USA-states",  
    color="cost",
    animation_frame="year",  
    color_continuous_scale="Blues",
    scope="usa",
    title="Abortion Cost Over Time",
    range_color=[150,850]  
)
    fig_cost.update_layout(
    height=600,  
    margin={"r": 0, "t": 50, "l": 0, "b": 50},  
)
    st.plotly_chart(fig_cost,use_container_width=True)
    st.markdown(
        """
        <div style="text-align: left; font-size: 12px; color: grey;">
            Data source: Advancing New Standards in Reproductive Health
        </div>
        """,
        unsafe_allow_html=True
    )

_, view4, dwn4 = st.columns([0.5,0.45,0.45])
with view4:
    expander = st.expander("View data for Abortion Cost over Time")
    expander.write(AbortionCostOverTime)
with dwn4:
    st.download_button("Get Data", data = AbortionCostOverTime.to_csv().encode("utf-8"),
                                        file_name="AbortionCostPerState.csv", mime="text.csv")
st.divider()
st.write("Writing!! XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.")   

_, col8 = st.columns([0.1,1])
with col8:
    st.subheader("Women Per Clinic By State")
    women_per_fac = px.choropleth(
    WomenPerClinic,
    locations="State",  
    locationmode="USA-states",  
    color="log_number_of_women_per_facility",  
    animation_frame="year",  
    color_continuous_scale="Cividis",
    scope="usa",
    title="Women's Health Centers Over Time (Log Scale)",
    range_color=[WomenPerClinic["log_number_of_women_per_facility"].min(), WomenPerClinic["log_number_of_women_per_facility"].max()] ,
    hover_data = ["State", "year", "log_number_of_women_per_facility", "number_of_women_per_facility"] 
)
    women_per_fac.update_traces(
    customdata=WomenPerClinic["number_of_women_per_facility"]  
)

    women_per_fac.update_traces(
    hovertemplate="<b>%{location}</b><br>"  
                  "Number of Women Per Facility: %{customdata}<br>" 
                  "log(Number of Women Per Facility): %{z}<br>" 
                  "Year: %{frame}<br>"  
)
    women_per_fac.update_layout(coloraxis_colorbar_title="Number of Women per Health Center (log)")
    women_per_fac.update_layout(
    height=600,  
    margin={"r": 0, "t": 50, "l": 0, "b": 50},  
)
    #women_per_fac = go.Figure(women_per_fac)
    st.plotly_chart(women_per_fac,use_container_width=True)
    st.markdown(
    """
    <div style="text-align: left; font-size: 12px; color: grey; margin-left: 20px;">
        Data source: Advancing New Standards in Reproductive Health
    </div>
    """,
    unsafe_allow_html=True
)
_, view5, dwn5 = st.columns([0.5,0.45,0.45])
with view5:
    expander = st.expander("View data for Women Served Per Facility over Time")
    expander.write(WomenPerClinic)
with dwn5:
    st.download_button("Get Data", data = WomenPerClinic.to_csv().encode("utf-8"),
                                        file_name="WomenPerFacilityByState.csv", mime="text.csv")
st.divider()   
st.write("Writing!! XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.")   


st.divider()
