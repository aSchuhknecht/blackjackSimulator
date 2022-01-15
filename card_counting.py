import config as cf
import sim_utils as ut


def main():
    run = True
    end = False
    ut.welcome_msg()
    deck = ut.gen_cards()

    while run:
        while True:
            if cf.mode == 'man' or cf.mode == 'test':
                print(f"Bankroll: {cf.bankroll}")
            cf.winnings_history.append(cf.bankroll)

            if cf.mode == 'man':
                cf.bet_size[0] = int(input('What is your bet?: '))
            else:
                cf.bet_size[0] = ut.adjust_bet_size()  # based on true count
            for i in range(0, len(cf.bet_size)):
                cf.bet_size[i] = cf.bet_size[0]

            if cf.bet_size[0] > cf.bankroll:
                print(f'Most you can wager is {cf.bankroll}')
                print(f'Bet is now {cf.bankroll}')

            d_cards, p_cards, deck = ut.deal_cards(deck)
            bj = ut.handle_bj(p_cards[cf.hi], d_cards, False)
            if bj:
                cf.total_hands += 1
                break

            busted_list = []
            bj_list = []
            sur_list = []
            aces = False

            for i in range(0, cf.max_splits + 4):

                if i <= 2*cf.num_splits:
                    p_busted, end, sur, has_split, s_bj, aces = ut.player_turn(p_cards, d_cards, deck)

                    if not has_split:
                        busted_list.append(p_busted)
                        bj_list.append(s_bj)
                        sur_list.append(sur)
                    if aces:
                        break
                    if has_split:
                        continue
                    else:
                        cf.hi += 1
                    if sur:
                        cf.sess_losses += 1
                        cf.bankroll -= 0.5*cf.bet_size[cf.hi - 1]
                        continue
                    if end:
                        continue
                    if p_busted:
                        if cf.mode == 'man' or cf.mode == 'test':
                            print('You bust, dealer wins.\n')
                        cf.sess_losses += 1
                        cf.bankroll -= cf.bet_size[cf.hi - 1]
                        continue
            if end:
                break

            # check if dealer busted
            d_busted = False
            for i in range(0, len(p_cards)):
                if not aces:
                    if busted_list[i] or bj_list[i] or sur_list[i]:
                        continue  # you lose even if dealer busts
                d_busted = ut.dealer_turn(d_cards, p_cards[cf.hi - 1], deck)
                if d_busted:
                    if cf.mode == 'man' or cf.mode == 'test':
                        print('Dealer busts!\n')
                    cf.sess_wins += 1
                    cf.bankroll += cf.bet_size[i]

            # compare totals if neither busted
            for i in range(0, len(p_cards)):
                if aces:
                    ut.find_winner(p_cards[i], d_cards, i)
                    continue
                if not busted_list[i] and not bj_list[i] and not sur_list[i] and not d_busted:
                    ut.find_winner(p_cards[i], d_cards, i)

            # check stop conditions
            if cf.total_hands >= cf.sim_hands:
                run = False
                print('Stopping sim')
                break
            if cf.bankroll <= 0:
                run = False
                print('Ran out of money!')
                break
            else:
                ut.reset_globals()

        if end:
            break

    if len(cf.winnings_history) > 1:
        ut.print_stats()


if __name__ == "__main__":
    main()
