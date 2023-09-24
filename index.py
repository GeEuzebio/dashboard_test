import datetime
from dash import Dash, html, dcc, dash_table, Input, Output, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from controller import get_data, vencimentos, get_ratio, stickers

today = datetime.datetime(datetime.datetime.now().year,datetime.datetime.now().month, datetime.datetime.now().day).strftime('%d/%m/%Y')

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.layout = dbc.Row(
    children=[
        dbc.Col(
            children=[
                html.P('ATIVO', style={'margin':'0'}),
                dbc.Input(
                    id='symbol',
                    value='PETR4', 
                    style={
                        'max-width':'150px',
                        'margin':'0'
                        })
            ],
            style={'max-width':'170px', 'background-color':'#000'}
            ),
        dbc.Col(
            children=[
                html.Div(
                    children=[
                        html.Img(id='img-ativo', style={'width':'50px', 'margin-left':'20px', 'border-radius':'5px', 'margin-right':'20px'}),
                html.Div(
                    children=[
                        html.H4(id='ativo'),
                        html.Div(
                            children=[
                                html.P(id='price'),
                                html.P(id='percentage')
                            ],
                        ),
                        html.Div(
                            children=[
                                html.P('Máxima', style={'color':'green', 'margin':'0', 'padding':'0'}),
                                html.P(id='max', style={'color':'green', 'margin':'0', 'padding':'0', 'text-align':'right'})
                            ],
                            style={'margin-left':'10px'}
                        ),
                        html.Div(
                            children=[
                                html.P('Mínima', style={'color':'red', 'margin':'0', 'padding':'0'}),
                                html.P(id='min', style={'color':'red', 'margin':'0', 'padding':'0', 'text-align':'right'})
                            ],
                            style={'margin-left':'10px'}
                        ),
                    ],
                    style={
                                'display':'flex',
                                'align-items':'center',
                                'justify-content':'space-around',
                                'max-width':'300px'
                            }
                    ),
                        ], 
                    style={'widht':'250px', 'display':'flex', 'align-items':'center'}),
                dcc.Graph(
                id='graph',
                figure=go.Figure(),
                style={'max-width': '100%', 'height':'480px'},
                config={'scrollZoom': True,
                        'displayModeBar': False,
                        'modeBarButtonsToRemove': ['toggleSpikelines', 'resetScale2d', 'sendDataToCloud'],
                        'modeBarButtons': [['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d']],
                        'modeBarButtonsToAdd': [],
                        }
            )
            ],
            style={'max-width':'650px', 'background-color':'#000'}
            ),
        dbc.Col(
            children=[
                html.P('Vencimentos', style={'margin':'0'}),
                dcc.Dropdown(
                    id='vencimento', 
                    placeholder='Escolha uma data', 
                    style={'max-width':'200px'}
                    ),
                html.Div(
                    children=[],
                    id='table-container', 
                    style={
                        'max-width':'400px',
                        'margin-top':'10px'
                        }
                    )
            ],
            style={'background-color':'#000'}
        )
    ],
    style={'background-color':'#292928'}
)
@app.callback(
    [Output('graph', 'figure'),
     Output('ativo', 'children'),
     Output('img-ativo', 'src'),
     Output('price', 'children'),
     Output('price', 'style'),
     Output('percentage', 'style'),
     Output('percentage', 'children'),
     Output('max', 'children'),
     Output('min', 'children')],
    [Input('symbol', 'value')],    
)
def update_graph(symbol):
    df = get_data(symbol)
    x = df.index
    candle = go.Figure(data=[go.Candlestick(x=x,
                                                open=df['o'].round(4),
                                                high=df['h'].round(4),
                                                low=df['l'].round(4),
                                                close=df['c'].round(4),
                                                line=dict(width=1))],
                           layout=go.Layout(
                               plot_bgcolor='rgba(255, 0, 0, 0)',
                               paper_bgcolor='rgba(0, 0, 0, 0)',
                               title=f'Gárfico de {symbol} em {today}',
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               clickmode='event'))
    candle.update_layout(xaxis_rangeslider_visible=False)
    src = f'https://d2titc900u8oh3.cloudfront.net/company_logos_icons/{symbol[0:4]}.png'
    ratio = get_ratio(symbol)
    if(df['c'].iloc[-2]<=df['c'].iloc[-1]):
        return candle, symbol, src, df['c'].tail(1), {'color':'green', 'font-size':'28px', 'margin':'0', 'padding':'0', 'text-align':'right'}, {'color':'green', 'font-size':'16px', 'margin':'0', 'padding':'0'}, f'+{(ratio["c"].iloc[-1]-ratio["c"].iloc[-2]).round(2)}(+{(100*(ratio["c"].iloc[-1]-ratio["c"].iloc[-2])/ratio["c"].iloc[-1]).round(2)}%)', ratio['h'].iloc[-1].round(2), ratio['l'].iloc[-1].round(2)
    else:
        return candle, symbol, src, df['c'].tail(1), {'color':'red', 'font-size':'28px', 'margin':'0', 'padding':'0', 'text-align':'right'}, {'color':'red', 'font-size':'16px', 'margin':'0', 'padding':'0'}, f'-{(ratio["c"].iloc[-1]-ratio["c"].iloc[-2]).round(2)}(-{(100*(ratio["c"].iloc[-1]-ratio["c"].iloc[-2])/ratio["c"].iloc[-1]).round(2)}%)', ratio['h'].iloc[-1].round(2), ratio['l'].iloc[-1].round(2)

@app.callback(
        [Output('vencimento', 'options'),
         Output('vencimento', 'value')],
        Input('symbol', 'value')
)

def venc(symbol):
    ven = vencimentos(symbol)
    return ven[0], ven[1]

@app.callback(
    Output('table-container', 'children'),
    [Input('symbol', 'value'),
     Input('vencimento', 'value')]
)

def input_stickers(symbol, vencimento):
    df = stickers(symbol, vencimento)
    table = [
            dash_table.DataTable(id='table-paging',
                                 page_size=10,
                                 columns =[{'name': 'Ticker', 'id': 'ticker'},
                                           {'name': 'Tipo', 'id': 'tipo'}, 
                                           {'name': 'Modelo', 'id': 'modelo'}, 
                                           {'name': 'Modelo Opç.', 'id': 'modelo de Opções'}, 
                                           {'name': 'Strike  ', 'id': 'strike'},   
                                           {'name': 'Preço', 'id': 'preco'}
                                           ],
                                 data=df.to_dict('records'),
                                 style_table={'width':'400px', 'margin':'0', 'backgroundColor':'#000','color':'#fff', 'border-radius':'10px'},
                                 style_cell={'textAlign': 'center', 'backgroundColor': '#000', 'color': '#fff'},
    style_header={'backgroundColor': 'grey', 'fontWeight': 'bold'}
    )]
        
    return table

if __name__ == '__main__':
    app.run_server(debug=True)