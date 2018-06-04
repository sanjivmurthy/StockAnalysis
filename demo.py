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

app.layout =  html.Div([

    html.Div([html.H1('Live Market Sentiment Analysis')]),

    html.Div([ html.H2('Crypto Price by the Minute (Europe)'),
    dcc.RadioItems(
        id='crypto',
        options=[
            {'label': 'Bitcoin', 'value': 'BTC'},
            {'label': 'Bitcoin Cash', 'value': 'BCH'},
            {'label': 'Litecoin', 'value': 'LTC'},
            {'label': 'Etherium', 'value': 'ETH'},
        ],
        value='BTC' , style = {'width': '49%', 'float': 'left'}
    )
    ,dcc.Graph(id='my-graph2' , style = {'width': '49%', 'left': '0px' , 'position' : 'relative' , 'top' : '50px'})
    ]),

    html.Div([ html.H2('Stock Price by the Minute (US)' , style = {'position' : 'relative' , 'top' : '20px'}),
    html.Div([ html.H3('Trading Hours: Monday-Friday 9:30:00 - 16:00:00' , style = {'position' : 'relative' , 'top' : '20px'})]),
    dcc.RadioItems(
        id='stock',
        options=[
            {'label': 'Microsoft', 'value': 'MSFT'},
            {'label': 'Tesla', 'value': 'TSLA'},
            {'label': 'Apple', 'value': 'AAPL'},
            {'label': 'Berkshire Hathaway', 'value': 'BRK.A'},
            {'label': 'Disney', 'value': 'DIS'},
            {'label': 'Facebook', 'value': 'FB'},
            {'label': 'Bank of America', 'value': 'BAC'},
            {'label': 'Netflix', 'value': 'NFLX'},
            {'label': 'Twitter', 'value': 'TWTR'},
            {'label': 'Nike', 'value': 'NKE'}
        ],
        value='MSFT' , style = {'width': '49%', 'float': 'left' , 'position' : 'relative' , 'top' : '20px' }
    )
    , dcc.Graph(id='my-graph', style = {'width': '49%', 'left': '0px' , 'position' : 'relative' , 'top' : '70px' })
    ]),
    ])



@app.callback(Output('my-graph', 'figure'), [Input('stock', 'value')])
def update_graph(selected_dropdown_value):

    x = selected_dropdown_value

    # df = web.DataReader(
    #     selected_dropdown_value, data_source='google',
    #     start=dt(2018, 1, 1), end=dt.now())
    # ts = TimeSeries(key='361NZHAPWQW945GZ', output_format='pandas')
    # data, meta_data = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='full')
    data = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=' + x + '&interval=1min&apikey=361NZHAPWQW945GZ&datatype=csv'
    #df = pd.read_csv('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=1min&apikey=361NZHAPWQW945GZ&datatype=csv')
    df = pd.read_csv(data)
    return {
        'data': [{
            'x': df['timestamp'],
            'y': df['close']
        }]
    }




@app.callback(Output('my-graph2', 'figure'), [Input('crypto', 'value')])
def update_graph2(selected_dropdown_value):

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


