import pandas as pd
from datetime import datetime
from update_data import *
from utils import flatten_dict_to_df, update_portfolio

atr_file = 'atr.xlsx'
hldings_file = "Current_holdings.xlsx"
trdng_log_file = "Trading_Log.xlsx"

def buy_stck(tcker, price, qty,df_trading_log):
    '''

    '''
    current_date = datetime.now().strftime("%Y-%b-%d")
    if 'Order_id' not in df_trading_log.columns or df_trading_log.empty:
        next_order_id = 1
    else:
        next_order_id = df_trading_log['Order_id'].max() +1
    new_row = pd.DataFrame(
        {
            'Order_id': next_order_id,
            'Date': [current_date],
            'Ticker': [tcker],
            'Price' : [price],
            'Qty': [qty],
            'Total':[round(price*qty,2)],
            'Action': ["Buy"],
            "P/L" : [None]
        }
    )
    df_trading_log = pd.concat([df_trading_log,new_row],ignore_index=True)
    row_4_cur_hlding = pd.DataFrame(
        {
            'Order_id': next_order_id,
            'Ticker': [tcker],
            'Price' : [price],
            'Qty': [qty]
        }
    )
    
    curr_hlding_file = pd.read_excel(hldings_file)
    curr_hlding_file = pd.concat([curr_hlding_file,row_4_cur_hlding],ignore_index=True)
    
    return df_trading_log,curr_hlding_file

def sell_stck(tcker, price, qty,df_trading_log):
    '''
    
    '''
    current_date = datetime.now().strftime("%Y-%b-%d")

    PnL= 0 
    df_hlding = pd.read_excel(hldings_file)
    hldings = df_to_dict(df_hlding)
    qty_left = qty

    while qty_left > 0 and len(hldings[tcker]) != 0:
        hand_qty = hldings[tcker][0]['qty']
        if hand_qty < qty_left:
            PnL+= hldings[tcker][0]['qty'] * (price - hldings[tcker][0]['price'])
            qty_left-= hand_qty
            hldings[tcker][0]['qty'] = 0 
        else:
            PnL+=  ((price *qty) - 
                    (hldings[tcker][0]['price'] * qty))
            hldings[tcker][0]['qty']-=qty_left
            qty_left= 0

        if hldings[tcker][0]['qty'] ==0:
            hldings[tcker].pop(0)
    df_hlding = flatten_dict_to_df (hldings)
    df_hlding.to_excel(hldings_file, index = False)
    next_order_id = df_trading_log['Order_id'].max() +1
    new_row = pd.DataFrame(
        {
            'Order_id': next_order_id,
            'Date': [current_date],
            'Ticker': [tcker],
            'Price' : [price],
            'Qty': [qty],
            'Total':[round(price*qty,2)],
            'Action': ["Sell"],
            "P/L" : [PnL]})
    print ("Sold for a profit of $ {}".format(round(PnL,2)))
    df_trading_log = pd.concat([df_trading_log,new_row], ignore_index= True)
    return df_trading_log, df_hlding

    

