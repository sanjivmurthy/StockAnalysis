import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
#from pandas_datareader import data as web
from datetime import datetime as dt


#############################################
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.cryptocurrencies import CryptoCurrencies
from pprint import pprint
import matplotlib.pyplot as plt
##############################################

app = dash.Dash()

app.layout = html.Div([
    html.H1('Stock Tickers'),
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Coke', 'value': 'COKE'},
            {'label': 'Tesla', 'value': 'TSLA'},
            {'label': 'Apple', 'value': 'AAPL'}
        ],
        value='COKE'
    ),
    dcc.Graph(id='my-graph')
])


@app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown_value):

    # df = web.DataReader(
    #     selected_dropdown_value, data_source='google',
    #     start=dt(2018, 1, 1), end=dt.now())
    ts = TimeSeries(key='361NZHAPWQW945GZ', output_format='pandas')
    data, meta_data = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='full')
    return {
        'data': [{
            'x': dt(2018, 1, 1),
            'y': data['4. close']
        }]
    }

if __name__ == '__main__':
    app.run_server()