from oauth2client.service_account import ServiceAccountCredentials
import gspread
import plotly.offline as py  # (version 4.4.1)
import dash  # (version 1.0.0)
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import numpy as np
import pandas as pd

mapbox_access_token = 'pk.eyJ1IjoiZXJpeXNkIiwiYSI6ImNrdHE1MDNoYjBzNzkyd3AzZGRibmZxZ3IifQ.H3yEfcNx_l80YR5XLGNAAw'

# API IMPORTS
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "studylocationapp-5aa90d2f8e44.json", scope)
client = gspread.authorize(creds)
sheet = client.open("studylocationapp").sheet1  # Open the spreadhseet
data = sheet.get_all_records()  # Get a list of all records

names = [item[0] for item in sheet.batch_get(('B2:B',))[0]]
lats = [item[0] for item in sheet.batch_get(('C2:C',))[0]]
longs = [item[0] for item in sheet.batch_get(('D2:D',))[0]]
addresses = [item[0] for item in sheet.batch_get(('E2:E',))[0]]
hover_txt = [name + '<br>' + address for name,
             address in zip(names, addresses)]


# app settings
df = pd.read_csv("finalrecycling.csv")
app = dash.Dash(__name__)
blackbold = {'color': 'black', 'font-weight': 'bold'}

app.layout = html.Div([
    # ---------------------------------------------------------------
    # Map_legen + Borough_checklist + Recycling_type_checklist + Web_link + Map
    html.Div([
        # html.Div([
        # html.Ul([
        #     html.Li("Compost", className='circle', style={'background': '#ff00ff', 'color': 'black',
        #         'list-style': 'none', 'text-indent': '17px'}),
        #     html.Li("Electronics", className='circle', style={'background': '#0000ff', 'color': 'black',
        #                                                       'list-style': 'none', 'text-indent': '17px', 'white-space': 'nowrap'}),
        #     html.Li("Hazardous_waste",  className='circle', style={'background': '#FF0000', 'color': 'black',
        #                                                            'list-style': 'none', 'text-indent': '17px'}),
        #     html.Li("Plastic_bags", className='circle', style={'background': '#00ff00', 'color': 'black',
        #                                                        'list-style': 'none', 'text-indent': '17px'}),
        #     html.Li("Recycling_bins", className='circle',  style={'background': '#824100', 'color': 'black',
        #                                                           'list-style': 'none', 'text-indent': '17px'}),
        # ], style={'border-bottom': 'solid 2px', 'border-color': 'RoyalBlue', 'padding-top': '6px'}
        # ),

        # Borough_checklist
        # html.Label(children=['Borough: '], style=blackbold),
        dcc.Checklist(id='name',
                      options=[{'label': str(b), 'value': b}
                               for b in names],
                      value=[b for b in names],
                      style={'display': 'none'}
                      ),

        # Recycling_type_checklist
        # html.Label(children=['Looking to recycle: '], style=blackbold),
        dcc.Checklist(id='address',
                      options=[{'label': str(b), 'value': b}
                               for b in addresses],
                      value=[b for b in addresses],
                      style={'display': 'none'}
                      ),

        # # Web_link
        # html.Br(),
        # html.Label(['Website:'], style=blackbold),
        # html.Pre(id='web_link', children=[],
        #          style={'white-space': 'pre-wrap', 'word-break': 'break-all',
        #                 'border': '1px solid black', 'text-align': 'center',
        #                 'padding': '12px 12px 12px 12px', 'color': 'blue',
        #                 'margin-top': '3px'}
        #          ),

    ],  className='three columns'
    ),

    # Map
    html.Div([
        dcc.Graph(id='graph', config={'displayModeBar': False, 'scrollZoom': True},
                  style={'background': 'pink', 'padding-bottom': '2px',
                         'height': '100vh'}
                  )
        # ], className='nine columns'
        # ),

    ], className='row'
    ),

], className='ten columns offset-by-one'
)

# ---------------------------------------------------------------
# Output of Graph


@ app.callback(Output('graph', 'figure'),
               [Input('name', 'value'),
               Input('address', 'value')])
def update_figure(name, address):

    # Create figure
    locations = [go.Scattermapbox(
        lon=longs,
        lat=lats,
        mode='markers',
        marker={'color': "Navy"},
        unselected={'marker': {'opacity': 1}},
        selected={'marker': {'opacity': 0.5, 'size': 25}},
        hoverinfo='text',
        hovertext=hover_txt,
    )]

    # Return figure
    return {
        'data': locations,
        'layout': go.Layout(
            uirevision='foo',  # preserves state of figure/map after callback activated
            clickmode='event+select',
            hovermode='closest',
            hoverdistance=2,
            title=dict(text="Study Space at UofT",
                       font=dict(size=50, color="SteelBlue")),
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=-17,
                style='light',
                center=dict(
                    lat=43.66416274156958,
                    lon=-79.39227603268147
                ),
                pitch=30,
                zoom=14.5
            ),
        )
    }
# ---------------------------------------------------------------
# callback for Web_link


@ app.callback(
    Output('web_link', 'children'),
    [Input('graph', 'clickData')])
def display_click_data(clickData):
    if clickData is None:
        return 'Click on any bubble'
    else:
        # print (clickData)
        the_link = clickData['points'][0]['customdata']
        if the_link is None:
            return 'No Website Available'
        else:
            return html.A(the_link, href=the_link, target="_blank")


# #--------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)
