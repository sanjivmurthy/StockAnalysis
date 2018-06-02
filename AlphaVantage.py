from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.cryptocurrencies import CryptoCurrencies
from pprint import pprint
import matplotlib.pyplot as plt

ts = TimeSeries(key='361NZHAPWQW945GZ', output_format='pandas')
data, meta_data = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='full')
pprint(data['timestamp'])
# data['4. close'].plot()
# plt.title('Intraday Times Series for the MSFT stock (1 min)')

# cc = CryptoCurrencies(key='361NZHAPWQW945GZ', output_format='pandas')
# data, meta_data = cc.get_digital_currency_intraday(symbol='BTC', market='CNY')
# data['1b. price (USD)'].plot()
# plt.tight_layout()
# plt.title('Intraday value for bitcoin (BTC)')
# plt.grid()


# plt.show()