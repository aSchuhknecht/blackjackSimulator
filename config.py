# deck vars
numDecks = 6
deck_penetration = 3/4
cut_card = round(numDecks * 52 * (1 - deck_penetration))  # point at which shoe is reshuffled

# statistics
sess_wins = 0
sess_losses = 0
sess_pushes = 0
total_hands = 0
winnings_history = []
hph = 100  # hands per hour estimate

# betting vars
initial = 0
bet_size = [0, 0, 0, 0]  # bet size for 4 possible split hands
bankroll = 0  # total amount of money
unit = 50  # minimum bet

# bet spread corresponding to true count of 0-,1,2,3,4,5
bet_spread = [unit, unit, 5*unit, 10*unit, 15*unit, 20*unit]
rc = 0  # running count
tc = 0  # true count

bj_payout = 3/2
doubled_down = [False, False, False, False]  # for each of 4 possible split hands

insurance_payout = 2
insurance_bet = 0
bought_insurance = False
handled_insurance = False

# splitting vars
num_splits = 0
hi = 0  # hand index (for splitting)
max_splits = 3

# rules
allow_sur = True
enable_count = True

sim_hands = 500000
mode = 'sim'
