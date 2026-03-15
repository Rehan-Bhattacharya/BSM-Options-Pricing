
import pandas as pd
import numpy as np
from datetime import datetime

def load_nse_options(filepath):
    '''
    This function loads and cleans NSE options chain CSV file
    Returns a clean dataframe with call and put data
    '''
    
    df_raw = pd.read_csv(   
        filepath,                                
        skiprows=1,
        header = 0
    )
    
    df_raw.columns = df_raw.columns.str.strip().str.replace('\n', '', regex=False)                   #stripping white space in the column names  
      
    columns = list(df_raw.columns)                                                   
    
    #LTP and IV appear twice in the column names
    ltp_positions = []
    
    for i, col in enumerate(columns):
        if col == 'LTP':
            ltp_positions.append(i)
    
    iv_positions = []

    for i, col in enumerate(columns):
        if col == "IV":
            iv_positions.append(i)

    #Renaming first occurance as call and second as put 
    df_raw = df_raw.rename(columns={
        'LTP'    : 'LTP_Call',
        'LTP.1'  : 'LTP_Put',
        "IV"     : 'IV_Call',
        'IV.1'   : "IV_Put",
        'STRIKE' : 'STRIKE'
    })

    df = df_raw[['STRIKE', 'LTP_Call', 'LTP_Put', 'IV_Call', 'IV_Put']].copy()

    for col in ['STRIKE', 'LTP_Call', 'LTP_Put', 'IV_Call', 'IV_Put']:                #Removing commas from numbers 
        df[col] = df[col].astype(str).str.replace(',', '', regex=False)

    df.replace('-', np.nan, inplace=True)                                             # Replace '-' with NaN (no trades)
 
    for col in ['STRIKE', 'LTP_Call', 'LTP_Put', 'IV_Call', 'IV_Put']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(subset=['STRIKE'], inplace=True)                                        #Dropping rows with missing strike or both LTPs missing
    df = df[df['LTP_Call'].notna() | df['LTP_Put'].notna()]

    df.set_index('STRIKE', inplace=True)
    df.sort_index(inplace=True)

    return df   

# Part 2: Computing Implied Volatility for every Strike Price

from implied_vol import implied_volatility
import warnings
warnings.filterwarnings('ignore')

def compute_iv_chain(df, S, r, T):
    """
    Computes implied volatility for every strike using real NSE market prices.
    Compares our BSM IV against NSE's own IV.
    
    Parameters:
        df : cleaned options chain DataFrame from load_nse_options()
        S  : current spot price (Nifty level)
        r  : risk free rate (use current Indian T-bill rate)
        T  : time to expiry in years
    """
    df = df[(df.index >= S * 0.80) & (df.index <= S * 1.20)] 

    our_iv_call = []
    our_iv_put  = []

    for strike in df.index:
        
        ltp_call = df.loc[strike, 'LTP_Call']
        if pd.notna(ltp_call) and ltp_call > 0:
            iv = implied_volatility(ltp_call, S, strike, r, T, 'call')
            our_iv_call.append(round(iv * 100, 2) if iv else None)
        else:
            our_iv_call.append(None)

        ltp_put = df.loc[strike, 'LTP_Put']
        if pd.notna(ltp_put) and ltp_put > 0:
            iv = implied_volatility(ltp_put, S, strike, r, T, 'put')
            our_iv_put.append(round(iv * 100, 2) if iv else None)
        else:
            our_iv_put.append(None)

    # Adding our IV columns to the DataFrame
    df['Our_IV_Call'] = our_iv_call
    df['Our_IV_Put']  = our_iv_put

    return df

# Part 3: PLotting the IV smile

def plot_iv_smile(df, S):
    """
    Plots the implied volatility smile using real NSE data.
    Shows IV across strikes for both calls and puts.
    """
    import plotly.express as px
    import plotly.graph_objects as go

    # Filtering valid IV rows 
    df_call = df[df['Our_IV_Call'].notna()][['Our_IV_Call']].copy()
    df_put  = df[df['Our_IV_Put'].notna()][['Our_IV_Put']].copy()

    df_call = df_call[(df_call.index >= S * 0.90) & (df_call.index <= S * 1.10)]
    df_put  = df_put[(df_put.index  >= S * 0.90) & (df_put.index  <= S * 1.10)]

    df_call = df_call[(df_call['Our_IV_Call'] >= 5) & (df_call['Our_IV_Call'] <= 35)]
    df_put  = df_put[(df_put['Our_IV_Put']   >= 5) & (df_put['Our_IV_Put']   <= 35)]

    df_call = df_call[['Our_IV_Call']].copy()
    df_put  = df_put[['Our_IV_Put']].copy()

    # Adding option type column 
    df_call['Option Type'] = 'Call'
    df_put['Option Type']  = 'Put'

    # Renaming IV columns to same name for concat 
    df_call = df_call.rename(columns={'Our_IV_Call': 'Implied Volatility %'})
    df_put  = df_put.rename(columns={'Our_IV_Put':  'Implied Volatility %'})

    # Reseting index to make Strike a regular column 
    df_call = df_call.reset_index()
    df_put  = df_put.reset_index()

    # Combining both DataFrames 
    df_combined = pd.concat([df_call, df_put], ignore_index=True)

    # Building the chart
    fig = px.line(
        df_combined,
        x     = 'STRIKE',
        y     = 'Implied Volatility %',
        color = 'Option Type',
        title = 'Implied Volatility Smile — Nifty Options (June 2026)',
        labels = {
            'STRIKE'               : 'Strike Price',
            'Implied Volatility %' : 'Implied Volatility (%)',
            'Option Type'          : 'Option Type'
        },
        color_discrete_map = {'Call': 'blue', 'Put': 'red'}
    )

    # Adding vertical line at spot price 
    fig.add_vline(
        x                   = S,
        line_dash           = 'dash',
        line_color          = 'black',
        annotation_text     = f'Spot ({S})',
        annotation_position = 'top right'
    )

    # Adding NSE's own IV for comparison 
    df_nse_call = df[df['IV_Call'].notna()].copy()
    df_nse_put  = df[df['IV_Put'].notna()].copy()

    # REPLACE the old filter lines with these
    df_nse_call = df_nse_call[
        (df_nse_call.index >= S * 0.90) &
        (df_nse_call.index <= S * 1.10)
    ].reset_index()

    df_nse_put = df_nse_put[
        (df_nse_put.index >= S * 0.90) &
        (df_nse_put.index <= S * 1.10)
    ].reset_index()

    fig.add_scatter(
        x    = df_nse_call['STRIKE'],
        y    = df_nse_call['IV_Call'],
        mode = 'lines',
        name = 'NSE IV Call',
        line = dict(color='lightblue', dash='dot')
    )

    fig.add_scatter(
        x    = df_nse_put['STRIKE'],
        y    = df_nse_put['IV_Put'],
        mode = 'lines',
        name = 'NSE IV Put',
        line = dict(color='pink', dash='dot')
    )

    fig.show()


# Part 4

def bsm_mispricing_analysis(df, S, r, T):
    """
    Compares BSM theoretical prices against real NSE market prices.
    Shows where BSM under and overprices options.
    """
    import plotly.express as px
    import plotly.graph_objects as go
    from bsm import Call_price, Put_price

    # Filtering to liquid strikes around ATM 
    df = df[(df.index >= S * 0.95) & (df.index <= S * 1.05)].copy()

    df = df[df['Our_IV_Call'].isna() | ((df['Our_IV_Call'] >= 5) & (df['Our_IV_Call'] <= 35))]
    df = df[df['Our_IV_Put'].isna()  | ((df['Our_IV_Put']  >= 5) & (df['Our_IV_Put']))]

    # Using ATM IV as constant volatility for BSM
    # Finding IV at closest strike to spot
    atm_strike = min(df.index, key=lambda x: abs(x - S))
    atm_iv     = df.loc[atm_strike, 'Our_IV_Call']
    if atm_iv is None or pd.isna(atm_iv):
        atm_iv = df.loc[atm_strike, 'Our_IV_Put']
    atm_iv = atm_iv / 100   # convert from % to decimal

    # Computing BSM theoretical prices for each strike 
    bsm_call_prices = []
    bsm_put_prices  = []

    for strike in df.index:
        bsm_call = Call_price(S, strike, r, T, atm_iv)
        bsm_put  = Put_price(S, strike, r, T, atm_iv)
        bsm_call_prices.append(round(bsm_call, 2))
        bsm_put_prices.append(round(bsm_put, 2))

    df['BSM_Call'] = bsm_call_prices
    df['BSM_Put']  = bsm_put_prices

    # Computing mispricing 
    # Mispricing = Market Price - BSM Price
    # Positive → Market more expensive than BSM (BSM underprices)
    # Negative → Market cheaper than BSM (BSM overprices)
    df['Mispricing_Call'] = df['LTP_Call'] - df['BSM_Call']
    df['Mispricing_Put']  = df['LTP_Put']  - df['BSM_Put']

    print(f"ATM Strike : {atm_strike}")
    print(f"ATM IV     : {atm_iv * 100:.2f}%")
    print("\nFull mispricing table:")
    print(df[['LTP_Call', 'BSM_Call', 'Mispricing_Call',
          'LTP_Put',  'BSM_Put',  'Mispricing_Put']].to_string())
    
    # Printing mispricing table
    print("\nBSM MISPRICING ANALYSIS")
    print("=" * 80)
    print(df[['LTP_Call', 'BSM_Call', 'Mispricing_Call',
              'LTP_Put',  'BSM_Put',  'Mispricing_Put']].to_string())
    print("=" * 80)

    # Plot 1: BSM vs Market Price 
    fig1 = go.Figure()

    # Call prices
    fig1.add_scatter(
        x    = df.index,
        y    = df['LTP_Call'],
        mode = 'lines',
        name = 'Market Call Price',
        line = dict(color='blue')
    )
    fig1.add_scatter(
        x    = df.index,
        y    = df['BSM_Call'],
        mode = 'lines',
        name = 'BSM Call Price',
        line = dict(color='lightblue', dash='dot')
    )

    # Put prices
    fig1.add_scatter(
        x    = df.index,
        y    = df['LTP_Put'],
        mode = 'lines',
        name = 'Market Put Price',
        line = dict(color='red')
    )
    fig1.add_scatter(
        x    = df.index,
        y    = df['BSM_Put'],
        mode = 'lines',
        name = 'BSM Put Price',
        line = dict(color='pink', dash='dot')
    )

    # Spot line
    fig1.add_vline(
        x                   = S,
        line_dash           = 'dash',
        line_color          = 'black',
        annotation_text     = f'Spot ({S})',
        annotation_position = 'top right'
    )

    fig1.update_layout(
        title  = 'BSM Theoretical Price vs NSE Market Price',
        xaxis_title = 'Strike Price',
        yaxis_title = 'Option Price (₹)'
    )
    fig1.show()

    # Plot 2: Mispricing across strikes 
    df_misprice = df[['Mispricing_Call', 'Mispricing_Put']].dropna().reset_index()

    fig2 = px.line(
        df_misprice,
        x     = 'STRIKE',
        y     = ['Mispricing_Call', 'Mispricing_Put'],
        title = 'BSM Mispricing — Market Price minus BSM Price',
        labels = {
            'value'    : 'Mispricing (₹)',
            'variable' : 'Option Type',
            'STRIKE'   : 'Strike Price'
        },
        color_discrete_map = {
            'Mispricing_Call': 'blue',
            'Mispricing_Put' : 'red'
        }
    )

    # Zero line — no mispricing
    fig2.add_hline(
        y                   = 0,
        line_dash           = 'dash',
        line_color          = 'black',
        annotation_text     = 'No Mispricing',
        annotation_position = 'bottom right'
    )

    fig2.add_vline(
        x                   = S,
        line_dash           = 'dash',
        line_color          = 'gray',
        annotation_text     = f'Spot ({S})',
        annotation_position = 'top right'
    )

    fig2.show()

# Quick Test
if __name__ == "__main__":
    df = load_nse_options('option-chain-ED-NIFTY-30-Mar-2026.csv')

    # Temporarily just print the raw data
    print(f"Total strikes: {len(df)}")
    print(f"\nAll strikes with LTP_Call:")
    print(df[df['LTP_Call'].notna()][['LTP_Call', 'LTP_Put']].to_string())

    # Step 2 — Define market parameters
    S = 24450.45    # Nifty spot price from earlier
    r = 0.0668      # Current Indian 91-day T-bill rate (6.68%)
    
    # Time to expiry — calculate from today to expiry date
    expiry = datetime(2026, 3, 30)    # from your filename!
    today  = datetime.today()
    T      = (expiry - today).days / 365

    print(f"Spot Price : {S}")
    print(f"Risk Free  : {r * 100:.2f}%")
    print(f"Time to Expiry: {T:.4f} years ({(expiry-today).days} days)")

    # Step 3 — Compute IV
    print("\nComputing implied volatilities...")
    df = compute_iv_chain(df, S, r, T)

    # Step 4 — Show results
    print("\nIV COMPARISON — OUR BSM vs NSE")
    print("=" * 75)
    print(df[['LTP_Call', 'IV_Call', 'Our_IV_Call',
              'LTP_Put',  'IV_Put',  'Our_IV_Put']].to_string())
    print("=" * 75)

    # Part 3 — Plot IV Smile
    plot_iv_smile(df, S)
    print("\nCall IV values:")
    print(df[['Our_IV_Call']].dropna().to_string())

    # Part 4 
    bsm_mispricing_analysis(df, S, r, T)





    

