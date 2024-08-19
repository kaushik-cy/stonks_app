import streamlit as st
import stonkslab as sl
import stonksplot as sp
from datetime import datetime, timedelta

st.set_page_config(layout = 'wide')

st.title('Stonkslab')

c00, c01, c02 = st.columns(3)
with c00:
	ticker = st.text_input('Ticker', value = "^GSPC")

with c01:
	date_from = st.date_input('From', value = datetime.now() - timedelta(weeks = 8))

with c02:
	date_to = st.date_input('To', value = datetime.now())

date_start = date_from - timedelta(weeks = 54)
d0 = datetime(year = date_start.year, month = date_start.month, day = date_start.day)
d1 = datetime(year = date_from.year, month = date_from.month, day = date_from.day)
d2 = datetime(year = date_to.year, month = date_to.month, day = date_to.day)

if(ticker != '' and d1 <= datetime.now() and d2 <= datetime.now()):
	s = sl.download_data(ticker, d0, d2)
	si = sl.all_indicators(s)
	si_userDates = si[si.index >= d1].copy()
	days = len(si_userDates.index)

	st.markdown("### Data Table")
	st.write(si_userDates)

	if(days > 1):
		c10, c11 = st.columns(2)

		with c10:
			st.markdown("### Change")
			st.write(sp.plot_change(si, days = days))

		with c11:
			st.markdown("### MA Difference")
			st.write(sp.plot_MA(si, days = days))

		with c10:
			st.markdown("### MACD")
			st.write(sp.plot_MACD(si, days = days))

		with c11:
			st.markdown("### RSI")
			st.write(sp.plot_RSI(si, days = days))

		with c10:
			st.markdown("### ADX")
			st.write(sp.plot_ADX(si, days = days))

		with c11:
			st.markdown("### CCI")
			st.write(sp.plot_CCI(si, days = days))

		with c10:
			st.markdown("### CMF")
			st.write(sp.plot_CMF(si, days = days))

		with c11:
			st.markdown("### Stochastic Oscillator")
			st.write(sp.plot_stochastic_oscillator(si, days = days))

		with c10:
			st.markdown("### Bollinger Bands")
			st.write(sp.plot_bollinger_bands(si, days = days))

		with c11:
			st.markdown("### Ichimoku Cloud")
			st.write(sp.plot_ichimoku_cloud(si, days = days))
