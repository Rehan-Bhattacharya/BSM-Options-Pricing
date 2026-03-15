
import pandas as pd
import numpy as np 
from bsm import Call_price, Put_price
from greeks import delta, gamma, rho, theta, vega

def options_chain(S , strikes , r , T , Sigma):
    '''
    Builds a complete options chain dataframe across a series of strike prices
    S       : Current stock price
    Strikes : List or array of strike prices
    r       : Risk free rate
    T       : Time to expiry (in years)
    Sigma   : Volatility
    '''
    
    rows = []                   #creating an empty row list to store each row.

    for X in strikes:                                                                              
        row = { 
            'Strike'     : X,
            'Call Price' :  round(Call_price(S , X , r , T , Sigma), 4),
            'Put Price ' :  round(Put_price(S , X , r , T , Sigma), 4),
            'Delta (C)'  :  round(delta(S , X , r , T , Sigma , option_type= 'Call'), 4),
            'Delta (P)'  :  round(delta(S , X , r , T , Sigma , option_type= 'Put'), 4),
            'Gamma'      :  round(gamma(S , X , r , T , Sigma), 4),
            'Vega'       :  round(vega(S , X , r , T , Sigma), 4),
            'Rho (C)'    :  round(rho(S , X , r , T , Sigma , option_type= 'Call'), 4),
            'Rho(P)'    : round(rho(S, X, r, T, Sigma, 'Put'), 4),
            'Theta(C)'  : round(theta(S, X, r, T, Sigma, 'Call'), 4),
            'Theta(P)'  : round(theta(S, X, r, T, Sigma, 'Put'), 4)
        }
        rows.append(row)

    df = pd.DataFrame(rows)                       # Converting list of dictionaries into a DataFrame
    df.set_index('Strike', inplace=True)
    return df 


# Quick Test 
if __name__ == '__main__':
    S     = 100
    r     = 0.05
    T     = 1
    Sigma = 0.2

    strikes = np.arange(80, 125, 5)               # Strike prices from 80 to 120 in steps of 5

    chain = options_chain(S , strikes , r , T , Sigma)

    print("\nOPTIONS CHAIN")
    print("=" * 90)
    print(chain.to_string())
    print("=" * 90)







