import yfinance as yf
import pandas as pd
import numpy as np
import math
from utils import get_stock_data
ATR_PERIOD = 14 

def calculate_atr_ema(data_df, period=ATR_PERIOD):
    '''
    Calculates the Average True Range (ATR) using an Exponential Moving 
        Average (EMA) of True Range

    calculate_atr_ema: DataFrame Nat -> Float 
    
    '''
    if data_df is None or data_df.empty:
        print("Error: No data provided for ATR calculation.")
        return None

    if not all(col in data_df.columns for col in ['High', 'Low', 'Close']):
        print("Error: Data must contain 'High', 'Low', and 'Close' columns for ATR calculation.")
        return None

    if len(data_df) < period + 1:
        print(f"Error: Not enough data ({len(data_df)} bars) to calculate ATR for period {period} using EMA. Need at least {period + 1} bars.")
        return None
    try:
        # calc TR 
        high_low = data_df['High'] - data_df['Low']
        # shift to get prev close
        high_prev_close = np.abs(data_df['High'] - data_df['Close'].shift(1))
        low_prev_close = np.abs(data_df['Low'] - data_df['Close'].shift(1))

        true_range = pd.concat([high_low, high_prev_close, low_prev_close], axis=1).max(axis=1)

    
        atr_series = true_range.ewm(span=period, adjust=False).mean()
        valid_atrs = atr_series.dropna()

        if valid_atrs.empty:
             print(f"Error: ATR (EMA) calculation resulted in no valid values for period {period} after dropping NaNs.")
             return None

        latest_atr = valid_atrs.iloc[-1]
        if math.isnan(latest_atr) or latest_atr <= 0:
            positive_valid_atrs = valid_atrs[valid_atrs > 0]
            if not positive_valid_atrs.empty:
                latest_atr = positive_valid_atrs.iloc[-1]
                print(f"Warning: Latest ATR (EMA) ({valid_atrs.iloc[-1]:.4f})was invalid. Using last valid positive ATR: {latest_atr:.4f}")
            else:
                print("Error: No valid positive ATR values found in the data.")
                return None 
            
        
        return latest_atr

    except Exception as e:
        print(f"An error occurred during EMA ATR calculation: {e}")
        return None
    
def get_atr(tcker):
    '''
    Returns the ATR of the tcker
     (you enter the symbol and it will fetch you the atr)
    
    get_atr: Str -> Float
    
    '''
    tcker = tcker.upper()
    try:    
        name = yf.Ticker(tcker).info["longName"]
        print(name, "\n") 
    except Exception as e :
        return tcker
    else:
        return calculate_atr_ema(get_stock_data(tcker))

## stopp mult 2.0
## target mult 3.5
def calc_stop(base_price, atr_val, stop_mult=2.0):
    '''
    Calculate the stop price based on base_price, atr_val and stop_mult
    
    calc_stop: Float Float Float -> Float
    
    Requires:
        base_price > 0
        stop_mult > 0
    '''
   
    if (atr_val <= 0 or stop_mult <= 0 or base_price <= 0):
        return None

    stop_distance = atr_val * stop_mult
    calculated_stop_loss = base_price - stop_distance
    return round(calculated_stop_loss,2)

def calc_target(base_price, atr_val, target_mult = 3.50):
    '''
    Calculate the target price based on base_price, atr_val and target_mult
    
    calc_target: Float Float Float -> Float
    
    Requires:
        base_price > 0
        target_mult > 0
    
    '''
    if (atr_val <= 0 or target_mult <= 0 or base_price <= 0):
        return None
     
    target_distance = atr_val* target_mult
    calculated_target = base_price + target_distance
    return round(calculated_target,2)

def check_atr(atr):
    '''
    Checks the atr column and returns the atr if its a number
        else asks for alternate symbol 
        
    check_atr: Float -> Float
    
    Effects:
        Asks for user input 
    '''
    if isinstance(atr, float):
        print("Is a number")
        return atr
    else:
        print(atr)
        tcker = input("Enter the alt ticker symbol for {}:".format(atr))
        return get_atr(tcker)