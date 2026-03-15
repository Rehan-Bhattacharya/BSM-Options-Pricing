
import numpy as np 
from scipy.stats import norm 
from bsm import d1,d2

def delta(S , X , r , T , Sigma , option_type = 'call'):
    '''
    Delta measures the sensitivity of option price w.r.t to the change in stock price
    Call Delta : Between 0 & 1
    Put  Delta : Between -1 & 0
    '''
    D1 = d1(S , X , r , T , Sigma)
    D2 = d2(S , X , r , T , Sigma)
    if option_type == "call":
        return norm.cdf(D1)
    else: 
        return -norm.cdf(-D1)

def gamma(S , X , r , T , Sigma):
    '''
    Gamma measures rate of change of delta 
    Same for both Call and Put options. 
    '''
    D1 = d1(S , X , r , T , Sigma)
    D2 = d2(S , X , r , T , Sigma)
    return(norm.pdf(D1) / (S * Sigma * np.sqrt(T)))

def theta(S , X , r , T , Sigma , option_type = 'call'):
    '''
    Theta measures sensitivity of the option price w.r.t time decay 
    Expressed as change per calender day 
    '''
    D1 = d1(S , X , r , T , Sigma )
    D2 = d2(S , X , r , T , Sigma )
    common = -(S * norm.pdf(D1) * Sigma) / (2 * np.sqrt(T))
    if option_type == 'call':
        return((common - r * X * np.exp(-r * T) * norm.cdf(D2)) / 365)
    else:
        return((common + r * X * np.exp(-r * T) * norm.cdf(-D2)) / 365)

def vega(S , X , r , T , Sigma):
    '''
    Vega measures sensitivity of the option price w.r.t the volatility.
    Expressed as per 1% change in volatility
    Same for both call and put options.
    '''
    D1 = d1(S , X , r , T , Sigma )
    D2 = d2(S , X , r , T , Sigma )
    return(S * norm.pdf(D1) * np.sqrt(T) / 100)

def rho(S , X , r , T , Sigma , option_type = 'call'):
    '''
    Measures the sensitivity of option price w.r.t change in interest rate.
    Expressed as per 1% change in rate
    '''
    D1 = d1(S , X , r , T , Sigma )
    D2 = d2(S , X , r , T , Sigma )
    if option_type == 'call':
        return(X * T * np.exp(-r * T) * norm.cdf(D2) / 100)
    else:
        return(-X * T * np.exp(-r * T) * norm.cdf(-D2) / 100)
    

#Quick Test 
if __name__ == "__main__":
    S     = 100
    X     = 100
    r     = 0.05
    T     = 1
    Sigma = 0.2 

    print("=" * 40)
    print(f"{'GREEKS SUMMARY':^40}")
    print("=" * 40)
    print(f"{'Greek':<10} {'Call':>10} {'Put':>10}")
    print("-" * 40)
    print(f"{'Delta':<10} {delta(S , X , r , T , Sigma , option_type='call'):>10,.4f} {delta(S , X , r , T , Sigma , option_type='put'):>10,.4f}")
    print(f"{'gamma':<10} {gamma(S , X , r , T , Sigma):>10,.4f} {gamma(S , X , r , T , Sigma):>10,.4f}")
    print(f"{'Theta':<10} {theta(S,X,r,T,Sigma,option_type ='call'):>10.4f} {theta(S,X,r,T,Sigma,option_type='put'):>10.4f}")
    print(f"{'Vega':<10} {vega(S,X,r,T,Sigma):>10.4f} {vega(S,X,r,T,Sigma):>10.4f}")
    print(f"{'Rho':<10} {rho(S,X,r,T,Sigma,option_type='call'):>10.4f} {rho(S,X,r,T,Sigma,option_type='put'):>10.4f}")
    print("=" * 40)


    


