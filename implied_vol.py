
# Part 1: Implied Volatility 

import numpy as np 
from scipy.optimize import brentq
from bsm import Call_price, Put_price

def implied_volatility(market_price, S , X , r, T , option_type = "call"):
    '''
    Calculating the implied volatility by finding the Sigma that makes 
    BSM model's option price equal to the observable market price.
    We are using Brent's method for numerical root finding.
    '''
    def objective(sigma):
        '''
        This is the function that we want to find the root of
        Root means : BSM model price - Market Price = 0 
        i.e finding the Sigma where BSM model price = Market Price
        '''
        if option_type.lower() == "call":
            return Call_price(S , X , r , T , sigma) - market_price
        else:
            return Put_price(S , X , r , T , sigma) - market_price
    try: 
        # Brent's method searches for sigma between 0.001 and 10 (0.1% to 1000% vol)
        iv = brentq(objective, 0.001, 20)                                                   #brentq is told:"Search for the root of objective(), but only look between sigma = 0.001 and sigma = 10". Brentq only accepts one agrument. 
        return iv
    except ValueError:
        return None
    

# Part 2: IV across option chains

import pandas as pd
from greeks import delta, gamma, theta, vega, rho

def iv_options_chain(S , r , T , strikes):
    '''
    Computing implied volatility for every strike price 
    Using BSM prices as synthetic market prices for now
    In phase 6 we will replace them with real market prices 
    
    The naming call_mkt is also intentional:
    call_price → the BSM function
    call_mkt → the "market price" we're simulating
    This distinction becomes very important in Phase 6 when call_mkt will be a real NSE market price fetched from live data, not a BSM computed price. The name already reflects that intent!
    '''
    rows = []

    for X in strikes:
        # Using BSM prices as synthetic market prices
        call_mkt = Call_price(S , X , r , T, 0.2)
        put_mkt  = Put_price(S , X , r , T, 0.2)

        # Now computing the implied volatility (iv) for call and put options
        iv_callprice = implied_volatility(call_mkt, S, X, r, T, 'call')
        iv_putprice  = implied_volatility(put_mkt,  S, X, r, T, 'put')

        row = {
            'Strike' : X,
            'Call Price' : round(call_mkt,4),
            'Put Price'  : round(put_mkt,4),
            'IV call'    : round(iv_callprice *100,4) if iv_callprice else None,
            'IV put'     : round(iv_putprice *100,4) if iv_callprice else None
        }

        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.set_index("Strike", inplace=True)
    return df


# Part 3: IV sensitivity analysis 

def iv_sensitivity(S , X , r , T , option_type = 'call'):
    '''
    Analysing how implied volatility changes as market price changes.
    Shows the relationship between option price and implied volatility.
    '''
    # For a call option = From slightly above 0 to deep ITM and vice versa for Put 
    if option_type.lower() == 'call':
        price_range = np.linspace(0.5 , S * 0.50 , 200)
    else: 
        price_range = np.linspace(0.5 , X * 0.50 , 200)
    
    ivs = []
    valid_price = []

    for i in price_range:
        iv = implied_volatility(i, S , X , r , T , option_type)
        if iv is not None:
            ivs.append(iv * 100)
            valid_price.append(i)
    
    df = pd.DataFrame({
        "Market Price" : valid_price,
        "Implied Volatility %" : ivs
    }
    )
    return df 


# Part 4: Implied Volatility (I.V) Visualization

import plotly.express as px

def plot_iv_sensitivity():
    '''
    Plotting implied volatility VS market prices for both call and put
    This is preview of the volatility smile that we build in Phase 6 
    '''

    df_call = iv_sensitivity( 100,100, 0.05, 1, 'call')
    df_put  = iv_sensitivity(100, 100, 0.05, 1, 'put')

    df_call["Option Type"] = "Call"
    df_put["Option Type"]  = "Put"

    df = pd.concat([df_call, df_put], ignore_index=True)

    # Build the Chart
    fig = px.line(
        df,
        x     = 'Market Price',
        y     = 'Implied Volatility %',
        color = 'Option Type',
        title = 'Implied Volatility vs Market Price',
        labels = {
            'Market Price'         : 'Option Market Price ($)',
            'Implied Volatility %' : 'Implied Volatility (%)',
            'Option Type'          : 'Option Type'
        },
        color_discrete_map = {'Call': 'blue', 'Put': 'red'}
    )

    # Add horizontal line at 20% — our base volatility
    fig.add_hline(
        y                   = 20,
        line_dash           = 'dash',
        line_color          = 'black',
        annotation_text     = 'Base Volatility (20%)',
        annotation_position = 'bottom right'
    )
    fig.show()

# Quick Test

if __name__ == "__main__":
    # Using our known BSM price from Phase 1 as the "market price"
    S     = 100
    X     = 100
    r     = 0.05
    T     = 1
    Sigma = 0.2   # true volatility

    # Phase 1 prices
    call_mkt = Call_price(S , X , r , T , Sigma)
    put_mkt = Put_price(S , X , r , T , Sigma)

    # Now calculating sigma from these prices 
    iv_callprice = implied_volatility(call_mkt, S , X , r , T , "call")
    iv_putprice  = implied_volatility(put_mkt, S , X , r , T , "put")

    print("=" * 45)
    print(f"{'IMPLIED VOLATILITY TEST':^45}")
    print("=" * 45)
    print(f"True Volatility    : {Sigma:.4f} (20.00%)")
    print(f"IV from Call Price : {iv_callprice:.4f} ({iv_callprice*100:.2f}%)")
    print(f"IV from Put Price  : {iv_putprice:.4f} ({iv_putprice*100:.2f}%)")
    print("=" * 45)

    # Sanity check
    if abs(iv_callprice - Sigma) < 0.0001:
        print("✓ Call IV matches true volatility!")
    if abs(iv_putprice - Sigma) < 0.0001:
        print("✓ Put IV matches true volatility!")
    
    # New — IV options chain
    print("\n")
    strikes = np.arange(80, 125, 5)
    chain   = iv_options_chain(S, r, T, strikes)
    print("IV OPTIONS CHAIN")
    print("=" * 50)
    print(chain.to_string())
    print("=" * 50)

    # Part 3 — IV Sensitivity Analysis
    print("\nIV SENSITIVITY ANALYSIS")
    print("=" * 45)

    df_call_sensitivity = iv_sensitivity(100, 100 , 0.05 , 1 , 'call')
    df_put_sensitivity  = iv_sensitivity(100, 100 , 0.05 , 1 , 'put')

    print("\nCall IV Sensitivity (sample):")
    print(df_call_sensitivity.iloc[::40].to_string())

    print("\nPut IV Sensitivity (sample):")
    print(df_put_sensitivity.iloc[::40].to_string())
    
    # Part 4 — IV Visualization
    plot_iv_sensitivity()








    



