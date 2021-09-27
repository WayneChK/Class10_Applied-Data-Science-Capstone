# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                 {'label':f'launch site {Lsite}',
                                                 'value':Lsite} for Lsite in spacex_df['Launch Site'].unique()
                                                 ],
                                             value='All Sites',
                                             style={'textAlign':'center'}
                                             ),
                                html.Br(),
                                html.Div(id='user_selection'),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',min=min_payload-50,max=max_payload+50,
                                                step=(max_payload-min_payload)/50,
                                                marks={500:f'500 KG',5000:f'3000 KG'},
                                                value=[500,5000]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    [Output(component_id='success-pie-chart',component_property='figure'),
     Output(component_id='user_selection',component_property='children'),
     Output(component_id='success-payload-scatter-chart',component_property='figure')],
    [Input(component_id='site-dropdown',component_property='value'),
     Input(component_id='payload-slider',component_property='value')]
     )
def chart_plot(site_i,payLD):
    if site_i=='All Sites':
        df_allsite=spacex_df.groupby(['Launch Site'])['class'].sum()
        df_allsite=df_allsite.reset_index()
        fig_pie=px.pie(df_allsite,values='class',names='Launch Site',title='Total Sucessful Launches at Each Site')
        # filter by input payloads from slider
        df_allScat=spacex_df[(spacex_df['Payload Mass (kg)']>payLD[0])&(spacex_df['Payload Mass (kg)']<payLD[1])]
        fig_scat=px.scatter(df_allScat,x='Payload Mass (kg)',y='class',color='Launch Site', title='Success Counts at All Sites')
    else:
        df_1=spacex_df.groupby('Launch Site')['class'].sum()   # it returns a pd series
        df_all=spacex_df.groupby('Launch Site')['class'].size()
        df_0=df_all-df_1
        dic={'Outcome':['Success','Failure'],'Counts':[df_1[site_i],df_0[site_i]]}
        plt_df=pd.DataFrame(dic)
        fig_pie=px.pie(plt_df,values='Counts',names='Outcome',title=f'Success vs Failure Counts for Site {site_i}')
        # select the group of input site
        df_selGP=spacex_df.groupby('Launch Site').get_group(site_i)
        df_selGP=df_selGP[(df_selGP['Payload Mass (kg)']>payLD[0])&(df_selGP['Payload Mass (kg)']<payLD[1])]
        fig_scat=px.scatter(df_selGP,x='Payload Mass (kg)',y='class', color='Booster Version',title=f'Success Counts at Site {site_i}')
    return fig_pie, f'You have selected {site_i}',fig_scat

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output


# Run the app
if __name__ == '__main__':
    app.run_server()
