import yfinance as yf
import pandas as pd
import numpy as np
import math
from atr_calcs import *
from utils import *

## this has all the functions that will fetch data from yfinance 
## anything that will use yfinance to get price is here. 
## or anything that is updating

def get_ltp(tcker):
    '''
    get_ltp: Str -> Float
    '''
    tcker = str(tcker).upper()
    ticker = yf.Ticker(tcker)
    data = ticker.history(period="7d", interval="1m")
    latest_price = data["Close"].iloc[-1]
    return round(latest_price,2)

def change_base_price(tcker, new_bp, df):
    '''
    Returns None and Mutates the df by changing the base price of tcker to 
        new_bp
        
    change_base_price: Str Float DataFrame -> None
    
    Effects:
        Mutates
        Prints to screen 
    
    '''
    
    x = df['Ticker'].tolist().index(tcker)
    df.at[x,"Base_Price"] = new_bp
    print("Base price for {0} changed to {1}".format(tcker, new_bp))



## db functions

def is_base_price_updated(df):
    '''
    Returns True if all the LL < current_price < UL name of the ticker(s)
        otherwise
    
    is_base_price_updated: DataFrame -> (Anyof True Str)
    
    '''
    to_be_updated = []
    for idx ,row in df.iterrows():
        if (row['Current_Price'] >= row['UL'] or
            row['Current_Price'] <= row['LL']):
            to_be_updated.append(row['Ticker'])
    
    if len(to_be_updated) == 0:
        print('All Values are up-to date.')
        return None
    for tcker in to_be_updated: print (tcker)
    return None



def update_ltp(df):
    '''
    Updates LTT price of the stocks.
    
    update_base_price: DataFrame -> None
    
    Effects:
        Mutates df
    
    '''
    ## after running this func check if any curr prices are more than UL
    for idx ,row in df.iterrows():
        new_p = get_ltp(row["Ticker"])
        df.at[idx, 'Current_Price'] = new_p
        print("Price for {0} updated to : ${1}".format(row["Ticker"], new_p))
    print("All prices updated.")
    return None

def update_base_price(df):
    '''
    Updated the base price of the stocks that have reached the UL
        and print the ones that have.
    
    update_base_price: DataFrame -> None
    
    Effects:
        Mutates df
    
    '''
    for idx ,row in df.iterrows():
        if row['Current_Price'] >= row["UL"]: # shifting to next window 
            new_base = row["UL"]
            df.at[idx, 'Base_Price'] = new_base
            df.at[idx, 'LL'] = calc_stop(new_base, row['ATR'])
            df.at[idx, 'UL'] = calc_target(new_base, row['ATR'])
            print("Base Price updated for {}".format(row['Ticker']))
       
def update_ul_ll(df):
    '''
    Returns None and mutates the df by updating  the LL and UL 
    '''
    for idx ,row in df.iterrows(): # making sure the LL and UL are correct
        df.at[idx, 'LL'] = calc_stop(row['Base_Price'], row['ATR'])
        df.at[idx, 'UL'] = calc_target(row['Base_Price'], row['ATR'])
        print("UL and LL updated for {}".format(row['Ticker']))

def  update_atr(df):
    ''' 
    '''
    for idx ,row in df.iterrows():
        df.at[idx,"ATR"] = get_atr(row["Ticker"])

def add_tcker(df,tcker,base_price):
    '''
    
    '''
    if tcker in df["Ticker"].tolist():
        print("{} already in ATR")
        change_base_price(tcker,base_price,df)
        return df

    atr = get_atr(tcker)
    new_row = pd.DataFrame(
        {
            "Ticker": [tcker],
            "Base_Price": [base_price],
            'Current_Price': [get_ltp(tcker)],
            'ATR': [atr],
            'LL': [calc_stop(base_price, atr)],
            'UL': [calc_target(base_price, atr)]
        }
    )
    df = pd.concat([df, new_row], ignore_index= True)
    return df
    