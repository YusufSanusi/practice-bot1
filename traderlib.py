# encoding: utf-8
#import alpaca_trade_api as tradeapi

import sys, time, os, pytz
import numpy as np
import tulipy as ti
import pandas as pd

import gvars

from logger import *
# from bot_functions import *
from datetime import datetime
from math import ceil

class Trader:
    def __init__(self, ticker):
        log.info('Trader initialized with ticker %s' % ticker)
        self.ticker = ticker

    # # check if tradable: ask broker/API if "asset" is tradable
    def is_tradable(self, ticker):
            # IN: ticker (string)
            # OUT: True (tradable) / False (not tradable)
            try:
                # asset = get asset from API
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

    # load stock data from API:
        # IN: ticker, interval, enteries limit
        # OUT: array with stock data (OHCL)

    # get open positions
    def get_open_positions(self, assetId):
        # IN: assetId
        # OUT: boolean (True = already open, False = not open)
        #positions = ask API
        for position in positions:
            if position.symbol == assetId:
                return True
            else:
                return False

    # submit order: gets our order through the API (retry)
        # IN: order data (number of shares, order type)
        # OUT: boolean (True = order successful / False = order failed)

    # cancel order: cancels our order (retry)
        # IN: order ID
        # OUT: boolean (True = order cancelled / False = order not cancelled)

    # check position whether it exists or not
    def check_position(self, ticker, doNotWait=False):
        # IN: ticker
        # OUT: boolean (True = already open, False = not open)
        attempt = 1

        while attempt <= gvars.check_position_max_attempts:
            try:
                #position = ask API
                current_price = position.current_price
                log.info('The position was found. Current price is: %.2f' % current_price)
                return True
            except:
                if doNotWait:
                    log.info('Position not found, this is good!')
                    return False

                log.info('Position not found, retrying...')
                time.sleep(5) # wait 5 secs and retry
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
            #total_equity = ask API

            # calculate the number of shares
            shares_quantity = int(gvars.max_spent_equity / asset_price)

            log.info('Total shares to operate: %d' % shares_quantity)

            return shares_quantity
        
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
                #position = ask API
                current_price = position.current_price
                log.info('The current price is: %.2f' % current_price)
                return current_price
            except:
                log.info('Position not found, retrying...')
                time.sleep(5) # wait 5 secs and retry
                attempt += 1

        log.error('Position not found for %s, moving on.' % ticker)
        return None

    # get general trend: detect interesting trend (long / short / False if NO TREND)
    def get_general_trend(self, ticker):
        # IN: 30 min candles data (Close data)
        # OUTput: LONG / SHORT / NO TREND (string)

        log.info('GENERAL TREND ANALYSIS commencing')

        attempt = 1

        try:
            while True:
                #data = ask 30 min stock data

                # calculate the EMAs
                ema9 = ti.ema(data, 9)
                ema26 = ti.ema(data, 26)
                ema50 = ti.ema(data, 50)

                log.info('%s general trend EMAs = [%.2f, %.2f, %.2f]' % (ticker, ema9, ema26, ema50))

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

                #data = ask 5 min stock data

                # calculate the EMAs
                ema9 = ti.ema(data, 9)
                ema26 = ti.ema(data, 26)
                ema50 = ti.ema(data, 50)

                log.info('%s instant trend EMAs = [%.2f, %.2f, %.2f]' % (ticker, ema9, ema26, ema50))

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

                #data = ask 5 min stock data

                # calculate the RSI
                rsi = ti.rsi(data, 14) # uses 14-sample-window

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
            log.error(str(e))
            sys.exit()

    # get stochastic: perform STOCHASTIC analysis
    def get_stochastic(self, ticker, trend):
        # IN: ticker, trend
        # OUT: True (confirmed) / False (not confirmed)

        log.info('STOCHASTIC ANALYSIS commencing')

        attempt = 1
        

        try:
            while True:

                #data = ask 5 min stock data

                # calculate the STOCHASTIC
                stoch_k, stoch_d = ti.stoch(high, low, close, 9, 6, 9)

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

        #data = ask 5 min data

        # get stochastic values
        stoch_k, stoch_d = ti.stoch(high, low, close, 9, 6, 9)

        log.info('%s stochastic = [%.2f, %.2f]' % (ticker, stoch_k, stoch_d))

        try:
            if (trend == 'long') and (stoch_k <= stoch_d):
                log.info('Stochastic curves crossed: %s, k=%.2f, d=%.2f' % (trend, stoch_k, stoch_d))
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

        #entry_price = ask the API

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
                if not self.get_instatnt_trend(self.ticker, self.trend):
                    log.info('The instant trend is not confirmed. Going back.')
                    continue # If failed go back to POINT DELTA

                if not self.get_rsi(self.ticker, self.trend):
                    log.info('The RSI is not confirmed. Going back.')
                    continue # If failed go back to POINT DELTA

                if not self.get_stochastic(self.ticker, self.trend):
                    log.info('The Stochastic analysis is not confirmed. Going back.')
                    continue # If failed go back to POINT DELTA

                log.info('All criteria have been met for trade. Procceding with trade.')
                break

            # get the current price
            self.current_price = self.get_current_price(self.ticker)

            # decide the total amount to invest
            shares_quantity = self.get_shares_amount(self.current_price)

            # submit order (limit)
            #submit_order(params)

            # check position: see if position exists
            if not self.check_position(self.ticker):
                # cancel pending order
                continue # go back to POINT ECHO

            # ENTER POSITION MODE
            successful_operation = self.enter_position_mode(self.ticker, self.trend)
                # If any return true get out

            #GET OUT: loop until succeed
            while True:
                # submit order (market)

                # check position is cleared
                if not self.check_position(self.ticker, doNotWait=True):
                    break

                time.sleep(10) # wait 10 secs

            # end of execution
            return successful_operation
