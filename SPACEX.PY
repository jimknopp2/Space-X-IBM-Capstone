# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
spacex_df = spacex_df.drop(['Unnamed: 0'],axis=1)
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
spacex_df.columns = [i.replace(' ','_') for i in spacex_df.columns]
Sites_list = [i for i in spacex_df.Launch_Site.unique()]

# Create a dash application
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                      {'label':'All Sites', 'value':'Allsite'},
                                                      {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                      {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                      {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                      {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}],
                                             value='Allsite',   
                                             placeholder='Select a Launch Site here',
                                             searchable= True,
                                             style={'width':'100%','padding':'3px','font size':'20px','text-align':'center'}
                                ),              
                                html.Br(),
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                value=[1000, 5000],
                                                marks={0:'0', 2000:'2000', 4000:'4000', 6000:'6000', 8000:'8000', 10000:'10000'}
                                ),
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback( 
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'))

def get_graph (select):
    if select == 'Allsite':
       fig = px.pie(spacex_df, values='class', names='Launch_Site', title='Success Rate by Launch Sites', color_discrete_sequence=px.colors.qualitative.Set3)
#color_discrete_map={'CCAFS LC-40':'lightcyan','VAFB SLC-4E':'cyan','KSC LC-39A':'royalblue','CCAFS SLC-40':'darkblue'})
       return fig        
    else:
        f_data = spacex_df[spacex_df['Launch_Site'] == select]
        f_data = f_data['Launch_Site'].groupby(spacex_df['class']).count().reset_index()
        fig = px.pie(f_data, values='Launch_Site', names='class', title='Success Rate by Launch Sites', 
                     color_discrete_sequence=px.colors.sequential.Bluered) 
        fig.update_layout(uniformtext_minsize=20, uniformtext_mode='hide')
        return fig 

# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback( 
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value'))

def get_graf (select, Range):
    low, high = Range
    scatt_data = spacex_df[spacex_df['Payload_Mass_(kg)'].apply(lambda x : x > low and x < high)].reset_index()
    if select == 'Allsite':
        scatt_fig = px.scatter(scatt_data, x= 'Payload_Mass_(kg)', y='class', color='Booster_Version',
                               title='Success correlation by Payload Mass & BoosterVersion')
        return scatt_fig
    else:
        scatt_data = scatt_data[spacex_df['Launch_Site']== select].reset_index()
        scatt_data = scatt_data.groupby(['Launch_Site','class', 'Booster_Version'])['Payload_Mass_(kg)'].sum().reset_index()
        scatt_fig = px.scatter(scatt_data, x= 'Payload_Mass_(kg)', y='class', color='Booster_Version',
                               title='Success correlation by Payload Mass & BoosterVersion')
        return scatt_fig            

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)