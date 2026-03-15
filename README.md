# Black-Scholes-Merton Options Pricing Engine

A complete options analytics tool built in Python,
tested on live NSE Nifty options data.

## Features
- BSM call and put pricing
- Complete Greeks (Delta, Gamma, Theta, Vega, Rho)
- Options chain builder with Pandas
- Interactive visualizations with Plotly
- Implied volatility solver using Brent's method
- Real NSE data integration
- Volatility smile and skew analysis
- BSM mispricing analysis vs live market prices

## Project Structure
- `bsm.py` — Core BSM pricing engine
- `greeks.py` — Options Greeks calculator
- `analysis.py` — Options chain builder
- `visualize.py` — Interactive Plotly charts
- `implied_vol.py` — IV solver using scipy Brent's method
- `fetch_data.py` — NSE data integration and mispricing analysis

## Libraries Required
pip install pandas numpy scipy plotly

## How to Get NSE Data
1. Go to nseindia.com/option-chain
2. Select NIFTY and choose your expiry date
3. Click Download to get the CSV
4. Move CSV to your project folder
5. Update the filename in fetch_data.py

## Key Results
- Successfully computed implied volatility for 100+ Nifty strikes using Brent's numerical method — results within 0.5% of NSE's
  own IV calculations
- Reproduced the Nifty volatility skew from live market data — OTM puts command significantly higher IV than OTM calls, reflecting
  institutional demand for crash protection
- Demonstrated BSM's core limitation — by using constant ATM volatility, BSM underprices OTM puts by up to ₹100 and overprices OTM calls
  directly proving the model's constant volatility assumption breaks down in real markets
