import json
import requests 
import websocket

from pybit import inverse_perpetual


# Введите искомую разницу цен в процентах 
Spread  =  0.1

# в объектах класса храню все цена на символы 
class Simbol:

    def __init__(self,name,price_huobi = None,
                 price_binance = None, price_bybit = None):
        
        self.name = name
        self.price_huobi  = price_huobi
        self.price_binance  = float(price_binance)
        self.price_bybit = price_bybit
        self.spread = Spread/100+1

    def append_Bybit(self,price):
        self.price_bybit  = float(price)

    def append_Binance(self,price):
        self.price_binance = float(price)

    def append_Huobi(self,price):
        self.price_huobi = float(price)

    # поиск разницы в курсе цена на криптовалюту (спрэда)
    def get_spread(self):
        if self.price_binance/self.price_bybit > self.spread or \
            self.price_bybit/self.price_binance > self.spread:
            print(f"{self.name} : Binance {self.price_binance} /" \
                f"Bybit {self.price_bybit} "\
                    f" spread : {self.price_binance/self.price_bybit} ")

        if self.price_binance/self.price_huobi > self.spread or \
            self.price_huobi/self.price_binance > self.spread:
            print(f"{self.name} : Binance {self.price_binance} /" \
                f"Huobi {self.price_bybit}  "\
                    f"spread : {self.price_binance/self.price_huobi} ")


# здесь будет словарь символов 
Simbols = {}
                
# список фиатов которые нам не нужны
fiats = ['GBP','KZT','UAH','EUR','TRY','RUB','BRL','VND']

# загрузка цен с хуоби 
def Load_Huobi():

    price_list = requests.get(
        'https://api.huobi.pro/market/tickers'
        ).json()
    
    for symbol in price_list["data"]:
        if  symbol['symbol'].upper() in Simbols:
            Simbols[symbol['symbol'].upper()].\
                append_Huobi(symbol['close'])
            
# загрузка цен с байбита 
def Load_Bybit():

    session_unauth = inverse_perpetual.HTTP(
        endpoint="https://api-testnet.bybit.com"
        )

    # скачиваем все пары юсдт 
    price_list = session_unauth.latest_information_for_symbol()

    # # парсим + заплоняем базу данных 
    for symbol in price_list["result"]:
        if symbol['symbol'].upper() in Simbols:
            Simbols[symbol['symbol'].upper()].\
                append_Bybit(symbol['last_price'])

# загрузка цен бинанса и поиск срэда  
def Load_Binance(message):
    data =  json.loads(message)
    for crypto_symbol in data:
        if 'USDT' in  crypto_symbol['s'].upper():
            if crypto_symbol['s'].upper() in Simbols:       
                Simbols[crypto_symbol['s'].upper()]\
                    .append_Binance(crypto_symbol['c'])
                Simbols[crypto_symbol['s'].upper()].get_spread()
            else:
                Simbols[crypto_symbol['s'].upper()] \
                    = Simbol(crypto_symbol['s'],
                             price_binance=crypto_symbol['c'])
            
                   

def on_message(ws, message):

    Load_Bybit()
    Load_Huobi() 
    Load_Binance(message)

def on_close(ws, close_status_code, close_msg):

    print(close_msg)
    print(close_status_code)
    print("### closed ###")



if __name__ == '__main__':
    
    ws = websocket.WebSocketApp(
    "wss://stream.binance.com:9443/ws/!ticker@arr",
    on_message=on_message,
    on_close=on_close)

    ws.run_forever() 