import yfinance as yf
import pandas as pd
import numpy as np
import math

## List of functions in this file
##  1) get_stock_data: Takes a ticker symbol and returns a df of the stock and its price
##  2) flatten_dict_to_df: makes a dict to df. The Dict should look something like this
##      {tcker:[{'id': Nat, 'qty': Float, }]} 

my_period = "1y"

def get_stock_data(ticker_symbol,DATA_PERIOD=my_period):
    '''
    Fetches historical stock data using yfinance.
    
    get_stock_data: Str -> DataFrame
    
    '''
    
    print(f"Fetching data for {ticker_symbol}...")
    try:
        data = yf.download(
            ticker_symbol,
            period=DATA_PERIOD,
            auto_adjust=True, 
            progress=False 
        )

        if data.empty:
            print("Error: No Data for the ticker symbol: {}, Check the symbol".format(ticker_symbol))
            return None

        if isinstance(data.columns, pd.MultiIndex):
             print("\nFixing the columns")
             data.columns = [col[0] if isinstance(col, tuple) else col \
                             for col in data.columns.values]
      
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        data.columns = [str(col).capitalize() for col in data.columns] 

        if not all(col in data.columns for col in required_cols):
             print(f"Warning: Data for '{ticker_symbol}' does not contain all\
                standard columns ({required_cols}). Missing: {[col for col in required_cols if col not in data.columns]}.")
             
             if not all(col in data.columns for col in ['High', 'Low', 'Close']):
                 print("Error: Essential price columns (High, Low, Close) are missing after processing.")
                 return None

        if 'Volume' not in data.columns:
             data['Volume'] = 0

        return data.sort_index()

    except Exception as e:
        print(f"An error occurred while fetching data for {ticker_symbol}: {e}")
        
        return None
    
def flatten_dict_to_df(dic_hldings):
    '''
    flatten_dict_to_df: (Dictof Str (listof 
                                        (dict Str Nat 
                                              Str Float 
                                              Str Float)) -> df
    '''
    df = pd.DataFrame(
        {
            'Order_id':[],
            'Ticker': [],
            'Price' : [],
            'Qty': []
        }
    )
    for tcker in dic_hldings:
        for row in dic_hldings[tcker]:
            new_row = pd.DataFrame(
                {
                    'Order_id': [row['id']],
                    'Ticker': [tcker],
                    'Price' : [row['price']],
                    'Qty': [row['qty']]
                }
            )
            df = pd.concat([df,new_row])
    return df

def update_portfolio(dic_hldings):
    df = pd.DataFrame(
        {
            'Ticker': [],
            'Avg. Price': [],
            'Quantity': [],
            'Total_Book_Val': []
            
        }
    )
    for tcker in dic_hldings:
        total_cost_tcker = 0
        total_qty_tcker = 0
        for row in dic_hldings[tcker]:
            total_cost_tcker += (row['qty'] * row['price'])
            total_qty_tcker += row['qty']
        new_row = pd.DataFrame(
            {
                'Ticker': [tcker],
                'Avg. Price': [round(total_cost_tcker/total_qty_tcker,2)],
                'Quantity': [total_qty_tcker],
                'Total_Book_Val': [total_cost_tcker]
            }
        )
        df = pd.concat([df,new_row], ignore_index= True)
    return df

def df_to_dict(df):
    hldings = {}
    for idx, row in df.iterrows():
        if not(row["Ticker"] in hldings) :
            hldings[row["Ticker"]] =[]

        hldings[row["Ticker"]].append({'id': row["Order_id"],'qty': row["Qty"],'price': row['Price']})
    return hldings