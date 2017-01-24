from blackjack import *
import time
# testing blackjack

######
# TODO
######
# Handle splits
# Implement double
# Insurance, half bet, 2:1, available when dealer's up card is ace
# Wrapper function to set up a game, interact with player(s)
# Automated playing with varied strategies
#   Inherit from Player class
#   fill table with non-human players, random strategy
# Logging, statistic collection
# Tip/side-bet bonus

# Issues
#   Blackjack appears to pay when dealer also has 21
#   Player busts not updated, handled in Hand class


def dev_table(numplayers = 3, default_balance=100, add_human=False):
    table = Table()
    try:
        player_count = max(table.players)
    except ValueError: # max() arg is an empty sequence
        player_count = 0
    total_players = player_count + numplayers
    for player in range(player_count+1,total_players+1):
        table.add_player(Player(player))
        table.players[player].add_balance(default_balance)
    if add_human:
        add_human(table, balance=10)
    return table

def add_human(table, balance):
    num_players = len(table.players)
    pid = len(table.players)+1
    table.add_player(Player(pid, human=True))
    table.players[pid].add_balance(balance)

def dev_play(table, rounds=1000, shuffle_every=False, debug=False):
    for rnd in range(rounds):
        for player in table.players:
            table.players[player].bet(10)
        deal_round(table, debug=debug)
        player_logic(table,debug=debug)
        dealer_logic(table,debug=debug)
        score_round(table, debug=debug)
        if debug:
            for player in table.players:
                print('Player %s: %s'% (player, table.players[player]))
            print('Dealer: %s' % table.dealer)
            print('######## END HAND ########\n')
        reset_round(table)
        if shuffle_every:
            table.shoe.shuffle()
    profit = 0
    for p in table.players: # TODO: is this accurate?
        profit -= (table.players[p].balance)
    print('House Profit: %s' % (profit))
    print('Your balance: %s' % (table.players[max(table.players)].balance))
    return profit # for (TODO) statistical work

def deal_round(table, debug=False):
    for card in range(2):
        table.deal_players(debug=debug)
        table.deal_dealer(debug=debug)

def score_round(table, debug=False):
    for player in table.players:
        if debug:
            bal_before = table.players[player].balance
            print('Player %s balance before payout: %s' % (player, bal_before))
        table.determine_winner(player)
        if debug:
            bal_after = table.players[player].balance
            print('Player %s balance after payout: %s\n' % (player, bal_after))

def reset_round(table):
    table.dealer.hand.reset()
    for player in table.players:
        table.players[player].hand.reset()
        table.players[player].hand.reset_bet()

def dealer_logic(table, debug=False):
    dealer = table.dealer
    player_scores = []
    for p in table.players:
        player_scores.append(table.players[p].hand.score)
    if debug:
        print('Player scores: %s' % player_scores)
        print('Dealer score: %s' % dealer.hand.score)
    while dealer.hand.score < max(player_scores):
        if dealer.hand.score <= 16:
            if debug:
                print('Dealer hits')
            dealer.take_card(table.shoe.deal_card())
            if debug:
                print('New Dealer score: %s' % dealer.hand.score)
        else:
            if debug:
                print('Dealer score: %s %s' % (dealer.hand.score, dealer.hand))
            if dealer.hand.score > 21:
                dealer.busts += 1
                print('Dealer busts!\n')
            else:
                print('Dealer stands\n')
                dealer.hand.standed()
            break

def player_logic(table, debug=False):
    for player_id in table.players:
        player = table.players[player_id]
        if player.human:
            human_input(table, player)
        else:
            if debug:
                print('Player %s score: %s %s' %(str(player_id), player.hand.score, player.hand))
            while player.hand.score <= 16:
                if debug:
                    print('Player %s hits' %str(player_id))
                player.take_card(table.shoe.deal_card())
                if debug:
                    print('New score: %s %s' %(player.hand.score, player.hand))
            if debug:
                if player.hand.score > 21:
                    print('Player %s busts\n' % player.id)
                else:
                    print('Player %s stands\n' % player.id)
            player.hand.standed()

def human_input(table, player):
    print('Player %s (human) hand %s, score %s' % (player.id, player.hand, player.hand.score))
    #while player.hand.stand == False:
    while not player.hand.stand:
        action = input('hit (h) or stand (s)? ')
        if action.lower() == 'h':
            player.take_card(table.shoe.deal_card())
            print('Hit %s, score now %s' % (table.shoe.dealt_card, player.hand.score))
            if player.hand.score > 21:
                print('Busted!\n')
        if action.lower() == 's':
            print('Player %s stands\n' %(player.id))
            player.hand.standed()

def run_profit(num_rounds = 1, hands=3, include_human=False, debug=False, default_balance=100):
    for i in range(num_rounds):
        table = dev_table()
        if include_human:
            add_human(table, default_balance)
        t1 = time.time()
        dev_play(table, hands, shuffle_every=True, debug=debug)
        t2 = time.time()
        print('%0.3f seconds' % (t2-t1))

#run_profit(include_human=True, debug=True)

run_profit(include_human=True, debug=True)
