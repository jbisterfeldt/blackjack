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


def dev_table(numplayers = 3, balance = 0):
    table = Table()
    try:
        player_count = max(table.players)
    except ValueError: # max() arg is an empty sequence
        player_count = 0
    total_players = player_count + numplayers
    for i in range(player_count+1,total_players+1):
        table.add_player(Player(i))
        table.players[i].add_balance(balance)
    #add_human(table, balance)
    return table

def add_human(table, balance):
    num_players = len(table.players)
    pid = len(table.players)+1
    table.add_player(Player(pid, human=True))
    table.players[pid].add_balance(balance)

def dev_play(table, rounds=1000, shuffle_every=False, debug=True):
    for rnd in range(rounds):
        for i in table.players:
            table.players[i].bet(10)
        deal_round(table)
        player_logic(table,debug=debug)
        dealer_logic(table,debug=debug)
        score_round(table, debug=debug)
        if debug:
            print('Dealer: %s' % table.dealer)
            for player in table.players:
                print('Player %s: %s'% (player, table.players[player]))
            print('######## END HAND ########\n')
        reset_round(table)
        if shuffle_every:
            table.shoe.shuffle()
    profit = 0
    for p in table.players:
        profit -= (table.players[p].balance)
    print('House Profit: %s' % (profit))
    return profit # for (TODO) statistical work

def deal_round(table):
    for card in range(2):
        table.deal_players()
        table.deal_dealer()

def score_round(table, debug=False):
    for player in table.players:
        if debug:
            bal_before = table.players[player].balance
            print('Player %s balance before payout: %s' % (player, bal_before))
        table.determine_winner(player)
        if debug:
            bal_after = table.players[player].balance
            print('Player %s balance: %s' % (player, bal_after))

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
    #print('Player scores: %s' % player_scores)
    #print('Dealer score: %s' % dealer.hand.score)
    while dealer.hand.score < max(player_scores):
        if dealer.hand.score <= 16:
            #print('Dealer hitting')
            dealer.take_card(table.shoe.deal_card())
            #print('New Dealer score: %s' % dealer.hand.score)
        else:
            if debug:
                print('Dealer standing\n')
            dealer.hand.standed()
            break

def player_logic(table, debug=False):
    for player_id in table.players:
        player = table.players[player_id]
        if player.human:
            human_input(table, player)
        else:
            if debug:
                print('Player %s score: %s' %(str(player_id),player.hand.score))
            while player.hand.score <= 16:
                if debug:
                    print('Player %s hits' %str(player_id))
                player.take_card(table.shoe.deal_card())
                if debug:
                    print('New score: %s' %player.hand.score)
            if debug:
                print('Player %s standing\n' % player.id)
            player.hand.standed()

def human_input(table, player):
    print('Your hand %s, score %s' % (player.hand, player.hand.score))
    #while player.hand.stand == False:
    while not player.hand.stand:
        action = raw_input('hit (h) or stand (s)? ')
        if action.lower() == 'h':
            player.take_card(table.shoe.deal_card())
            print('Hit %s, score now %s' % (table.shoe.dealt_card, player.hand.score))
            if player.hand.score > 21:
                print('Busted!')
        if action.lower() == 's':
            player.hand.standed()

def run_profit(num_rounds = 1, hands=3):
    for i in range(num_rounds):
        table = dev_table()
        t1 = time.time()
        dev_play(table, hands, shuffle_every=True, debug=True)
        t2 = time.time()
        print('%0.3f seconds' % (t2-t1))

run_profit()
