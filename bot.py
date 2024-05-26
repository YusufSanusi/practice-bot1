# encoding: utf-8

# import needed libraries
from traderlib import *
from logger import *
import sys
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

# from alpaca_trade_api.rest import REST

import gvars

# Load environment variables from .env file
load_dotenv()

apca_api_base_url = os.getenv('APCA_API_BASE_URL')
apca_api_key_id = os.getenv('APCA_API_KEY_ID')
apca_api_secret_key = os.getenv('APCA_API_SECRET_KEY')


# check trading account
def check_account_status(api):
    try:
        account = api.get_account()
        if account.status != 'ACTIVE':
            log.error('The account is not active, aborting')
            sys.exit()
    except Exception as e:
        log.error('Could not get account info, aborting')
        log.error(str(e))
        sys.exit()


# close current orders
def close_open_orders(api):
    '''
    open_orders = api.list_orders(
        status='open',
        limit=100,
        nested=True  # show nested multi-leg orders
    )
    if not open_orders:
        log.info('No open orders')
    else:
        log.info('List of open orders')
        log.info(open_orders)
        log.info('Cancelling all open orders')
        api.cancel_all_orders()


    # for order in open_orders:
    #     #close order
    #     log.info('Order %s closed' % str(order.id))

    log.info('All pending orders closed')
    '''

    log.info('Cancelling all open orders')
    
    try:
        api.cancel_all_orders()
        log.info('All pending orders cancelled')
    except Exception as e:
        log.error('Could not cancel orders')
        log.error(e)



# define asset
def get_ticker():
    # enter ticker with the keyboard
    ticker = input('Enter desired asset ticker: ')
    return ticker


# execute trading bot
def main():
    api = tradeapi.REST(apca_api_key_id, apca_api_secret_key)

    # initialize the logger
    initialize_logger()

    # check trading account
    check_account_status(api)

    # close current orders
    close_open_orders(api)

    # # define asset
    # ticker = get_ticker()
    #
    # trader = Trader(ticker)  # initialize trading bot
    # trading_successful = trader.run()  # run trading bot
    # # IN: string (ticker)
    # # OUT: boolean (True = success, False = failure)
    #
    # if not trading_successful:
    #     log.info('Trading was not successful, locking asset')
    #     # wait some time


if __name__ == '__main__':
    main()
