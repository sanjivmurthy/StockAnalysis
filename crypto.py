import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
#from pandas_datareader import data as web
from datetime import datetime as dt
import numpy as np
import pandas as pd


#############################################
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.cryptocurrencies import CryptoCurrencies
from pprint import pprint
import matplotlib.pyplot as plt
##############################################

app = dash.Dash()

colors = {                                     
    'background': '#001016',                   
    'text': '#fff9f9'                          
}  

app.layout = html.Div([
    html.H1('Crypto Price by the Minute'),
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Bitcoin', 'value': 'BTC'},
            {'label': 'Bitcoin Cash', 'value': 'BCH'},
            {'label': 'Litecoin', 'value': 'LTC'},
            {'label': 'Etherium', 'value': 'ETH'},
            {'label': 'Dashcoin', 'value': 'DSH'},
            {'label': 'Monero', 'value': 'XMR'},
            {'label': 'Ripple', 'value': 'XRP'},
            {'label': 'ZCash', 'value': 'ZEC'},
            {'label': 'OmiseGo', 'value': 'OMG'},
            {'label': 'Steem', 'value': 'STEEM'}
        ],
        value='BTC'
    ),
    dcc.Graph(id='my-graph')
])



@app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown_value):

    x = selected_dropdown_value

    # df = web.DataReader(
    #     selected_dropdown_value, data_source='google',
    #     start=dt(2018, 1, 1), end=dt.now())
    # ts = TimeSeries(key='361NZHAPWQW945GZ', output_format='pandas')
    # data, meta_data = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='full')
    #data = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_INTRADAY&symbol=' + x + '&market=EUR&apikey=361NZHAPWQW945GZ&datatype=csv'
    df = pd.read_csv('https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_INTRADAY&symbol='+ x + '&market=EUR&apikey=361NZHAPWQW945GZ&datatype=csv')
    #df = pd.read_csv(data)
    return {
        'data': [{
            'x': df['timestamp'],
            'y': df['price (USD)']
        }]
    }

if __name__ == '__main__':
    app.run_server()