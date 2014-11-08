from blackjack import *
# testing blackjack

######
# TODO
######
# Unit test: edge cases, ensure cards are not lost, etc
# Handle splits
# Implement double
# Insurance, half bet, 2:1, available when dealer's up card is ace
# Wrapper function to set up a game, interact with player(s)
# Automated playing with varied strategies
#   Inherit from Player class
#   fill table with non-human players, random strategy
# Logging, statistic collection
# Cash in, ticket out
# Bookkeeping
# Tip/side-bet bonus

def dev_table(numplayers=3):
    table = Table()
    for i in range(1,numplayers+1):
        table.add_player(Player(i))
        table.players[i].add_balance(0)
    return table
        
def dev_play(table, rounds=1000, shuffle_every=False):
    for rnd in range(rounds):
        if shuffle_every:
            table.shoe.shuffle()
        for i in table.players:
            table.players[i].bet(10)
        deal_round(table)
        player_logic(table)
        dealer_logic(table)
        score_round(table)
        reset_round(table)
    for player in table.players:
        print table.players[player]
    profit = 0
    for p in table.players:
        profit -= (table.players[p].balance)
    print('House Profit: %s' % (profit))
    return profit

def deal_round(table):
    for card in range(2):
        table.deal_players()
        table.deal_dealer()

def score_round(table):
    for player in table.players:
##        print 'Dealer  : %s' % table.dealer.hand.score
##        print 'Player %s: %s' % (str(player),table.players[player].hand.score)
##        print 'Dealer hand: %s' % (str(table.dealer.hand))
##        print 'Player hand: %s' % (str(table.players[player].hand))
        table.determine_winner(player)

def reset_round(table):
    table.dealer.hand.reset()
    for player in table.players:
        table.players[player].hand.reset()
        table.players[player].hand.reset_bet()

def dealer_logic(table):
    dealer = table.dealer
    player_scores = []
    for p in table.players:
        player_scores.append(table.players[p].hand.score)
    while dealer.hand.score < max(player_scores):
        if dealer.hand.score <= 16:
            dealer.take_card(table.shoe.deal_card())
        else:
            break

def player_logic(table):
    for player_id in table.players:
        player = table.players[player_id]
        while player.hand.score <= 16:
            player.take_card(table.shoe.deal_card())
