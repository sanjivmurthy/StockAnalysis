# set chdir to current dir
import os
import sys
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))
os.chdir(os.path.realpath(os.path.dirname(__file__)))

import dash
from dash.dependencies import Output, Event, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import sqlite3
import pandas as pd

from collections import Counter
import string
import regex as re
from cache import cache
from config import stop_words
import time
import pickle

# it's ok to use one shared sqlite connection
# as we are making selects only, no need for any kind of serialization as well
conn = sqlite3.connect('twitter.db', check_same_thread=False)

punctuation = [str(i) for i in string.punctuation]



sentiment_colors = {-1:"#EE6055",
                    -0.5:"#FDE74C",
                     0:"#FFE6AC",
                     0.5:"#D0F2DF",
                     1:"#9CEC5B",}


app_colors = {
    'background': '#0C0F0A',
    'text': '#FFFFFF',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}

POS_NEG_NEUT = 0.1

MAX_DF_LENGTH = 100

app = dash.Dash(__name__)
app.layout = html.Div(
    [   html.Div(className='container-fluid', children=[

        html.Div([ html.H2('Live Market Sentiment vs. Price' , style = {'text-align' : 'center' ,'color':"#CECECE",'position' : 'relative' , 'top' : '10px', 'left': '0px'}),
        html.Div([ html.H4('Crypto Price by the Minute', style = {'color':"#CECECE", 'float' : 'left'} ),
        html.Div([ html.H4('Stock Price by the Minute (Dollar)', style = {'color':"#CECECE",'float' : 'right'} ),
        # html.Div([ html.H6('Trading Hours: 24 Hours' , style = {'color':"#CECECE",'float' : 'left' , 'text-align':'left'})]),
        # html.Div([ html.H6('Trading Hours: Monday-Friday 9:30:00 - 16:00:00 EST' , style = {'color':"#CECECE",'float' : 'right' , 'position' : 'relative' ,'top' : '10px', 'text-align':'right'})]),
        html.Div([dcc.Dropdown(
                        id='crypto',
                        options=[
                            {'label': 'Bitcoin', 'value': 'BTC'},
                            {'label': 'Bitcoin Cash', 'value': 'BCH'},
                            {'label': 'Litecoin', 'value': 'LTC'},
                            {'label': 'Etherium', 'value': 'ETH'},
                            {'label': 'Coindash', 'value': 'CDT'},
                            {'label': 'DigitalCoin', 'value': 'CGC'},
                        ],
                        value='BTC' 
                    ),
                ], style = {'float': 'left' ,'width': '49%'})
        , 

        html.Div([dcc.Dropdown(
                    id='stock',
                    options=[
                        {'label': 'Microsoft', 'value': 'MSFT'},
                        {'label': 'Tesla', 'value': 'TSLA'},
                        {'label': 'Apple', 'value': 'AAPL'},
                        {'label': 'Disney', 'value': 'DIS'},
                        {'label': 'Netflix', 'value': 'NFLX'},
                        {'label': 'Twitter', 'value': 'TWTR'},
                        {'label': 'Nike', 'value': 'NKE'}
                    ],
                    value='MSFT' 
                ),
                ], style = {'float': 'right' ,'width': '49%'}),

    dcc.Graph(id='my-graph2' , style = {'width': '49%','position' : 'relative' , 'float':'left', 'margin-right':'0' })
    ]), dcc.Graph(id='my-graph', style = {'width': '49%','position' : 'relative' , 'float':'right', 'margin-left':'0'}),

        # dcc.Graph(id='my-graph', style = {'width': '49%', 'left': '0px' , 'position' : 'relative' , 'top' : '75px'})
        # ]),], style={'width':'98%','margin-left':10,'margin-right':10,'max-width':50000})

      # html.H4('Live Twitter Sentiment of Stocks', style={'color':"#CECECE",'position' : 'relative' , 'top' : '30px'}),
       
                 #html.H5('Search:', style={'color':app_colors['text']}),
        #     dcc.RadioItems(
        #     id='sentiment_term',
        #     options=[
        #         {'label': 'Microsoft', 'value': 'MSFT'},
        #         {'label': 'Tesla', 'value': 'TSLA'},
        #         {'label': 'Apple', 'value': 'AAPL'},
        #         # {'label': 'Berkshire Hathaway', 'value': 'BRK.A'},
        #         {'label': 'Disney', 'value': 'DIS'},
        #         # {'label': 'Facebook', 'value': 'FB'},
        #         # {'label': 'Bank of America', 'value': 'BAC'},
        #         {'label': 'Netflix', 'value': 'NFLX'},
        #         {'label': 'Twitter', 'value': 'TWTR'},
        #         {'label': 'Nike', 'value': 'NKE'}
        #     ],
        #     value='MSFT' , style = {'width': '49%', 'float': 'left' , 'position' : 'relative' , 'top' : '20px' }
        # ),

            html.Div([dcc.Dropdown(
                    id='sentiment_term',
                    options=[
                        {'label': 'Bitcoin', 'value': 'Bitcoin'},
                        {'label': 'Bitcoin Cash', 'value': 'Bitcoin Cash'},
                        {'label': 'Litecoin', 'value': 'Litecoin'},
                        {'label': 'Etherium', 'value': 'Etherium'},
                        {'label': 'Coindash', 'value': 'Coindash'},
                        {'label': 'DigitalCoin', 'value': 'DigitalCoin'},
                    ],
                    placeholder="Select Cryptocurrency" , value='Bitcoin'
                    #, style = {'width': '49%', 'float': 'left'} , labelStyle={'display': 'inline-block'}
                ),
                ], style = {'width': '49%', 'float': 'left', 'position' : 'relative' , 'top' : '60px'}),

            html.Div([dcc.Dropdown(
                    id='sentiment_term',
                    options=[
                        {'label': 'Apple', 'value': 'Apple'},
                        {'label': 'Facebook', 'value': 'Facebook'},
                        {'label': 'Twitter', 'value': 'Twitter'},
                        {'label': 'Netflix', 'value': 'Netflix'},
                        {'label': 'Amazon', 'value': 'Amazon'},
                        {'label': 'Google', 'value': 'Google'},
                    ],
                    placeholder="Select Stock" , value='Apple'
                    #, style = {'width': '49%', 'float': 'left'} , labelStyle={'display': 'inline-block'}
                ),
                ], style = {'width': '49%', 'float': 'right', 'position' : 'relative' , 'top' : '60px'}),



        html.Div(className='row', children=[html.Div(id='related-sentiment', 
                  # children=html.Button('Loading related terms...', id='related_term_button'), 
                                            className='col s12 m6 l6', style={"word-wrap":"break-word"}),
                                            html.Div(id='recent-trending', className='col s12 m6 l6', style={"word-wrap":"break-word"})]),

        html.Div(className='row', children=[
                                            html.Div(dcc.Graph(id='live-graph', animate=False , style={'position' : 'relative' , 'top' : '60px'}), className='col s12 m6 l6'),
                                            html.Div(dcc.Graph(id='historical-graph', animate=False , style={'position' : 'relative' , 'top' : '60px'}), className='col s12 m6 l6')
                                            ]),

        html.Div(className='row', children=[html.Div(id="recent-tweets-table", className='col s12 m6 l6' , style={'position' : 'relative' , 'top' : '60px'}),
                                            html.Div(dcc.Graph(id='sentiment-pie', animate=False , style={'position' : 'relative' , 'top' : '60px'}), className='col s12 m6 l6'),]),
        
        dcc.Interval(
            id='graph-update',
            interval=1*1000
        ),
        dcc.Interval(
            id='historical-update',
            interval=60*1000
        ),

        dcc.Interval(
            id='related-update',
            interval=30*1000
        ),

        dcc.Interval(
            id='recent-table-update',
            interval=2*1000
        ),

        dcc.Interval(
            id='sentiment-pie-update',
            interval=60*1000
        ),

    ], style={'backgroundColor': app_colors['background'], 'margin-top':'0px', 'height':'2300px'},
),
]),
]),
], style={'backgroundColor': app_colors['background']} )


def df_resample_sizes(df, maxlen=MAX_DF_LENGTH):
    df_len = len(df)
    resample_amt = 100
    vol_df = df.copy()
    vol_df['volume'] = 1

    ms_span = (df.index[-1] - df.index[0]).seconds * 1000
    rs = int(ms_span / maxlen)

    df = df.resample('{}ms'.format(int(rs))).mean()
    df.dropna(inplace=True)

    vol_df = vol_df.resample('{}ms'.format(int(rs))).sum()
    vol_df.dropna(inplace=True)

    df = df.join(vol_df['volume'])

    return df

# make a counter with blacklist words and empty word with some big value - we'll use it later to filter counter
stop_words.append('')
blacklist_counter = Counter(dict(zip(stop_words, [1000000]*len(stop_words))))

# complie a regex for split operations (punctuation list, plus space and new line)
split_regex = re.compile("[ \n"+re.escape("".join(punctuation))+']')

def related_sentiments(df, sentiment_term, how_many=15):
    try:

        related_words = {}

        # it's way faster to join strings to one string then use regex split using your punctuation list plus space and new line chars
        # regex precomiled above
        tokens = split_regex.split(' '.join(df['tweet'].values.tolist()).lower())

        # it is way faster to remove stop_words, sentiment_term and empty token by making another counter
        # with some big value and substracting (counter will substract and remove tokens with negative count)
        blacklist_counter_with_term = blacklist_counter.copy()
        blacklist_counter_with_term[sentiment_term] = 1000000
        counts = (Counter(tokens) - blacklist_counter_with_term).most_common(15)

        for term,count in counts:
            try:
                df = pd.read_sql("SELECT sentiment.* FROM  sentiment_fts fts LEFT JOIN sentiment ON fts.rowid = sentiment.id WHERE fts.sentiment_fts MATCH ? ORDER BY fts.rowid DESC LIMIT 200", conn, params=(term,))
                related_words[term] = [df['sentiment'].mean(), count]
            except Exception as e:
                with open('errors.txt','a') as f:
                    f.write(str(e))
                    f.write('\n')

        return related_words

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')


def quick_color(s):
    # except return bg as app_colors['background']
    if s >= POS_NEG_NEUT:
        # positive
        return "#002C0D"
    elif s <= -POS_NEG_NEUT:
        # negative:
        return "#270000"

    else:
        return app_colors['background']

def generate_table(df, max_rows=10):
    return html.Table(className="responsive-table",
                      children=[
                          html.Thead(
                              html.Tr(
                                  children=[
                                      html.Th(col.title()) for col in df.columns.values],
                                  style={'color':app_colors['text']}
                                  )
                              ),
                          html.Tbody(
                              [
                                  
                              html.Tr(
                                  children=[
                                      html.Td(data) for data in d
                                      ], style={'color':app_colors['text'],
                                                'background-color':quick_color(d[2])}
                                  )
                               for d in df.values.tolist()])
                          ]
    )


def pos_neg_neutral(col):
    if col >= POS_NEG_NEUT:
        # positive
        return 1
    elif col <= -POS_NEG_NEUT:
        # negative:
        return -1

    else:
        return 0
    
            
@app.callback(Output('recent-tweets-table', 'children'),
              [Input(component_id='sentiment_term', component_property='value')],
              events=[Event('recent-table-update', 'interval')])        
def update_recent_tweets(sentiment_term):
    if sentiment_term:
        df = pd.read_sql("SELECT sentiment.* FROM sentiment_fts fts LEFT JOIN sentiment ON fts.rowid = sentiment.id WHERE fts.sentiment_fts MATCH ? ORDER BY fts.rowid DESC LIMIT 10", conn, params=(sentiment_term+'*',))
    else:
        df = pd.read_sql("SELECT * FROM sentiment ORDER BY id DESC, unix DESC LIMIT 10", conn)

    df['date'] = pd.to_datetime(df['unix'], unit='ms')

    df = df.drop(['unix','id'], axis=1)
    df = df[['date','tweet','sentiment']]

    return generate_table(df, max_rows=10)


@app.callback(Output('sentiment-pie', 'figure'),
              [Input(component_id='sentiment_term', component_property='value')],
              events=[Event('sentiment-pie-update', 'interval')])
def update_pie_chart(sentiment_term):

    # get data from cache
    for i in range(100):
        sentiment_pie_dict = cache.get('sentiment_shares', sentiment_term)
        if sentiment_pie_dict:
            break
        time.sleep(0.1)

    if not sentiment_pie_dict:
        return None

    labels = ['Positive','Negative']

    try: pos = sentiment_pie_dict[1]
    except: pos = 0

    try: neg = sentiment_pie_dict[-1]
    except: neg = 0

    
    
    values = [pos,neg]
    colors = ['#007F25', '#800000']

    trace = go.Pie(labels=labels, values=values,
                   hoverinfo='label+percent', textinfo='value', 
                   textfont=dict(size=20, color=app_colors['text']),
                   marker=dict(colors=colors, 
                               line=dict(color=app_colors['background'], width=2)))

    return {"data":[trace],'layout' : go.Layout(
                                                  title='Positive vs Negative sentiment for "{}" (longer-term)'.format(sentiment_term),
                                                  font={'color':app_colors['text']},
                                                  plot_bgcolor = app_colors['background'],
                                                  paper_bgcolor = app_colors['background'],
                                                  showlegend=True)}




@app.callback(Output('live-graph', 'figure'),
              [Input(component_id='sentiment_term', component_property='value')],
              events=[Event('graph-update', 'interval')])
def update_graph_scatter(sentiment_term):
    try:
        if sentiment_term:
            df = pd.read_sql("SELECT sentiment.* FROM sentiment_fts fts LEFT JOIN sentiment ON fts.rowid = sentiment.id WHERE fts.sentiment_fts MATCH ? ORDER BY fts.rowid DESC LIMIT 1000", conn, params=(sentiment_term+'*',))
        else:
            df = pd.read_sql("SELECT * FROM sentiment ORDER BY id DESC, unix DESC LIMIT 1000", conn)
        df.sort_values('unix', inplace=True)
        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)
        init_length = len(df)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
        df = df_resample_sizes(df)
        X = df.index
        Y = df.sentiment_smoothed.values
        Y2 = df.volume.values
        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Sentiment',
                mode= 'lines',
                yaxis='y2',
                line = dict(color = (app_colors['sentiment-plot']),
                            width = 4,)
                )

        data2 = plotly.graph_objs.Bar(
                x=X,
                y=Y2,
                name='Volume',
                marker=dict(color=app_colors['volume-bar']),
                )

        return {'data': [data,data2]
        ,'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                          yaxis=dict(range=[min(Y2),max(Y2*4)], title='Volume', side='right'),
                                                          yaxis2=dict(range=[min(Y),max(Y)], side='left', overlaying='y',title='sentiment'),
                                                          title='Live sentiment for: "{}"'.format(sentiment_term),
                                                          font={'color':app_colors['text']},
                                                          plot_bgcolor = app_colors['background'],
                                                          paper_bgcolor = app_colors['background'],
                                                          showlegend=False)
        }

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')

@app.callback(Output('historical-graph', 'figure'),
              [Input(component_id='sentiment_term', component_property='value'),
               ],
              events=[Event('historical-update', 'interval')])
def update_hist_graph_scatter(sentiment_term):
    try:
        if sentiment_term:
            df = pd.read_sql("SELECT sentiment.* FROM sentiment_fts fts LEFT JOIN sentiment ON fts.rowid = sentiment.id WHERE fts.sentiment_fts MATCH ? ORDER BY fts.rowid DESC LIMIT 10000", conn, params=(sentiment_term+'*',))
        else:
            df = pd.read_sql("SELECT * FROM sentiment ORDER BY id DESC, unix DESC LIMIT 10000", conn)
        df.sort_values('unix', inplace=True)
        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)
        # save this to a file, then have another function that
        # updates because of this, using intervals to read the file.
        # https://community.plot.ly/t/multiple-outputs-from-single-input-with-one-callback/4970
        # store related sentiments in cache
        cache.set('related_terms', sentiment_term, related_sentiments(df, sentiment_term), 120)

        #print(related_sentiments(df,sentiment_term), sentiment_term)
        init_length = len(df)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
        df.dropna(inplace=True)
        df = df_resample_sizes(df,maxlen=500)
        X = df.index
        Y = df.sentiment_smoothed.values
        Y2 = df.volume.values

        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Sentiment',
                mode= 'lines',
                yaxis='y2',
                line = dict(color = (app_colors['sentiment-plot']),
                            width = 4,)
                )

        data2 = plotly.graph_objs.Bar(
                x=X,
                y=Y2,
                name='Volume',
                marker=dict(color=app_colors['volume-bar']),
                )

        df['sentiment_shares'] = list(map(pos_neg_neutral, df['sentiment']))

        #sentiment_shares = dict(df['sentiment_shares'].value_counts())
        cache.set('sentiment_shares', sentiment_term, dict(df['sentiment_shares'].value_counts()), 120)

        return {'data': [data,data2]
        ,'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]), # add type='category to remove gaps'
                                                          yaxis=dict(range=[min(Y2),max(Y2*4)], title='Volume', side='right'),
                                                          yaxis2=dict(range=[min(Y),max(Y)], side='left', overlaying='y',title='sentiment'),
                                                          title='Longer-term sentiment for: "{}"'.format(sentiment_term),
                                                          font={'color':app_colors['text']},
                                                          plot_bgcolor = app_colors['background'],
                                                          paper_bgcolor = app_colors['background'],
                                                          showlegend=False)
        }

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')



max_size_change = .4

def generate_size(value, smin, smax):
    size_change = round((( (value-smin) /smax)*2) - 1,2)
    final_size = (size_change*max_size_change) + 1
    return final_size*120
    
    


# SINCE A SINGLE FUNCTION CANNOT UPDATE MULTIPLE OUTPUTS...
#https://community.plot.ly/t/multiple-outputs-from-single-input-with-one-callback/4970

# @app.callback(Output('related-sentiment', 'children'),
#               [Input(component_id='sentiment_term', component_property='value')],
#               events=[Event('related-update', 'interval')])
def update_related_terms(sentiment_term):
    try:

        # get data from cache
        for i in range(100):
            related_terms = cache.get('related_terms', sentiment_term) # term: {mean sentiment, count}
            if related_terms:
                break
            time.sleep(0.1)

        if not related_terms:
            return None

        buttons = [html.Button('{}({})'.format(term, related_terms[term][1]), id='related_term_button', value=term, className='btn', type='submit', style={'background-color':'#4CBFE1',
                                                                                                                                                           'margin-right':'5px',
                                                                                                                                                           'margin-top':'5px'}) for term in related_terms]
        #size: related_terms[term][1], sentiment related_terms[term][0]
        

        sizes = [related_terms[term][1] for term in related_terms]
        smin = min(sizes)
        smax = max(sizes) - smin  

        buttons = [html.H5('Terms related to "{}": '.format(sentiment_term), style={'color':app_colors['text']})]+[html.Span(term, style={'color':sentiment_colors[round(related_terms[term][0]*2)/2],
                                                              'margin-right':'15px',
                                                              'margin-top':'15px',
                                                              'font-size':'{}%'.format(generate_size(related_terms[term][1], smin, smax))}) for term in related_terms]


        return buttons
        

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')


#recent-trending div
# term: [sent, size]

@app.callback(Output('recent-trending', 'children'),
              [Input(component_id='sentiment_term', component_property='value')],
              events=[Event('related-update', 'interval')])
def update_recent_trending(sentiment_term):
    try:
        query = """
                SELECT
                        value
                FROM
                        misc
                WHERE
                        key = 'trending'
        """

        c = conn.cursor()

        result = c.execute(query).fetchone()

        related_terms = pickle.loads(result[0])



##        buttons = [html.Button('{}({})'.format(term, related_terms[term][1]), id='related_term_button', value=term, className='btn', type='submit', style={'background-color':'#4CBFE1',
##                                                                                                                                                           'margin-right':'5px',
##                                                                                                                                                           'margin-top':'5px'}) for term in related_terms]
        #size: related_terms[term][1], sentiment related_terms[term][0]
        

        sizes = [related_terms[term][1] for term in related_terms]
        smin = min(sizes)
        smax = max(sizes) - smin  

        # buttons = [html.H5('Recently Trending Terms: ', style={'color':app_colors['text']})]+[html.Span(term, style={'color':sentiment_colors[round(related_terms[term][0]*2)/2],
        #                                                       'margin-right':'15px',
        #                                                       'margin-top':'15px',
        #                                                       'font-size':'{}%'.format(generate_size(related_terms[term][1], smin, smax))}) for term in related_terms]


        return buttons
        

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')

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
        }],
        'layout' : go.Layout(
                          yaxis=dict( title='Price (USD)'),
                          xaxis=dict( title= 'Time Elapsed'),
                          title='Stock Price: ',
                          font={'color':app_colors['text']},
                          plot_bgcolor = app_colors['background'],
                          paper_bgcolor = app_colors['background'],
                          showlegend=False)

    }
            

@app.callback(Output('my-graph2', 'figure'), [Input('crypto', 'value')])
def update_graph2(selected_dropdown_value):

    x = selected_dropdown_value

    # df = web.DataReader(
    #     selected_dropdown_value, data_source='google',
    #     start=dt(2018, 1, 1), end=dt.now())
    # ts = TimeSeries(key='361NZHAPWQW945GZ', output_format='pandas')
    # data, meta_data = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='full')
    #data = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_INTRADAY&symbol=BTC&market=USD&apikey=demo&datatype=csv'
    df = pd.read_csv('https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_INTRADAY&symbol='+ x + '&market=USD&apikey=361NZHAPWQW945GZ&datatype=csv')
    #df = pd.read_csv(data)
    return {
        'data': [{
            'x': df['timestamp'],
            'y': df['price (USD)']
        }],
        'layout': go.Layout(
                          yaxis=dict( title='Price (USD)'),
                          xaxis=dict( title= 'Time Elapsed'),
                          title='Cryptocurrency Price: ',
                          font={'color':app_colors['text']},
                          plot_bgcolor = app_colors['background'],
                          paper_bgcolor = app_colors['background'],
                          showlegend=False)
    }            

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
for css in external_css:
    app.css.append_css({"external_url": css})


external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js',
               'https://pythonprogramming.net/static/socialsentiment/googleanalytics.js']
for js in external_js:
    app.scripts.append_script({'external_url': js})

server = app.server
dev_server = app.run_server
