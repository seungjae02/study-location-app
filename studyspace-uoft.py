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
colors = [item[0] for item in sheet.batch_get(('G2:G',))[0]]
hov_text = [item[0] for item in sheet.batch_get(('I2:I',))[0]]
marker_sizes = [item[0] for item in sheet.batch_get(('J2:J',))[0]]

for i in range(len(marker_sizes)):
    marker_sizes[i] = int(marker_sizes[i])

# app settings
app = dash.Dash(__name__)
blackbold = {'color': 'black', 'font-weight': 'bold'}

app.layout = html.Div([
    # ---------------------------------------------------------------
    html.Div([
        # Input Names
        dcc.Checklist(id='name',
                      options=[{'label': str(b), 'value': b}
                               for b in names],
                      value=[b for b in names],
                      style={'display': 'none'}
                      ),

        # Input Addresses
        dcc.Checklist(id='address',
                      options=[{'label': str(b), 'value': b}
                               for b in addresses],
                      value=[b for b in addresses],
                      style={'display': 'none'}
                      ),


    ],  className='three columns'
    ),

    html.Button('Submit', id='submit-val', n_clicks=0),

    # Map
    html.Div([

        dcc.Graph(id='graph', config={'displayModeBar': False, 'scrollZoom': True},
                  style={'background': 'pink', 'padding-bottom': '2px',
                         'height': '100vh'}
                  )


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
        marker={'opacity': 0.5, 'color': colors, 'size': marker_sizes},
        unselected={'marker': {'opacity': 0.5}},
        selected={'marker': {'opacity': 1.0, 'size': 50}},
        hoverinfo='text',
        hovertext=hov_text
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
