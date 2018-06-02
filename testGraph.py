import plotly
import plotly.plotly as py
# plotly.tools.set_credentials_file(username='sanjivp98', api_key='9EVZEvNLfHMrOyGTuja9')
# plotly.sign_in("sanjivp98", "9EVZEvNLfHMrOyGTuja9")

import plotly.graph_objs as go
import plotly.figure_factory as FF

import numpy as np
import pandas as pd



df = pd.read_csv('https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=MSFT&interval=1min&apikey=361NZHAPWQW945GZ&datatype=csv')

df_external_source = FF.create_table(df.head())
py.iplot(df_external_source, filename='MSFT Share Price (Minute)')


trace = go.Scatter(x = df['timestamp'], y = df['close'],
                  name='MSFT (Microsoft)')
layout = go.Layout(title='MSFT Intraday Prices',
                   plot_bgcolor='rgb(230, 230,230)', 
                   showlegend=True)
fig = go.Figure(data=[trace], layout=layout)

py.iplot(fig, filename='MSFT Intraday Prices')

if __name__ == '__main__':
    app.run_server(debug=True)