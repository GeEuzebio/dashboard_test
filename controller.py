import requests
from datetime import datetime, timedelta
import pandas as pd

def get_data(symbol):
    date = datetime.now()
    today = datetime(date.year, date.month, date.day).timestamp()
    url = f'https://ssltvc.forexprostools.com/8bb04f8932bd9c19558e67ec237d06bc/1695254447/1/1/8/history?symbol={symbol}&resolution=5&from={today}&to={today}'
    response = requests.get(url).json()
    df = pd.DataFrame(response, columns={'c':'close', 'o':'open', 'h':'high', 'l':'low', 'v':'volume'})
    df = df.round(4)
    return df

def get_ratio(symbol):
    end = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
    begin = end - timedelta(days=7)
    end = end.timestamp()
    begin = begin.timestamp()
    url = f'https://ssltvc.forexprostools.com/8bb04f8932bd9c19558e67ec237d06bc/1695254447/1/1/8/history?symbol={symbol}&resolution=D&from={begin}&to={end}' 
    response = requests.get(url).json()
    df = pd.DataFrame(response, columns={'c':'close', 'o':'open', 'h':'high', 'l':'low', 'v':'volume'})
    return df

def vencimentos(symbol):
    url = f'https://opcoes.net.br/listaopcoes/completa?idAcao={symbol}&listarVencimentos=True&cotacoes=true'
    r = requests.get(url).json()
    vencimentos = [i['value'] for i in r['data']['vencimentos']]
    return vencimentos, vencimentos[0]

def stickers(symbol, vencimento):
    url = f'https://opcoes.net.br/listaopcoes/completa?idAcao={symbol}&listarVencimentos=false&cotacoes=true&vencimentos={vencimento}'
    r = requests.get(url).json()
    l = [[symbol, vencimento, i[0].split('_')[0], i[2], i[3], i[4], i[5], i[8]] for i in r['data']['cotacoesOpcoes']]
    
    df = pd.DataFrame(l, columns=['ativo', 'vencimento', 'ticker', 'tipo', 'modelo', 'modelo de Opções', 'strike', 'preco'])
    df = df.sort_values('strike')
    df = df.reset_index(drop=True)
    return df