import random
import config as cf
import strat as st
import matplotlib.pyplot as plt
import numpy as np
import math


def welcome_msg():
    print('Welcome to Blackjack \n')
    mode = input('Play manually? (y/n): ')
    if mode.lower() == 'y':
        cf.mode = 'man'
        print('Guide:\nh = hit\ns = stand\nd = double\nv = split\nx = surrender\nq = quit\n')
    elif mode.lower() == 'n':
        cf.mode = 'sim'
        print('Entering simulation mode')
        # cf.sim_hands = int(input('Enter number of hands to be played: '))
    elif mode.lower() == 't':
        cf.mode = 'test'
        print('Entering testing mode.')
    else:
        print('Invalid input, entering sim mode')
    cf.bankroll = cf.initial = int(input("Enter buy-in amount: "))


# converts card to numeric value
def numeric(card):
    if card == 'A':
        return 11
    elif card == 'T' or card == 'J' or card == 'Q' or card == 'K':
        return 10
    else:
        return int(card)


# returns sum of cards
def get_total(cards):
    total = 0
    for i in range(0, len(cards)):
        total += numeric(cards[i])
    return total


# generate new deck of cards and shuffle
def gen_cards():
    cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    shoe = []
    for i in range(0, 4 * cf.numDecks):
        shoe.extend(cards)
    random.shuffle(shoe)

    # init counts
    cf.rc = 0
    cf.tc = 0

    return shoe


def deal_cards(deck):
    if len(deck) < cf.cut_card:
        deck = gen_cards()  # reshuffle

    # uncomment to test predetermined deck
    # deck = ['T', '9', '6', '5', 'T', 'T', '8', 'T', '6', 'A', '2', '5', 'T', '4']

    # dealer gets 2 cards
    c1 = deck.pop(0)
    c2 = deck.pop(0)
    d_cards = [c1, c2]
    adjust_counts(c1, deck)
    adjust_counts(c2, deck)

    # player gets 2 cards
    c1 = deck.pop(0)
    c2 = deck.pop(0)
    p_cards = [[c1, c2]]
    adjust_counts(c1, deck)
    adjust_counts(c2, deck)
    return d_cards, p_cards, deck


def reset_globals():
    cf.total_hands += 1
    cf.hi = 0
    cf.num_splits = 0
    cf.handled_insurance = False
    cf.insurance_bet = 0
    cf.bought_insurance = False
    for i in range(0, cf.num_splits + 1):
        if cf.doubled_down[i]:
            cf.bet_size[i] /= 2
            cf.doubled_down[i] = False


def adjust_counts(card, deck):

    if not cf.enable_count:
        cf.tc = 0
        return
    if numeric(card) <= 6:
        cf.rc += 1
    elif numeric(card) > 9:
        cf.rc -= 1

    num_decks = math.ceil(len(deck) / 52)
    cf.tc = math.floor(cf.rc / num_decks)


def print_cards(d_cards, p_cards, show_hole):
    # dealer hole-card is only shown after player acts
    if show_hole:
        print(f'Dealer Cards: {d_cards}')
        print(f'Your cards: {p_cards}')
    else:
        print(f'Dealer Up-card: {d_cards[0]}')
        print(f'Your cards: {p_cards}')


def check_bj(cards):
    if get_total(cards) == 21 and len(cards) == 2:
        return True
    else:
        return False


def ask_insurance():
    if cf.mode == 'man':
        ans = input('Would you like to buy insurance? (y/n): ')
    else:
        if cf.tc >= 3:
            cf.bought_insurance = True
            cf.insurance_bet = 0.5 * cf.bet_size[0]
            return True
        else:
            return False

    if ans.lower() == 'y':
        cf.bought_insurance = True
        cf.insurance_bet = 0.5 * cf.bet_size[0]
        return True
    else:
        return False


# checks to see if game is over due to blackjack
def handle_bj(p_cards, d_cards, is_split):
    p_blackjack = check_bj(p_cards)
    d_blackjack = check_bj(d_cards)
    ins = False

    if d_cards[0] == 'A':
        if cf.mode != 'sim':
            print_cards(d_cards, p_cards, False)
        ins = ask_insurance()

    if d_blackjack and ins and not cf.handled_insurance:
        if cf.mode != 'sim':
            print('You win insurance bet.')
        cf.bankroll += cf.insurance_bet
        cf.handled_insurance = True
    elif not d_blackjack and ins and not cf.handled_insurance:
        if cf.mode != 'sim':
            print('You lose insurance bet.')
        cf.bankroll -= cf.insurance_bet
        cf.handled_insurance = True

    if p_blackjack and not d_blackjack:
        if cf.mode == 'man' or cf.mode == 'test':
            print_cards(d_cards, p_cards, True)
            print('Blackjack! You win\n')
        cf.sess_wins += 1
        if is_split:
            cf.bankroll += cf.bet_size[cf.hi]  # can't get natural blackjack on split hands
        else:
            cf.bankroll += cf.bj_payout * cf.bet_size[cf.hi]
        return True
    elif d_blackjack and not p_blackjack:
        if cf.mode == 'man' or cf.mode == 'test':
            print_cards(d_cards, p_cards, True)
            print('Dealer has blackjack and wins.\n')
        cf.sess_losses += 1
        cf.bankroll -= cf.bet_size[cf.hi]
        return True
    elif p_blackjack and d_blackjack:
        if cf.mode == 'man' or cf.mode == 'test':
            print_cards(d_cards, p_cards, True)
            print('Push.\n')
        cf.sess_pushes += 1
        return True
    else:
        return False


# Possible combos: using all aces as 1's
# or using one of the aces as an 11 while the rest are 1's.
# Returns boolean for if busted and total that should be used
def handle_aces(cards):
    num_aces = cards.count('A')  # number of aces in hand
    hard_total = 0
    for i in range(0, len(cards)):
        if cards[i] != 'A':
            hard_total += numeric(cards[i])

    # try using one ace as 11
    new_total = hard_total + 11 + (num_aces - 1)
    if new_total > 21:
        new_total = hard_total + num_aces  # using all aces as 1s
        if new_total > 21:
            return False, new_total
        else:
            return True, new_total
    else:
        return True, new_total


# returns boolean for if busted (True = no bust, continue game)
def check_for_bust(cards):

    total = get_total(cards)
    if 'A' in cards:
        run, total = handle_aces(cards)  # need to do special check for aces
        return run
    else:
        if total > 21:
            return False
        else:
            return True


# check for a valid split
def verify_split(cards):
    if len(cards[cf.hi]) == 2:
        if numeric(cards[cf.hi][0]) == numeric(cards[cf.hi][1]) and cf.num_splits <= cf.max_splits:
            return True
    return False


def verify_double(cards):
    if cf.doubled_down[cf.hi] or len(cards[cf.hi]) > 2:
        return False
    else:
        return True


def handle_split(cards, deck):
    aces = False
    if not verify_split(cards):
        if cf.mode == 'man' or cf.mode == 'test':
            print("Cannot split here.")
        return cards, False, aces

    if cards[cf.hi][0] == cards[cf.hi][1] == 'A':
        aces = True

    # add new hand to player hand list
    cards.append([0, 0])
    cards[cf.num_splits][0] = cards[cf.hi][1]
    cards[cf.hi][1] = deck.pop(0)
    cards[cf.num_splits][1] = deck.pop(0)

    adjust_counts(cards[cf.hi][1], deck)
    adjust_counts(cards[cf.num_splits][1], deck)

    return cards, True, aces


# determines winner when neither player busts
def find_winner(p_cards, d_cards, index):

    p_total = get_total(p_cards)
    while p_total > 21:
        p_total -= 10  # must be using an ace as a 1

    d_total = get_total(d_cards)
    while d_total > 21:
        d_total -= 10  # must be using an ace as a 1

    if cf.mode == 'man' or cf.mode == 'test':
        print(f'Your total is {p_total}')
        print(f'Dealer total is {d_total}')

    if p_total > d_total:
        if cf.mode == 'man' or cf.mode == 'test':
            print('You win!\n')
        cf.sess_wins += 1
        cf.bankroll += cf.bet_size[index]
    elif d_total > p_total:
        if cf.mode == 'man' or cf.mode == 'test':
            print('Dealer wins.\n')
        cf.sess_losses += 1
        cf.bankroll -= cf.bet_size[index]
    else:
        if cf.mode == 'man' or cf.mode == 'test':
            print('Push\n')
        cf.sess_pushes += 1


def random_choice():
    choices = ['h', 'd', 's', 'x', 'v']
    random.shuffle(choices)
    return choices.pop()


# returns correct action based on basic strategy along with table used
def basic_strategy(p_cards, d_card):

    col = numeric(d_card) - 1
    total = get_total(p_cards)
    while total > 21:
        total -= 10  # must be using an ace as a 1

    hard_total = 0
    for i in range(0, len(p_cards)):
        if p_cards[i] != 'A':
            hard_total += numeric(p_cards[i])

    if len(p_cards) == 2 and numeric(p_cards[0]) == numeric(p_cards[1]) and cf.num_splits < cf.max_splits:
        # use split table
        row = 12 - numeric(p_cards[0])
        return st.split[row][col], 'split'
    elif hard_total <= 9 and 'A' in p_cards and cf.num_splits < cf.max_splits:
        # use soft table
        row = 10 - hard_total
        return st.soft[row][col], 'soft'
    # else use hard table
    row = 22 - total
    return st.hard[row][col], 'hard'


# adjust bet size based on true count
def adjust_bet_size():

    if cf.tc <= -2:
        return 0
    if cf.tc <= 0:
        return cf.bet_spread[0]  # TC <= 0
    elif 1 <= cf.tc <= 5:
        return cf.bet_spread[cf.tc]
    else:
        return cf.bet_spread[5]  # TC > 5


def print_stats():

    margin = cf.bankroll - cf.initial
    pct_gain = (margin / cf.initial) * 100
    ev_per_hand = pct_gain / cf.total_hands
    winnings_per_hand = margin / cf.total_hands
    winnings_per_hour = winnings_per_hand * cf.hph

    print(f'\nTotal rounds played: {cf.total_hands}')
    print(f'# of wins: {cf.sess_wins}')
    print(f'# of losses: {cf.sess_losses}')
    print(f'# of pushes: {cf.sess_pushes}')
    print(f'% of hands won: {"{:.2f}".format((cf.sess_wins / cf.total_hands) * 100)}')
    print(f'Money won/lost: {cf.bankroll - cf.initial}')
    print(f'% money gain: {"{:.2f}".format(pct_gain)}')
    print(f'% EV/hand: {"{:.6f}".format(ev_per_hand)}')
    print(f'$/hand: ${"{:.2f}".format(winnings_per_hand)}')
    print(f'$/hr: ${"{:.2f}".format(winnings_per_hour)}')
    plot_winnings()


def plot_winnings():

    x = np.linspace(0, len(cf.winnings_history), len(cf.winnings_history))
    baseline = np.full((len(cf.winnings_history), ), cf.initial)
    y = np.array(cf.winnings_history)
    m = np.polyfit(x, y, 1)
    best_fit = m[0]*x + m[1]

    plt.plot(x, y, 'r--', x, baseline, 'k--', x, best_fit, 'b--')
    plt.title("Winnings over time")
    plt.xlabel("Hands")
    plt.ylabel("Total Money")
    plt.show()


def hit(cards, deck, double):
    c1 = deck.pop(0)
    cards.append(c1)  # hit
    adjust_counts(c1, deck)
    run = check_for_bust(cards)
    busted = not run
    if double:
        run = False  # can only get one card after doubling
    if cf.mode == 'man' or cf.mode == 'test':
        print(f'{c1} is drawn')
    return cards, busted, run


def player_turn(cards, d_cards, deck):

    # flags
    run = True
    busted = False
    end = False
    sur = False
    has_split = False
    bj = False
    aces = False

    while run:
        if cf.num_splits > 0 and (cf.mode == 'man' or cf.mode == 'test'):
            print(f'Hand #{cf.hi + 1}:')
        if handle_bj(cards[cf.hi], d_cards, True):
            bj = True
            break

        if cf.mode == 'man':
            print_cards(d_cards[0], cards[cf.hi], False)
            action = input('Action: ')
        else:
            action, table = basic_strategy(cards[cf.hi], d_cards[0])
            # print(f'Action is {action}')
            if cf.mode == 'test':
                print_cards(d_cards[0], cards[cf.hi], False)
                print(f'Action is {action} from {table} table')
        action = action.lower()

        # switch on action
        if action == 'h':
            cards[cf.hi], busted, run = hit(cards[cf.hi], deck, False)
        elif action == 's':
            run = False  # stand
        elif action == 'd':
            if verify_double(cards):
                cf.bet_size[cf.hi] *= 2
                cf.doubled_down[cf.hi] = True
                cards[cf.hi], busted, run = hit(cards[cf.hi], deck, True)
            else:
                if cf.mode == 'man' or cf.mode == 'test':
                    print("Invalid double, hitting instead")
                cards[cf.hi], busted, run = hit(cards[cf.hi], deck, False)  # just hit
        elif action == 'v':
            if verify_split(cards) or aces:
                has_split = True
                cf.num_splits += 1
                cards, valid_split, aces = handle_split(cards, deck)
                run = False
            else:
                if cf.mode == 'man' or cf.mode == 'test':
                    print("Invalid split")
        elif action == 'x':
            if len(cards[cf.hi]) <= 2 and cf.allow_sur:
                sur = True
                run = False
            else:
                if cf.mode == 'man' or cf.mode == 'test':
                    print("Invalid surrender")
                cards[cf.hi], busted, run = hit(cards[cf.hi], deck, False)  # just hit
        elif action == 'q':
            end = True
            run = False
        else:
            if cf.mode == 'man' or cf.mode == 'test':
                print('Not a valid input.')
    return busted, end, sur, has_split, bj, aces


def dealer_turn(cards, p_cards, deck):

    if cf.mode == 'man' or cf.mode == 'test':
        print_cards(cards, p_cards, deck)
    total = get_total(cards)
    run = True
    while run:

        # hit
        if total < 17:
            c1 = deck.pop(0)
            cards.append(c1)
            adjust_counts(c1, deck)
            total += numeric(cards[len(cards) - 1])
            if cf.mode == 'man' or cf.mode == 'test':
                print(f'Dealer draws a {cards[len(cards) - 1]}')
        else:
            if 'A' in cards:
                run, total = handle_aces(cards)  # special check to check hand with aces
                if total > 16:
                    run = False
            else:
                run = False

    # check if busted
    if total > 21:
        return True
    else:
        return False
