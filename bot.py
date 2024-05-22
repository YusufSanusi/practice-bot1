# define asset
    # IN: keyboard
    # OUT: string

#LOOP until timeout reached (ex. 2h)
#POINT ECHO: INITIAL CHECK
# check the position: ask broker/API if we have an open position with "asset"
    # IN: asset (string)
    # OUT: True (exists) / False (does not exist)

# check if tradable: ask broker/API if "asset" is tradable
    # IN: asset (string)
    # OUT: True (exists) / False (does not exist)

#GENERAL TREND
# load 30 min candles: demand the API 30 min candles or go back to beginning
    # IN: asset (for whatever the API needs), time range*, candle size*
    # OUT: 30 min candles (OHLC for every candle)

# perform general trend analysis: detect interesting trend (UP / DOWN / NO TREND)
    # IN: 30 min candles data (Close data)
    # OUTput: UP / DOWN / NO TREND (string)
    #If no trend defined, go back to POINT ECHO

#LOOP until timeout reached (ex. 30min)
# POINT DELTA
    # STEP 1: load 5 min candles
        # IN: asset (for whatever the API needs), time range*, candle size*
        # OUT: 5 min candles (OHLC for every candle)
        # If failed go back to POINT DELTA

    # STEP 2: perform instant trend analysis: confirm the trend detected by GT analysis
        # IN: 5 min candles data (Close date), output of the GT analysis (Up / Down string)
        # OUT: True (confirmed) / False (not confirmed)
        # If failed go back to POINT DELTA

    # STEP 3: perform RSI analysis
        # IN: 5 min candles data (Close date), output of the GT analysis (Up / Down string)
        # OUT: True (confirmed) / False (not confirmed)
        # If failed go back to POINT DELTA

    # STEP 4: perform stochastic analysis
        # IN: 5 min candles data (OHLC date), output of the GT analysis (Up / Down string)
        # OUT: True (confirmed) / False (not confirmed)
        # If failed go back to POINT DELTA

#SUBMIT ORDER
# submit order (limit order): interact with broker API
    # IN: number of shares, asset, desired price
    # OUT: True (confirmed) / False (not confirmed), position ID
    # If False, abort / go back to POINT ECHO

# check position: see if position exists
    # IN: position ID
    # OUT: True (confirmed) / False (not confirmed)
    # If False, abort / go back to POINT ECHO

#LOOP until timeout reached (ex. ~8h)
#ENTER POSITION MODE: check the conditions in parallel
# IF check take profit -> close position
    # IN: current gains (earning $)
    # OUT: True / False

# ELIF check stop loss -> close position
    # IN: current gains (losing $)
    # OUT: True / False

# ELIF check stoch crossing -> close position
    # STEP 1: pull 5 minutes OHLC data.
        # IN: asset
        # OUT: OHLC data (5 min candles)

    # STEP 2: check stochastic curves crossing
        # IN: OHLC data (5 min candles)
        # OUT: True / False

#GET OUT
#SUBMIT ORDER
# submit order (market): interact with broker API
    # IN: number of shares, asset, position ID
    # OUT: True (confirmed) / False (not confirmed)
    # If False, retry until True

# check position: see if position exists
    # IN: position ID
    # OUT: True (still exists!) / False (does not exist)
    # If False, abort / go back to SUBMIT ORDER

# wait 15 min

# end
