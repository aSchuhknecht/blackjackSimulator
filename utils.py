import random
import config as cf
import strat as st
import matplotlib.pyplot as plt


def numeric(card):
    if card == 'A':
        return 11
    elif card == 'T' or card == 'J' or card == 'Q' or card == 'K':
        return 10
    else:
        return int(card)


def gen_cards():
    cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    shoe = []
    for i in range(0, 4 * cf.numDecks):
        shoe.extend(cards)
    random.shuffle(shoe)

    return shoe


def deal_cards(deck):
    if len(deck) < cf.cut_card:
        deck = gen_cards()  # reshuffle
        print('Reshuffling cards')

    # for testing
    # deck = ['T', '9', 'A', 'A', 'T', '8', '6', '8', '3', 'A', '2', '5', 'T', '4']

    d_cards = [deck.pop(0), deck.pop(0)]

    p_cards = [[deck.pop(0), deck.pop(0)]]
    return d_cards, p_cards, deck


def print_cards(d_cards, p_cards, show_hole):
    if show_hole:
        print(f'Dealer Cards: {d_cards}')
        print(f'Your cards: {p_cards}')
    else:
        print(f'Dealer Up-card: {d_cards[0]}')
        print(f'Your cards: {p_cards}')


def check_bj(cards):
    total = 0
    for i in range(0, len(cards)):
        total += numeric(cards[i])
    if total == 21 and len(cards) == 2:
        return True
    else:
        return False


def handle_bj(p_cards, d_cards, is_split):
    p_blackjack = check_bj(p_cards)
    d_blackjack = check_bj(d_cards)

    if p_blackjack and not d_blackjack:
        print_cards(d_cards, p_cards, True)
        print('Blackjack! You win\n')
        cf.sess_wins += 1
        if is_split:
            cf.bankroll += cf.bet_size[cf.hi]
        else:
            cf.bankroll += cf.bj_payout * cf.bet_size[cf.hi]
        return True
    elif d_blackjack and not p_blackjack:
        print_cards(d_cards, p_cards, True)
        print('Dealer has blackjack and wins.\n')
        cf.sess_losses += 1
        cf.bankroll -= cf.bet_size[cf.hi]
        return True
    elif p_blackjack and d_blackjack:
        print_cards(d_cards, p_cards, True)
        print('Push.\n')
        cf.sess_pushes += 1
        return True
    else:
        return False


# returns boolean for if busted (True = no)
def check_for_bust(cards):
    total = 0  # allows for four possible aces

    for i in range(0, len(cards)):
        total += numeric(cards[i])

    if 'A' in cards:
        run, total = handle_aces(cards)
        return run
    else:
        if total > 21:
            return False
        else:
            return True


# Possible combos: using all aces as 1's
# or using one of the aces as an 11 while the rest are 1's.
# Returns boolean for if busted and total that should be used
def handle_aces(cards):
    num_aces = cards.count('A')
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


def verify_split(cards):
    if len(cards[cf.hi]) == 2:
        if cards[cf.hi][0] == cards[cf.hi][1] and cf.num_splits <= cf.max_splits:
            return True
    return False


def handle_split(cards, deck):
    aces = False
    if not verify_split(cards):
        print("Cannot split here.")
        return cards, False, aces

    if cards[cf.hi][0] == cards[cf.hi][1] == 'A':
        aces = True
    # add another hand, hit
    # cf.hi is hand being split
    cards.append([0, 0])
    cards[cf.num_splits][0] = cards[cf.hi][1]
    cards[cf.hi][1] = deck.pop(0)
    cards[cf.num_splits][1] = deck.pop(0)

    return cards, True, aces


def find_winner(p_cards, d_cards, index):
    p_total = 0
    for i in range(0, len(p_cards)):
        p_total += numeric(p_cards[i])
    while p_total > 21:
        p_total -= 10  # must be using an ace as a 1
    d_total = 0
    for i in range(0, len(d_cards)):
        d_total += numeric(d_cards[i])
    while d_total > 21:
        d_total -= 10  # must be using an ace as a 1

    if cf.num_splits > 0:
        print(f'\nHand #{index + 1}:')
    print(f'Your total is {p_total}')
    print(f'Dealer total is {d_total}')

    if p_total > d_total:
        print('You win!')
        cf.sess_wins += 1
        cf.bankroll += cf.bet_size[index]
        return 'You'
    elif d_total > p_total:
        print('Dealer wins.')
        cf.sess_losses += 1
        cf.bankroll -= cf.bet_size[index]
        return 'Dealer'
    else:
        print('Push')
        cf.sess_pushes += 1
        return 'PUSH'


def random_choice():
    choices = ['h', 'd', 's', 'x', 'v']
    random.shuffle(choices)
    return choices.pop()


def bad_strategy(cards):

    total = 0
    for i in range(0, len(cards)):
        total += numeric(cards[i])

    if total >= 15:
        return 's'
    if 9 <= total <= 11:
        return 'd'
    else:
        return 'h'


def basic_strategy(p_cards, d_card):

    col = numeric(d_card) - 1
    total = 0
    for i in range(0, len(p_cards)):
        total += numeric(p_cards[i])
    while total > 21:
        total -= 10  # must be using an ace as a 1

    if len(p_cards) == 2 and p_cards[0] == p_cards[1] and cf.num_splits < cf.max_splits:
        # use split table
        row = 12 - numeric(p_cards[0])
        return st.split[row][col]
    elif len(p_cards) == 2 and 'A' in p_cards and cf.num_splits < cf.max_splits:
        # use soft table
        row = 21 - total
        return st.soft[row][col]
    # else use hard table
    row = 22 - total
    return st.hard[row][col]


def print_stats():
    total_hands = cf.total_hands
    pct_win = (cf.sess_wins / total_hands) * 100
    margin = cf.bankroll - cf.initial
    pct_gain = (margin / cf.initial) * 100
    ev_per_hand = pct_gain / total_hands
    winnings_per_hand = margin / total_hands

    print(f'\nTotal rounds played: {total_hands}')
    print(f'# of wins: {cf.sess_wins}')
    print(f'# of losses: {cf.sess_losses}')
    print(f'# of pushes: {cf.sess_pushes}')
    print(f'% of hands won: {"{:.2f}".format(pct_win)}')
    print(f'Money won/lost: {margin}')
    print(f'% money gain: {"{:.2f}".format(pct_gain)}')
    print(f'% EV/hand: {"{:.6f}".format(ev_per_hand)}')
    print(f'money/hand: {"{:.6f}".format(winnings_per_hand)}')


def plot_winnings():
    x = []
    baseline = []
    for i in range(0, cf.total_hands + 1):
        x.append(i)
        baseline.append(cf.initial)
    y = cf.winnings_history

    plt.plot(x, y, 'r--', x, baseline, 'k--')
    plt.show()


def player_turn(cards, d_cards, deck):
    run = True
    busted = False
    end = False
    sur = False
    has_split = False
    bj = False
    aces = False

    while run:

        if cf.num_splits > 0:
            print(f'Hand #{cf.hi + 1}:')
            if handle_bj(cards[cf.hi], d_cards, True):
                bj = True
                break
        print_cards(d_cards, cards[cf.hi], False)

        action = input('Action: ')
        # action = random_choice()
        # action = bad_strategy(cards[cf.hi])
        # action = 's'
        # action = basic_strategy(cards[cf.hi], d_cards[0])
        print(f'Action is {action}')

        action = action.lower()

        if action == 'd' and (cf.doubled_down[cf.hi] or len(cards[cf.hi]) > 2):
            print('Invalid DD, hitting.')
            action = 'h'

        # switch on action
        if action == 'h':
            cards[cf.hi].append(deck.pop(0))  # hit
            print(f'You draw a {cards[cf.hi][len(cards[cf.hi]) - 1]}')
            run = check_for_bust(cards[cf.hi])
            busted = not run  # if function returns False, a bust happened
        elif action == 's':
            run = False  # stand
        elif action == 'd':
            cf.bet_size[cf.hi] *= 2
            cf.doubled_down[cf.hi] = True
            cards[cf.hi].append(deck.pop(0))  # hit
            print(f'{cards[cf.hi][len(cards[cf.hi]) - 1]} is drawn')
            run = check_for_bust(cards[cf.hi])
            busted = not run  # if function returns False, a bust happened
        elif action == 'v':
            has_split = True
            cf.num_splits += 1
            cards, valid_split, aces = handle_split(cards, deck)
            if valid_split or aces:
                run = False
            else:
                cf.num_splits -= 1
                has_split = False
        elif action == 'x' and cf.allow_sur:
            if len(cards) <= 2:
                sur = True
            else:
                print("Invalid surrender, standing")
            run = False
        elif action == 'q':
            end = True
            run = False
        else:
            print('Not a valid input.')

        if cf.doubled_down[cf.hi]:
            run = False  # can only hit once

    return busted, end, sur, has_split, bj, aces


def dealer_turn(cards, p_cards, deck):
    print_cards(cards, p_cards, True)
    total = 0
    for i in range(0, len(cards)):
        total += numeric(cards[i])

    run = True
    while run:

        if total < 17:
            cards.append(deck.pop(0))  # hit
            total += numeric(cards[len(cards) - 1])
            print(f'Dealer draws a {cards[len(cards) - 1]}')
        else:
            if 'A' in cards:
                run, total = handle_aces(cards)
                if total > 16:
                    run = False
            else:
                run = False

    if total > 21:
        return True
    else:
        return False
