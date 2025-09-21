from atr_calcs import *
from update_data import *
from order_book_func import * 
## stopp mult 2.0
## target mult 3.5

## main function

def close(df,name):
    df.to_excel(name, index=False)
    print(name, "Closed.")

if __name__ == "__main__":
    atr_file = 'atr.xlsx'
    hldings_file = "Current_holdings.xlsx"
    trdng_log_file = "Trading_Log.xlsx"
    prtfl_file = "Portfolio.xlsx"

    user_input = input("Enter command:").strip().lower()
    while user_input != 'exit': 

        df_atr =  pd.read_excel(atr_file)
        df_trading_log = pd.read_excel(trdng_log_file)
        df_cur_hlding = pd.read_excel(hldings_file)
        df_prfl = pd.read_excel(prtfl_file)


        if user_input in['update prices', 'update all price','update all ltp']:
            update_ltp(df_atr)
        elif user_input in['check base prices']:
            is_base_price_updated(df_atr)
        elif user_input in ['update base price']: ## shifts the window
            update_base_price(df_atr)
        elif user_input in ["fix upper limit", "fix lower limit"]:
            update_ul_ll(df_atr)
        elif "change base price of " in user_input:
            tcker = user_input.split[-1].capitalize()
            new_bp = input("What is the new Base price of {}".format(tcker))
            change_base_price(tcker, new_bp, df_atr)
        elif user_input in ["update atr"]:
            update_atr(df_atr)
        elif user_input[0:3] in ["buy"]:
            ## user_input format for buy
            ##  'buy {qty} {tcker} for {price}'
            lst_input = user_input.split(" ")
            tcker = lst_input[2].upper()
            price = float(lst_input[4])
            qty = float(lst_input[1])

            df_trading_log, df_cur_hlding =buy_stck(tcker,price, qty,df_trading_log)
            df_prfl = update_portfolio(df_to_dict(df_cur_hlding))
            df_prfl.to_excel(prtfl_file,index= False)
            df_trading_log.to_excel(trdng_log_file,index = False)
            df_cur_hlding.to_excel(hldings_file,index= False)

            avg_price = float(df_prfl[df_prfl['Ticker']== tcker]["Avg. Price"])
            df_atr = add_tcker(df_atr,tcker,avg_price).sort_values(by="Ticker")
        elif user_input[0:4] in ['sell']:
            lst_input = user_input.split(" ")
            tcker = lst_input[2].upper()
            price = float(lst_input[4])
            qty = float(lst_input[1])
            on_hand_qty = (df_prfl[df_prfl['Ticker']== tcker]['Quantity'][0])
            
            if on_hand_qty < qty:
                print ("You only have {0} for {1}, you can't sell more than that"
                       .format(on_hand_qty,tcker))
            else:
                df_trading_log, df_cur_hlding = sell_stck(tcker,price,qty,df_trading_log)
                df_prfl = update_portfolio(df_to_dict(df_cur_hlding))
                df_prfl.to_excel(prtfl_file,index= False)
                df_trading_log.to_excel(trdng_log_file,index = False)
                df_cur_hlding.to_excel(hldings_file,index= False)

        else:
            print("Please Enter a valid Command")

        close(df_atr,atr_file)
        user_input = input("Enter command:").strip().lower()
    print("Succesfully Exited")


