# encoding: utf-8
#import alpaca_trade_api as tradeapi

import sys, time, os, pytz
import numpy as np
import tulipy as ti
import pandas as pd
import yfinance as yf


import gvars

from logger import *
# from bot_functions import *
from datetime import datetime
from math import ceil

class Trader:
    # constructor
    def __init__(self, api, ticker):
        log.info('Trader initialized with ticker %s' % ticker)
        self.ticker = ticker
        self.api = api

    # get start time clock
    def get_time_now(self):
        try:
            clock = self.api.get_clock()
            now = datetime.fromisoformat(str(clock.timestamp)).timestamp()
            return now
        except Exception as e:
            log.error('Error getting current time')
            log.error(e)
            sys.exit()

    # get next market close time clock
    def end_of_day(self):
        try:
            clock = self.api.get_clock()
            next_market_close_time = datetime.fromisoformat(str(clock.next_close)).timestamp()
            return next_market_close_time - 600
        except Exception as e:
            log.error('Error getting next market close time')
            log.error(e)
            sys.exit()

    # difference in minutes
    def difference_in_minutes(self, start_time, minutes):
    
        try:
            clock = self.api.get_clock()
            now = datetime.fromisoformat(str(clock.timestamp)).timestamp()
            # next_close = datetime.fromisoformat(str(clock.next_close)).timestamp()

            difference = now - start_time

            difference_minutes = difference / 60

            return difference_minutes <= minutes
        except Exception as e:
            log.error('Something went wrong getting the difference in minutes')
            log.error(e)
            sys.exit()

    # check if tradable: ask broker/API if "asset" is tradable
    def is_tradable(self, ticker):
            # IN: ticker (string)
            # OUT: True (tradable) / False (not tradable)
            try:
                asset = self.api.get_asset(ticker)
                if asset.tradable:
                    log.info('The asset %s is tradable' % ticker)
                    return True
                else:
                    log.info('The asset %s is not tradable at the moment' % ticker)
                    return False
            except Exception as e:
                log.error('The API did not answer as expected')
                log.error(str(e))
                return False

    # set stoploss: takes a price as input and sets stoploss
    def set_stop_loss(self, entry_price, trend):
        # IN: entry price, trend(long/short)
        # OUT: stop loss

        try:
            if trend == 'long':
                # eg. 10 - (10*0.05) = 9.5 for 5% margin
                stop_loss = entry_price - (entry_price * gvars.stop_loss_margin)
                log.info('Stop loss set for %s at %.2f' % (trend, stop_loss))
                return stop_loss
            elif trend == 'short':
                # eg. 10 + (10*0.05) = 10.5 for 5% margin
                stop_loss = entry_price + (entry_price * gvars.stop_loss_margin)
                log.info('Stop loss set for %s at %.2f' % (trend, stop_loss))
                return stop_loss
            else:
                raise ValueError
        except Exception as e:
            log.error('The trend is not clear: %s' % str(trend))
            sys.exit()

    # set take profit: takes a price as input and sets take profit
    def set_take_profit(self, entry_price, trend):
        # IN: entry price, trend(long/short)
        # OUT: take profit

        try:
            if trend == 'long':
                # eg. 10 + (10*0.05) = 10.5 for 5% margin
                take_profit = entry_price - (entry_price * gvars.take_profit_margin)
                log.info('Take profit set for %s at %.2f' % (trend, take_profit))
                return take_profit
            elif trend == 'short':
                # eg. 10 - (10*0.05) = 9.5 for 5% margin
                take_profit = entry_price + (entry_price * gvars.take_profit_margin)
                log.info('Take profit set for %s at %.2f' % (trend, take_profit))
                return take_profit
            else:
                raise ValueError
        except Exception as e:
            log.error('The trend is not clear: %s' % str(trend))
            sys.exit()

    # get open positions
    def get_open_positions(self, ticker):
        # IN: ticker
        # OUT: boolean (True = already open, False = not open)
        positions = self.api.list_positions()
        if positions:
            for position in positions:
                if position.symbol == ticker:
                    return True
                else:
                    return False
        else:
            return False

    # submit order: gets our order through the API (retry)
    def submit_order(self, type, trend, ticker, shares_quantity, current_price, exit=False):
        # IN: order data (number of shares, order type)
        # OUT: boolean (True = order successful / False = order failed)

        log.info('Submitting %s order for %s' % (trend, ticker))

        match trend:
            case 'long':
                if not exit:
                    side = 'buy'
                    limit_price = round(current_price + (current_price * gvars.max_var), 2)
                elif exit:
                    side = 'sell'
            case 'short':
                if not exit:
                    side = 'sell'
                    limit_price = round(current_price - (current_price * gvars.max_var), 2)
                elif exit:
                    side = 'buy'
            case _:
                log.error('Trend was not understood')
                sys.exit()

        try:

            if type == 'limit':
                log.info('Current price: %.2f // Limit price: %.2f' % (current_price, limit_price))
                order = self.api.submit_order(
                    symbol=ticker,
                    qty=shares_quantity,
                    side=side,
                    type=type,
                    time_in_force='gtc',
                    limit_price=limit_price
                )

            elif type == 'market':
                log.info('Current price: %.2f' % current_price)
                order = self.api.submit_order(
                    symbol=ticker,
                    qty=shares_quantity,
                    side=side,
                    type=type,
                    time_in_force='gtc'
                )

            else:
                log.error('Type of order was not understood')
                sys.exit()

            self.order_id = order.id

            log.info('%s order submitted correctly!' % trend)
            log.info('%d shares %s for %s' % (shares_quantity, side, ticker))
            log.info('Order ID: %s' % self.order_id)
            return True

        except Exception as e:
            log.error('Something happened when submitting order')
            log.error(e)
            return False

    # cancel order: cancels our order (retry)
    def cancel_pending_order(self, ticker):
        # IN: order ID
        # OUT: boolean (True = order cancelled / False = order not cancelled)

        attempt = 1

        log.info('Cancelling %s order %s' % (ticker, self.order_id))

        while attempt <= gvars.cancel_pending_order_max_attempts:
            try:
                self.api.cancel_order(self.order_id)
                log.info('%s order %s successfully cancelled' % (ticker, self.order_id))
                return True
            except:
                log.info('Cancelling order failed, retrying...')
                time.sleep(5)
                attempt += 1
            
            log.error('Something went wrong when cancelling order. cancelling all pending orders just to be safe.')
            log.info('Order ID: %s' % self.order_id)
            self.api.cancel_all_orders()
            sys.exit()

    # check position whether it exists or not
    def check_position(self, ticker, doNotWait=False):
        # IN: ticker
        # OUT: boolean (True = already open, False = not open)
        attempt = 1

        while attempt <= gvars.check_position_max_attempts:
            try:
                position = self.api.get_position(ticker)
                current_price = position.current_price
                
                log.info('The position was found. Current price is: %.2f' % current_price)
                self.position = position
                return True
            except:
                if doNotWait:
                    log.info('Position not found, this is good!')
                    return False

                log.info('Position not found, retrying...')
                time.sleep(10) # wait 5 secs and retry
                attempt += 1

        log.info('Position not found for %s, moving on.' % ticker)
        return False

    # get total equity
    def get_shares_amount(self, asset_price):
        # works out the number of shares I want to buy
        # IN: asset price
        # OUT: number of shares

        log.info('Getting shares amount')

        try:
            # get the total equity available
            account = self.api.get_account()
            equity = float(account.equity)

            # calculate the number of shares
            shares_quantity = int(gvars.max_spent_equity / asset_price)

            if equity - (shares_quantity * asset_price) >= 0:
                log.info('Total shares to operate: %d' % shares_quantity)
                return shares_quantity
            else:
                log.info('Cannot spend that amount, remaining equity is %.2f' % equity)
                sys.exit()
        
        except Exception as e:
            log.error('Error at get shares amount')
            log.error(str(e))
            sys.exit()

    # get current price of an asset
    def get_current_price(self, ticker):
        # IN: ticker
        # OUT: current price ($)
        attempt = 1

        while attempt <= gvars.get_shares_amount_max_attempts:
            try:
                data = self.fetch_historical_data(ticker, '1m', '1d')
                close = data.Close.values
                current_price = round(float(close[-1]),2)
                return current_price

            except:
                log.info('Position not found, retrying...')
                time.sleep(5) # wait 5 secs and retry
                attempt += 1

        log.error('Position not found for %s, moving on.' % ticker)
        return None

    # load stock data from API:
    def fetch_historical_data(self, ticker, interval, period):
        # load historical stock data
        # IN : ticker, interval
        # OUT : stock data (OHLC)

        try:
            asset = yf.Ticker(ticker)
            data = asset.history(period, interval)
            return data

        except Exception as e:
            log.error('Something went wrong while fetching historical data')
            log.error(e)
            sys.exit()

    # get general trend: detect interesting trend (long / short / False if NO TREND)
    def get_general_trend(self, ticker):
        # IN: 30 min candles data (Close data)
        # OUTput: LONG / SHORT / NO TREND (string)

        log.info('GENERAL TREND ANALYSIS commencing')

        attempt = 1

        try:
            while True:
                
                data = self.fetch_historical_data(ticker, '30m', '5d')
                close = data.Close.values

                # calculate the EMAs
                ema9 = ti.ema(close, 9)[-1]
                ema26 = ti.ema(close, 26)[-1]
                ema50 = ti.ema(close, 50)[-1]

                log.info('%s general trend EMAs = [EMA9: %.2f, EMA26: %.2f, EMA50: %.2f]' % (ticker, ema9, ema26, ema50))

                # checking EMAs relative position
                if (ema50 > ema26) and (ema26 > ema9):
                    log.info('Trend detected for %s: long' %ticker)
                    return 'long'
                elif (ema50 < ema26) and (ema26 < ema9):
                    log.info('Trend detected for %s: short' % ticker)
                    return 'short'
                elif attempt <= gvars.get_general_trend_max_attempts:
                    log.info('Trend not clear for %s, waiting...' % ticker)
                    attempt += 1
                    time.sleep(60*10) # sleep 10 minutes
                else:
                    log.info('No trend detected for %s' % ticker)
                    return 'no trend'
                
        except Exception as e:
            log.error('Something went wrong at get general trend')
            log.error(str(e))
            sys.exit()

    # get instant trend: confirm the trend detected by GT analysis
    def get_instant_trend(self, ticker, trend):
        # IN: ticker, trend(long / short)
        # OUT: True (confirmed) / False (not confirmed)

        log.info('INSTANT TREND ANALYSIS commencing')

        attempt = 1

        try:
            while True:

                data = self.fetch_historical_data(ticker, '5m', '1d')
                close = data.Close.values

                # calculate the EMAs
                ema9 = ti.ema(close, 9)[-1]
                ema26 = ti.ema(close, 26)[-1]
                ema50 = ti.ema(close, 50)[-1]

                log.info('%s instant trend EMAs = [EMA9: %.2f, EMA26: %.2f, EMA50: %.2f]' % (ticker, ema9, ema26, ema50))

                if (trend == 'long') and (ema9 > ema26) and (ema26 > ema50):
                    log.info('Long trend confirmed for %s' % ticker)
                    return True
                elif (trend == 'short') and (ema9 < ema26) and (ema26 < ema50):
                    log.info('Short trend confirmed for %s' % ticker)
                    return True
                elif attempt <= gvars.get_instant_trend_max_attempts:
                    log.info('Trend not clear for %s, waiting...' % ticker)
                    attempt += 1
                    time.sleep(50) # sleep 50 secs
                else:
                    return False
                
        except Exception as e:
            log.error('Something went wrong at get initial trend')
            log.error(str(e))
            sys.exit()

    # get rsi: perform RSI analysis
    def get_rsi(self, ticker, trend):
        # IN: ticker, trend
        # OUT: True (confirmed) / False (not confirmed)

        log.info('RSI ANALYSIS commencing')

        attempt = 1

        try:
            while True:

                data = self.fetch_historical_data(ticker, '5m', '5d')
                close = data.Close.values

                # calculate the RSI
                rsi = ti.rsi(close, 14)[-1] # uses 14-sample-window

                log.info('%s rsi = [%.2f]' % (ticker, rsi))

                if (trend == 'long') and (rsi > 50) and (rsi < 80):
                    log.info('Long trend confirmed for %s' % ticker)
                    return True
                elif (trend == 'short') and (rsi < 50) and (rsi > 20):
                    log.info('Short trend confirmed for %s' % ticker)
                    return True
                elif attempt <= gvars.get_rsi_max_attempts:
                    log.info('Trend not clear for %s, waiting...' % ticker)
                    attempt += 1
                    time.sleep(20) # sleep 20 secs
                else:
                    return False
                
        except Exception as e:
            log.error('Something went wrong at rsi analysis')
            log.error(e)
            sys.exit()

    # get stochastic: perform STOCHASTIC analysis
    def get_stochastic(self, ticker, trend):
        # IN: ticker, trend
        # OUT: True (confirmed) / False (not confirmed)

        log.info('STOCHASTIC ANALYSIS commencing')

        attempt = 1
        

        try:
            while True:

                data = self.fetch_historical_data(ticker, '5m', '5d')
                high = data.High.values
                low = data.Low.values
                close = data.Close.values

                # calculate the STOCHASTIC
                stoch_k, stoch_d = ti.stoch(high, low, close, 9, 6, 9)
                stoch_k = stoch_k[-1]
                stoch_d = stoch_d[-1]

                log.info('%s stochastic = [%.2f, %.2f]' % (ticker, stoch_k, stoch_d))

                if (trend == 'long') and (stoch_k > stoch_d) and (stoch_k < 80) and (stoch_d < 80):
                    log.info('Long trend confirmed for %s' % ticker)
                    return True
                elif (trend == 'short') and (stoch_k < stoch_d) and (stoch_k > 20) and (stoch_d > 20):
                    log.info('Short trend confirmed for %s' % ticker)
                    return True
                elif attempt <= gvars.get_stochastic_max_attempts:
                    log.info('Trend not clear for %s, waiting...' % ticker)
                    attempt += 1
                    time.sleep(10) # sleep 10 secs
                else:
                    return False
                
        except Exception as e:
            log.error('Something went wrong at stochastic analysis')
            log.error(str(e))
            sys.exit()

    # check stochastic crossing
    def check_stochastic_crossing(self, ticker, trend):
        # IN: ticker, trend
        # OUT: True (if crossed) / False (if not crossed)

        log.info('Checking stochastic crossing...')

        data = self.fetch_historical_data(ticker, '5m', '5d')
        high = data.High.values
        low = data.Low.values
        close = data.Close.values

        # get stochastic values
        stoch_k, stoch_d = ti.stoch(high, low, close, 9, 6, 9)
        stoch_k = stoch_k[-1]
        stoch_d = stoch_d[-1]

        log.info('%s stochastic = [%.2f, %.2f]' % (ticker, stoch_k, stoch_d))

        try:
            if (trend == 'long') and (stoch_k <= stoch_d):
                log.info('Stochastic curves crossed: %s, K_FAST=%.2f, D_SLOW=%.2f' % (trend, stoch_k, stoch_d))
                return True
            elif (trend == 'short') and (stoch_k >= stoch_d):
                log.info('Stochastic curves crossed: %s, k=%.2f, d=%.2f' % (trend, stoch_k, stoch_d))
                return True
            else:
                log.info('Stochastic curves not crossed')
                return False
            
        except Exception as e:
            log.error('Error at stochastic crossing check')
            log.error(str(e))
            return True

    # enter position mode: check the conditions in parallel
    def enter_position_mode(self, ticker, trend):

        # order = self.api.get_order(order_id)
        # position = self.api.get_position(ticker)
        entry_price = self.position.avg_entry_price

        # set the take profit
        take_profit = self.set_take_profit(entry_price, trend)

        # set the stop loss
        stop_loss = self.set_stop_loss(entry_price, trend)

        attempt = 1

        try:
            while True:
                # check if take profit met. If True -> close position
                    # IN: current gains (earning $)

                # long trend version
                current_price = self.get_current_price(ticker)
                
                if (trend == 'long') and (current_price >= take_profit):
                    log.info('Take profit met at %.2f, Current price is %.2f' % (take_profit, current_price))
                    return True
                
                # short trend version
                
                elif (trend == 'short') and (current_price <= take_profit):
                    log.info('Take profit met at %.2f, Current price is %.2f' % (take_profit, current_price))
                    return True

                # check stop loss. If True -> close position
                    # IN: current gains (losing $)

                # long trend version
                elif (trend == 'long') and (current_price <= stop_loss):
                    log.info('Stop loss met at %.2f, Current price is %.2f' % (stop_loss, current_price))
                    return False
                
                # short trend version
                elif (trend == 'short') and (current_price >= stop_loss):
                    log.info('Stop loss met at %.2f, Current price is %.2f' % (stop_loss, current_price))
                    return False

                # check stoch crossing. If True -> close position
                    # IN: OHLC data (5 min candles)
                
                elif self.check_stochastic_crossing(ticker, trend):
                    log.info('Curves crossed. Current price is %.2f' % current_price)
                    return True
                
                elif attempt <= gvars.enter_position_mode_max_attempts:
                    log.info('Waiting inside position, attempt #%d' % attempt)
                    log.info('%.2f <-- %.2f --> %.2f' % (stop_loss, current_price, take_profit))
                    time.sleep(60) # wait for 60 secs
                
                # we wait
                else:
                    log.info('Day is ending, closing open positions')
                    return False
        except Exception as e:
            log.error('Error at enter position function')
            log.error(str(e))
            return True

    def run(self):

        try:
            if self.is_tradable(self.ticker):
                #LOOP until timeout reached (ex. 2h)
        
                while True:
                    #POINT ECHO
                    # ask broker/API if we have an open position with "asset"
                    if self.check_position(self.ticker, doNotWait=True):
                        log.info('There is already an open position with that asset! Aborting...')
                        return False # aborting execution

                    # POINT DELTA
                    while True:

                        # find general trend
                        self.trend = self.get_general_trend(self.ticker)
                        if self.trend == 'no trend':
                            log.info('No general trend found for %s! Going out...' % self.ticker)
                            return False # aborting execution
                        
                        # confirm instant trend
                        if not self.get_instant_trend(self.ticker, self.trend):
                            log.info('The instant trend is not confirmed. Going back.')
                            continue # If failed go back to POINT DELTA

                        if not self.get_rsi(self.ticker, self.trend):
                            log.info('The RSI is not confirmed. Going back.')
                            continue # If failed go back to POINT DELTA

                        # if not self.get_stochastic(self.ticker, self.trend):
                        #     log.info('The Stochastic analysis is not confirmed. Going back.')
                        #     continue # If failed go back to POINT DELTA

                        log.info('All criteria have been met for trade. Procceding with trade.')
                        break

                    # get the current price
                    self.current_price = self.get_current_price(self.ticker)

                    # decide the total amount to invest
                    shares_quantity = self.get_shares_amount(self.current_price)

                    # submit order (limit)
                    submit_order = self.submit_order('limit', self.trend, self.ticker, shares_quantity, self.current_price, False)

                    # check position: see if position exists
                    if not self.check_position(self.ticker):
                        # cancel pending order
                        self.cancel_pending_order(self.ticker)
                        continue # go back to POINT ECHO

                    # ENTER POSITION MODE
                    successful_operation = self.enter_position_mode(self.ticker, self.order_id, self.trend)
                        # If any return true get out

                    #GET OUT: loop until succeed
                    while True:
                        # submit order (market)
                        self.submit_order('market', self.trend, self.ticker, shares_quantity, self.current_price, True)

                        # check position is cleared
                        if not self.check_position(self.ticker, doNotWait=True):
                            break

                        time.sleep(10) # wait 10 secs

                    # end of execution
                    return successful_operation
            else:
                log.info('Not tradable at the moment. exiting')
                sys.exit()
        except Exception as e:
            log.error('Error at is tradable check function')
            log.error(str(e))
            sys.exit()  
