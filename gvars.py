# encoding: utf-8

# eg. 10 - (10*0.05) = 9.5 for 5% margin for long
# eg. 10 + (10*0.05) = 10.5 for 5% margin for short
stop_loss_margin = 0.05  # percentage margin

# eg. 10 + (10*0.05) = 10.5 for 5% margin for long
# eg. 10 - (10*0.05) = 9.5 for 5% margin for short
take_profit_margin = 0.1  # percentage margin

# Max Spent Equity: total equity to spend in a single operation
max_spent_equity = 10000  # $

# MAX ATTEMPTS SECTION
check_position_max_attempts = 5
cancel_pending_order_max_attempts = 5
get_shares_amount_max_attempts = 5
get_general_trend_max_attempts = 5
get_instant_trend_max_attempts = 10
get_rsi_max_attempts = 5
get_stochastic_max_attempts = 5
enter_position_mode_max_attempts = 120

# LIMIT PRICE
max_var = 0.01 # max variation percentage when buying/selling
