import pandas as pd
import numpy as np
import yfinance as yf

MACD_W1 = 12
MACD_W2 = 26
RSI_WINDOW = 14
ADX_WINDOW = 14
CCI_WINDOW = 20
CCI_CONSTANT = 0.015
GDC_W1 = 50
GDC_W2 = 200
CMF_WINDOW = 21
SO_W1 = 14
SO_W2 = 3
BOL_W1 = 20
BOL_SD = 2
ICH_W1 = 9
ICH_W2 = 26
ICH_W3 = 52
ICH_W4 = 26

stock = 'SBIN.NS'
start_date = '2015-01-01'
end_date = '2024-08-18'

def download_data(stock, start_date, end_date):
	# print('Downloading data. Please be connected to your internet.')
	data = yf.download(stock, start_date, end_date)
	# print('Download complete.')
	return data


def all_indicators(stock_data):
	data = stock_data.copy()
	data['change'] = change(data)
	data['MA_' + str(GDC_W1)], data['MA_' + str(GDC_W2)], data['MA_Diff'] = MA(data)
	data['MACD'] = MACD(data)
	data['RSI'] = RSI(data)
	data['ADX'] = ADX(data)
	data['CCI'] = CCI(data)
	data['CMF'] = CMF(data)
	data['stochastic_osc_k'], data['stochastic_osc_d'] = stochastic_oscillator(data)
	data['bollinger_u'], data['bollinger_l'] = bollinger_bands(data)
	data['conversion'], data['base'], data['leading_span_A'], data['leading_span_B'], data['lagging_span'] = ichimoku_cloud(data)
	return data


def change(data):
	change = 100 * (data['Close'] - data['Close'].shift(1)) / data['Close']
	return change

def MA(data):
	ma_w1 = data['Close'].rolling(window = GDC_W1).mean()
	ma_w2 = data['Close'].rolling(window = GDC_W2).mean()
	ma_diff = ma_w1 - ma_w2
	return ma_w1, ma_w2, ma_diff

def MACD(data):
	ema_w1 = data['Close'].ewm(span = MACD_W1).mean()
	ema_w2 = data['Close'].ewm(span = MACD_W2).mean()
	macd = ema_w1 - ema_w2
	return macd

def RSI(data):
	diff = data['Close'].diff()
	diff_gain = diff.apply(lambda x: x if x > 0 else 0)
	diff_loss = diff.apply(lambda x: -x if x < 0 else 0)
	av_gain = diff_gain.rolling(window = RSI_WINDOW).mean()
	av_loss = diff_loss.rolling(window = RSI_WINDOW).mean()
	rs = av_gain/av_loss
	rsi = 100 - (100/(1 + rs))
	rsi = rsi.apply(lambda x: 100 if str(x) == 'inf' else x)
	return rsi

def ADX(data):
	x = data['High'] - data['Low']
	y = abs(data['High'] - data['Close'].shift(1))
	z = abs(data['Low'] - data['Close'].shift(1))
	tr = pd.DataFrame({'x': x, 'y': y, 'z': z}).max(axis = 1)
	atr = tr.rolling(window = ADX_WINDOW).mean()
	move_up = data['High'] - data['High'].shift(1)
	move_down = data['Low'].shift(1) - data['Low']
	d1 = pd.DataFrame({'up': move_up, 'dn': move_down})
	pdm_c1 = d1['up'] > d1['dn']
	pdm_c2 = d1['up'] > 0
	ndm_c1 = d1['dn'] > d1['up']
	ndm_c2 = d1['dn'] > 0
	pdm = (pdm_c1 & pdm_c2) * d1['up']
	ndm = (ndm_c1 & ndm_c2) * d1['dn']
	pdi = 100 * pdm.ewm(span = ADX_WINDOW).mean() / atr
	ndi = 100 * ndm.ewm(span = ADX_WINDOW).mean() / atr
	adx = (abs(pdi - ndi) / (pdi + ndi)).ewm(span = ADX_WINDOW).mean() * 100
	return adx

def CCI(data):
	tpt = (data['High'] + data['Low'] + data['Close'])/3
	tpt_sma = tpt.rolling(window = CCI_WINDOW).mean()
	md_t = np.array([])
	s = 0
	for n in range(CCI_WINDOW):
	    a = list(abs(tpt_sma - tpt.shift(n)))
	    md_t = np.append(md_t, a)
	md_t = md_t.reshape(CCI_WINDOW, len(tpt))
	md = np.mean(md_t.T, axis = 1)
	md = pd.Series(md, index = tpt.index)
	cci = (tpt - tpt_sma)/(CCI_CONSTANT * md)
	return cci

def CMF(data):
	mf_mul = ((data['Close'] - data['Low']) - (data['High'] - data['Close'])) / (data['High'] - data['Low'])
	mf_vol = mf_mul * data['Volume']
	mf_vol_sma = mf_vol.rolling(window = CMF_WINDOW).mean()
	vol_sma = data['Volume'].rolling(window = CMF_WINDOW).mean()
	cmf = mf_vol_sma / vol_sma
	return cmf

def stochastic_oscillator(data):
	l_14 = data['Low'].rolling(window = SO_W1).min()
	h_14 = data['High'].rolling(window = SO_W1).max()
	so_k = 100 * ((data['Close'] - l_14) / (h_14 - l_14))
	so_d = so_k.rolling(window = SO_W2).mean()
	return so_k, so_d

def bollinger_bands(data):
	tp = (data['High'] + data['Low'] + data['Close']) / 3
	tp_sma = tp.rolling(window = BOL_W1).mean()
	tp_std = tp.rolling(window = BOL_W1).std()
	bol_u = tp_sma + BOL_SD * tp_std
	bol_l = tp_sma - BOL_SD * tp_std
	return bol_u, bol_l

def ichimoku_cloud(data):
	h_1 = data['High'].rolling(window = ICH_W1).max()
	l_1 = data['Low'].rolling(window = ICH_W1).min()
	h_2 = data['High'].rolling(window = ICH_W2).max()
	l_2 = data['Low'].rolling(window = ICH_W2).min()
	h_3 = data['High'].rolling(window = ICH_W3).max()
	l_3 = data['Low'].rolling(window = ICH_W3).min()
	# tenkan-sen
	conversion = (h_1 + l_1) / 2
	# kijun-sen
	base = (h_2 + l_2) / 2
	# senkou span A
	leading_span_A = (conversion + base) / 2
	# senkou span B
	leading_span_B = (h_3 + l_3) / 2
	# chikou span
	lagging_span = data['Close'].shift(ICH_W4)
	return conversion, base, leading_span_A, leading_span_B, lagging_span
