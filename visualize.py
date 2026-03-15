
import numpy as np 
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from bsm import Call_price, Put_price
from greeks import delta, gamma, rho, vega, theta

# Common Parameters 
X     = 100
r     = 0.05
T     = 1
Sigma = 0.2

# Range of Stock Prices 
SP_range = np.linspace(60,140,200)


# Plot 1: Option Price VS Stock Price
def plot_option_prices():
    #Building a dataframe 
    data = {
        'Stock Price' : SP_range,
        'Call Price'  : [Call_price(i, X, r, T, Sigma) for i in SP_range],
        'Put Price'   : [Put_price(i, X, r, T, Sigma)  for i in SP_range]
    }
    df = pd.DataFrame(data)
    
    #Building the graph
    fig = px.line(
        df, 
        x='Stock Price',
        y=['Call Price', 'Put Price'],
        title = 'BSM option prices VS Stock Prices',
        labels ={'variable': 'Option Type', 'value' : 'Option Price'},
        color_discrete_map= {'Call Price':'blue', 'Put Price':'red'}
    )

    #Adding the vertical line at the strike price 
    fig.add_vline(
        x = X,
        line_dash = 'dash',
        line_color = 'black',
        annotation_text = "Strike Price",
        annotation_position = 'top right'
    )
    fig.show()

#Plot 2: Greeks VS Stock Prices

def plot_greeks():
    #Building Dataframes for each greek
    deltas_c = [delta(i , X , r , T , Sigma , "call") for i in SP_range]
    deltas_p = [delta(i , X , r , T , Sigma , "put")  for i in SP_range]
    gammas  = [gamma(i , X , r , T , Sigma)                 for i in SP_range]
    vegas   = [vega(i , X , r , T , Sigma )                  for i in SP_range]
    thetas_c = [theta(i , X , r , T , Sigma , "call") for i in SP_range]
    thetas_p = [theta(i , X , r , T , Sigma , "put") for i in SP_range]
    rhos_c = [rho(S, X, r, T, Sigma, 'call') for S in SP_range]
    rhos_p = [rho(S, X, r, T, Sigma, 'put')  for S in SP_range]

    data = {
        "Stock Price" : SP_range,
        "Delta (C)"    : deltas_c,
        "Delta (P)"    : deltas_p,
        "Gamma"        : gammas,
        "Vega"         : vegas,
        "Theta (C)"    : thetas_c,
        "Theta (P)"    : thetas_p,
        'Rho (C)' : rhos_c,
        'Rho (P)' : rhos_p,
    }
    df = pd.DataFrame(data)

    # Delta plot 
    fig_delta = px.line(
        df,
        x= "Stock Price",
        y= ["Delta (C)", "Delta (P)"],
        title = "Delta VS Stock Price",
        labels= {'value' : "Delta", "variable" : "Option Type"},
        color_discrete_map= {"Delta (C)" : 'blue', "Delta (P)":"red"}
    )
    fig_delta.add_vline(
        x = X, 
        line_dash = "dash",
        line_color = "black",
        annotation_text = "Strike (X)",
        annotation_position = "top right"
    )
    fig_delta.show()

    # Gamma plot
    fig_gamma = px.line(
        df,
        x     = 'Stock Price',
        y     = 'Gamma',
        title = 'Gamma vs Stock Price',
        labels = {'Gamma': 'Gamma', 'Stock Price': 'Stock Price'},
        color_discrete_sequence = ['green']
    )
    fig_gamma.add_vline(
        x                   = X,
        line_dash           = 'dash',
        line_color          = 'black',
        annotation_text     = 'Strike (X)',
        annotation_position = 'top right'
    )
    fig_gamma.show()

    #Theta plot
    fig_theta = px.line(
        df,
        x = "Stock Price",
        y = ["Theta (C)", "Theta (P)"],
        title = "Theta VS Stock Price",
        labels = {"value": "Theta", "variable":"Option Type"},
        color_discrete_map = {'Theta (C)':'orange', "Theta (P)" : 'red'}
    )
    fig_theta.add_vline(
        x = X,
        line_dash = "dash",
        line_color = 'black',
        annotation_text = "Strike (X)",
        annotation_position = "top right"
    )
    fig_theta.show()

    #Vega plot
    fig_vega = px.line(
        df,
        x = "Stock Price",
        y = "Vega",
        title = 'Vega vs Stock Price',
        labels = {'Vega': 'Vega', 'Stock Price': 'Stock Price'},
        color_discrete_sequence = ['purple']
    )
    fig_vega.add_vline(
        x                   = X,
        line_dash           = 'dash',
        line_color          = 'black',
        annotation_text     = 'Strike (X)',
        annotation_position = 'top right'
    )
    fig_vega.show()
    
    #Rho plot 
    fig_rho = px.line(
        df,
        x="Stock Price",
        y=["Rho (C)", 'Rho (P)'],
        title = "Rho VS Stock Prices",
        labels = {"value": "Rho", "variable":"Option Type"},
        color_discrete_map = {'Rho(C)': 'blue', 'Rho(P)': 'red'}
    )
    fig_rho.add_vline(
        x = X,
        line_dash = "dash",
        line_color = "black",
        annotation_text = 'Strike (X)',
        annotation_position = "top right"
    )
    fig_rho.show()

#Plot 3: Option Price vs Time to Expiry
def plot_time_decay():
    # Range of time values from 0.1 years to 2 years
    T_range = np.linspace(0.1,2,200)
    S       = 100                   #(at the money option)

    # Computing option prices across time range
    call_prices = [Call_price(S, X, r, t, Sigma) for t in T_range]
    put_prices  = [Put_price(S, X, r, t, Sigma)  for t in T_range]

    # Building DataFrame
    df = pd.DataFrame({
        'Time to Expiry (Years)' : T_range,
        'Call Price'             : call_prices,
        'Put Price'              : put_prices
    })

    # Building the chart
    fig = px.line(
        df,
        x     = 'Time to Expiry (Years)',
        y     = ['Call Price', 'Put Price'],
        title = 'Option Price vs Time to Expiry (Time Decay)',
        labels = {'value': 'Option Price', 'variable': 'Option Type'},
        color_discrete_map = {'Call Price': 'blue', 'Put Price': 'red'}
    )
    # Add vertical line at T = 1 (our base case)
    fig.add_vline(
        x                   = 1,
        line_dash           = 'dash',
        line_color          = 'black',
        annotation_text     = 'T = 1 Year',
        annotation_position = 'top right'
    )

    fig.show()

# Plot 4: P&L Diagram at Expiry
def plot_pnl():
    # Premium paid upfront
    C = Call_price(100, X, r, T, Sigma)   # call premium
    P = Put_price(100, X, r, T, Sigma)    # put premium

    # P&L at expiry = intrinsic value - premium paid
    call_pnl = [max(S - X, 0) - C for S in SP_range]
    put_pnl  = [max(X - S, 0) - P for S in SP_range]

    # Building DataFrame
    df = pd.DataFrame({
        'Stock Price at Expiry' : SP_range,
        'Long Call P&L'         : call_pnl,
        'Long Put P&L'          : put_pnl
    })

    # Building the chart
    fig = px.line(
        df,
        x     = 'Stock Price at Expiry',
        y     = ['Long Call P&L', 'Long Put P&L'],
        title = 'P&L Diagram at Expiry',
        labels = {'value': 'Profit / Loss ($)', 'variable': 'Position'},
        color_discrete_map = {'Long Call P&L': 'blue', 'Long Put P&L': 'red'}
    )

    # Strike price line
    fig.add_vline(
        x                   = X,
        line_dash           = 'dash',
        line_color          = 'black',
        annotation_text     = 'Strike (X = 100)',
        annotation_position = 'top left'
    )

    # Breakeven line
    fig.add_hline(
        y                   = 0,
        line_dash           = 'dash',
        line_color          = 'gray',
        annotation_text     = 'Breakeven',
        annotation_position = 'bottom right'
    )

    fig.show()


if __name__ == "__main__":
    plot_option_prices()
    plot_greeks()
    plot_time_decay()
    plot_pnl()







    
